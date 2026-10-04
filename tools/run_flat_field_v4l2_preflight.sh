#!/bin/sh

set -eu

TOKEN=--run-flat-field-v4l2-preflight
FRAME_BYTES=1228800
YUYV_FRAME_BYTES=2457600
FRAMES=6
VIDEO_NUMBER=${TCA_PREFLIGHT_VIDEO_NUMBER:-43}
DEVICE=/dev/video${VIDEO_NUMBER}
LOADED=0
WRITER_PID=0

usage() {
    echo "usage: sudo $0 $TOKEN [OUTPUT_DIRECTORY]" >&2
    echo "       runs a synthetic filter-to-V4L2 check; sends no USB transfer" >&2
}

if [ "$#" -eq 0 ]; then
    usage
    echo "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." >&2
    exit 0
fi
if [ "$#" -gt 2 ] || [ "$1" != "$TOKEN" ]; then
    usage
    echo "NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE." >&2
    exit 64
fi
if [ "$(uname -s)" != Linux ] || [ "$(id -u)" -ne 0 ]; then
    echo "this preflight requires Linux root for temporary v4l2loopback" >&2
    exit 69
fi

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
flat_tool=$project_dir/build/tca-flat-field
for command in dd ffmpeg grep mktemp od sha256sum stat tr v4l2-ctl; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "missing command: $command" >&2
        exit 69
    fi
done
if [ ! -x "$flat_tool" ]; then
    echo "missing $flat_tool; run make first" >&2
    exit 69
fi
if [ ! -x /usr/sbin/modprobe ]; then
    echo "missing /usr/sbin/modprobe" >&2
    exit 69
fi
if grep -q '^v4l2loopback ' /proc/modules 2>/dev/null || [ -e "$DEVICE" ]; then
    echo "refusing to alter an existing loopback setup or device: $DEVICE" >&2
    exit 73
fi

if [ "$#" -eq 2 ]; then
    output_dir=$2
    if [ -e "$output_dir" ]; then
        echo "output directory already exists: $output_dir" >&2
        exit 73
    fi
    mkdir -m 0755 "$output_dir"
else
    output_dir=$(mktemp -d "${TMPDIR:-/tmp}/tca-flat-v4l2.XXXXXX")
fi

cleanup() {
    if [ "$WRITER_PID" -ne 0 ]; then
        kill "$WRITER_PID" 2>/dev/null || true
        wait "$WRITER_PID" 2>/dev/null || true
    fi
    if [ "$LOADED" -eq 1 ]; then
        /usr/sbin/modprobe -r v4l2loopback || true
    fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

dd if=/dev/zero bs=$FRAME_BYTES count=2 status=none \
    | tr '\000' '\012' > "$output_dir/darks.bayer"
dd if=/dev/zero bs=$FRAME_BYTES count=2 status=none \
    | tr '\000' '\156' > "$output_dir/flats.bayer"
dd if=/dev/zero bs=$FRAME_BYTES count=$FRAMES status=none \
    | tr '\000' '\074' > "$output_dir/input-six.bayer"

"$flat_tool" calibrate --mode 2 --phase grbg \
    --dark "$output_dir/darks.bayer" --dark-frames 2 \
    --flat "$output_dir/flats.bayer" --flat-frames 2 \
    --output "$output_dir/uniform.tca-flat" \
    2> "$output_dir/calibrate.stderr.txt"
"$flat_tool" inspect --calibration "$output_dir/uniform.tca-flat" \
    > "$output_dir/calibration.json"
"$flat_tool" apply --calibration "$output_dir/uniform.tca-flat" \
    --input "$output_dir/input-six.bayer" \
    --output "$output_dir/corrected-six.bayer" \
    2> "$output_dir/apply.stderr.txt"

corrected_bytes=$(stat -c %s "$output_dir/corrected-six.bayer")
expected_corrected_bytes=$((FRAME_BYTES * FRAMES))
if [ "$corrected_bytes" -ne "$expected_corrected_bytes" ]; then
    echo "corrected stream size mismatch: $corrected_bytes" >&2
    exit 1
fi
first_value=$(od -An -tu1 -N1 "$output_dir/corrected-six.bayer" | tr -d ' ')
if [ "$first_value" != 50 ]; then
    echo "dark subtraction/gain result mismatch: $first_value" >&2
    exit 1
fi

/usr/sbin/modprobe v4l2loopback video_nr="$VIDEO_NUMBER" \
    card_label="TCA Flat Field Preflight" exclusive_caps=1 max_buffers=4
LOADED=1
owner_uid=${SUDO_UID:-0}
owner_gid=${SUDO_GID:-0}
chown "$owner_uid:$owner_gid" "$DEVICE"

ffmpeg -hide_banner -loglevel error -re \
    -f rawvideo -pixel_format bayer_grbg8 -video_size 1280x960 -framerate 2 \
    -i "$output_dir/corrected-six.bayer" -frames:v "$FRAMES" \
    -vf format=yuyv422 -f v4l2 "$DEVICE" \
    > "$output_dir/writer.stdout.txt" 2> "$output_dir/writer.stderr.txt" &
WRITER_PID=$!

attempt=0
while [ "$attempt" -lt 50 ]; do
    if v4l2-ctl -d "$DEVICE" --all \
        > "$output_dir/device.txt" 2>/dev/null &&
       grep -q "Pixel Format.*'YUYV'" "$output_dir/device.txt"; then
        break
    fi
    if ! kill -0 "$WRITER_PID" 2>/dev/null; then
        echo "V4L2 writer exited before format negotiation" >&2
        exit 1
    fi
    sleep 0.1
    attempt=$((attempt + 1))
done
if [ "$attempt" -ge 50 ]; then
    echo "V4L2 writer did not become ready" >&2
    exit 1
fi

v4l2-ctl -d "$DEVICE" --stream-mmap=3 --stream-count="$FRAMES" \
    --stream-to="$output_dir/six-frames.yuyv" \
    > "$output_dir/consumer.stdout.txt" 2> "$output_dir/consumer.stderr.txt"
wait "$WRITER_PID"
WRITER_PID=0

yuyv_bytes=$(stat -c %s "$output_dir/six-frames.yuyv")
expected_yuyv_bytes=$((YUYV_FRAME_BYTES * FRAMES))
if [ "$yuyv_bytes" -ne "$expected_yuyv_bytes" ]; then
    echo "V4L2 consumer size mismatch: $yuyv_bytes" >&2
    exit 1
fi

(
    cd "$output_dir"
    sha256sum apply.stderr.txt calibrate.stderr.txt calibration.json \
        corrected-six.bayer device.txt six-frames.yuyv writer.stderr.txt \
        > manifest.sha256
)
echo "output=$output_dir corrected_frames=$FRAMES v4l2_frames=$FRAMES status=ok"
