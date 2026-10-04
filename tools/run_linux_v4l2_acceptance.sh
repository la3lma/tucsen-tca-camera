#!/bin/sh
# Corrected live-camera Linux/V4L2 acceptance. Inert without the exact token.

set -eu
LC_ALL=C
export LC_ALL

TOKEN=--run-live-linux-v4l2-acceptance
DEFAULT_VIDEO_NUMBER=42
DEFAULT_EXPOSURE_MS=250
DEFAULT_GAIN=0
DEFAULT_FRAMES=60
MODE2_RAW_BYTES=1229312
MODE2_FRAME_BYTES=1228800
YUYV_FRAME_BYTES=2457600

usage()
{
    printf 'usage: %s %s RELEASE_ROOT CALIBRATION EVIDENCE_PARENT [VIDEO_NUMBER [EXPOSURE_MS [GAIN [FRAMES]]]]\n' \
        "$0" "$TOKEN"
}

camera_count()
{
    count=0
    for candidate in /sys/bus/usb/devices/*; do
        [ -f "$candidate/idVendor" ] || continue
        [ -f "$candidate/idProduct" ] || continue
        vendor=$(tr '[:upper:]' '[:lower:]' <"$candidate/idVendor")
        product=$(tr '[:upper:]' '[:lower:]' <"$candidate/idProduct")
        [ "$vendor:$product" = 0547:c003 ] && count=$((count + 1))
    done
    printf '%s\n' "$count"
}

file_bytes()
{
    wc -c <"$1" | tr -d '[:space:]'
}

is_decimal()
{
    case "$1" in
        ''|*[!0-9]*) return 1 ;;
        *) return 0 ;;
    esac
}

if [ "$#" -eq 0 ]; then
    printf 'harness=dry-run target=0547:c003 transfer=none\n'
    usage
    printf 'NO USB TRANSFER SENT.\n'
    exit 0
fi

if [ "$#" -lt 4 ] || [ "$#" -gt 8 ] || [ "$1" != "$TOKEN" ]; then
    usage >&2
    printf 'NO USB TRANSFER SENT.\n' >&2
    exit 64
fi

release_root=$2
calibration=$3
evidence_parent=$4
video_number=${5:-$DEFAULT_VIDEO_NUMBER}
exposure_ms=${6:-$DEFAULT_EXPOSURE_MS}
gain=${7:-$DEFAULT_GAIN}
frames=${8:-$DEFAULT_FRAMES}
device=/dev/video$video_number

for value in "$video_number" "$exposure_ms" "$gain" "$frames"; do
    is_decimal "$value" || {
        printf 'video number, exposure, gain, and frames must be decimal integers\n' >&2
        exit 64
    }
done
if [ "$exposure_ms" -lt 1 ] || [ "$exposure_ms" -gt 480 ] ||
   [ "$gain" -gt 320 ] || [ "$frames" -lt 2 ] || [ "$frames" -gt 600 ]; then
    printf 'ranges: EXPOSURE_MS=1..480 GAIN=0..320 FRAMES=2..600\n' >&2
    exit 64
fi
if [ "$(uname -s)" != Linux ]; then
    printf 'this live acceptance harness requires Linux\n' >&2
    exit 69
fi

reader=$release_root/build/tca-camera
analyzer=$release_root/scripts/tca-frame-stats
timing_analyzer=$release_root/scripts/tca-timing-stats
bridge=$release_root/scripts/tca-v4l2
flat_field_tool=$release_root/build/tca-flat-field

git -C "$release_root" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    printf 'release root is not a Git worktree: %s\n' "$release_root" >&2
    exit 66
}
if [ -n "$(git -C "$release_root" status --porcelain)" ]; then
    printf 'release worktree must be clean: %s\n' "$release_root" >&2
    exit 73
fi
release_commit=$(git -C "$release_root" rev-parse HEAD)
for executable in "$reader" "$analyzer" "$timing_analyzer" "$bridge" \
                  "$flat_field_tool"; do
    [ -x "$executable" ] || {
        printf 'missing executable: %s\n' "$executable" >&2
        exit 69
    }
done
[ -r "$calibration" ] || {
    printf 'calibration is not readable: %s\n' "$calibration" >&2
    exit 66
}
[ -d "$evidence_parent" ] || {
    printf 'evidence parent must already exist: %s\n' "$evidence_parent" >&2
    exit 66
}

for command_name in awk cut date dd ffmpeg find git grep lsusb mkdir \
                    sha256sum sort tr v4l2-ctl wc xargs; do
    command -v "$command_name" >/dev/null 2>&1 || {
        printf 'missing required command: %s\n' "$command_name" >&2
        exit 69
    }
done
[ -x /usr/bin/time ] || {
    printf 'missing required command: /usr/bin/time\n' >&2
    exit 69
}
[ "$(camera_count)" -eq 1 ] || {
    printf 'expected exactly one 0547:c003 camera\n' >&2
    exit 69
}
[ ! -e "$device" ] || {
    printf 'refusing existing %s\n' "$device" >&2
    exit 73
}
if grep -q '^v4l2loopback ' /proc/modules 2>/dev/null; then
    printf 'refusing an already-loaded v4l2loopback module\n' >&2
    exit 73
fi
sudo -n true >/dev/null 2>&1 || {
    printf 'prime sudo credentials in this shell before running the harness\n' >&2
    exit 77
}

run_id=$(date -u '+%Y%m%dT%H%M%SZ')-$$
run_dir=$evidence_parent/linux-v4l2-acceptance-$run_id
[ ! -e "$run_dir" ] || {
    printf 'evidence directory already exists: %s\n' "$run_dir" >&2
    exit 73
}
mkdir -p "$run_dir"
bridge_pid=0

finalize()
{
    if [ "$bridge_pid" -ne 0 ]; then
        kill -TERM "$bridge_pid" 2>/dev/null || true
        wait "$bridge_pid" 2>/dev/null || true
        bridge_pid=0
    fi
    if [ -d "$run_dir" ]; then
        (
            cd "$run_dir"
            find . -type f ! -name manifest.sha256 -print0 | sort -z | \
                xargs -0 sha256sum >manifest.sha256
        )
    fi
}
trap finalize EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

{
    printf 'profile=tca-linux-v4l2-acceptance-v1\n'
    printf 'target=0547:c003\n'
    printf 'release_commit=%s\n' "$release_commit"
    printf 'calibration=%s\n' "$calibration"
    printf 'video_device=%s\n' "$device"
    printf 'exposure_ms=%s\n' "$exposure_ms"
    printf 'gain=%s\n' "$gain"
    printf 'consumer_frames=%s\n' "$frames"
} >"$run_dir/session.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' >"$run_dir/start-utc.txt"
uname -a >"$run_dir/uname.txt"
lsusb >"$run_dir/lsusb.txt"
lsusb -t >"$run_dir/lsusb-tree.txt"
git -C "$release_root" status --short >"$run_dir/release-status.txt"
"$flat_field_tool" inspect --calibration "$calibration" \
    >"$run_dir/calibration.json"
sha256sum "$reader" "$analyzer" "$timing_analyzer" "$bridge" \
    "$flat_field_tool" "$calibration" "$0" >"$run_dir/pinned-inputs.sha256"

timestamps=$run_dir/reader-timestamps.csv
TCA_FLAT_FIELD="$calibration" TCA_TIMESTAMPS="$timestamps" \
    "$bridge" --serve "$run_dir/bridge-first-device.raw" "$video_number" \
    "$exposure_ms" "$gain" >"$run_dir/bridge.stdout.txt" \
    2>"$run_dir/bridge.stderr.txt" &
bridge_pid=$!

attempt=0
while [ "$attempt" -lt 100 ]; do
    if v4l2-ctl -d "$device" --all >"$run_dir/v4l2-device.txt" \
        2>/dev/null && grep -q 'Video Capture' "$run_dir/v4l2-device.txt"; then
        break
    fi
    kill -0 "$bridge_pid" 2>/dev/null || {
        printf 'V4L2 bridge exited before readiness\n' >&2
        exit 1
    }
    sleep 0.1
    attempt=$((attempt + 1))
done
[ "$attempt" -lt 100 ] || {
    printf 'timed out waiting for %s\n' "$device" >&2
    exit 1
}

consumer_bytes=$((frames * YUYV_FRAME_BYTES))
/usr/bin/time -p ffmpeg -hide_banner -loglevel warning \
    -f v4l2 -input_format yuyv422 -video_size 1280x960 \
    -i "$device" -frames:v "$frames" -pix_fmt yuyv422 -f rawvideo \
    "$run_dir/consumer.yuyv" >"$run_dir/consumer.stdout.txt" \
    2>"$run_dir/consumer.stderr-and-time.txt"
[ "$(file_bytes "$run_dir/consumer.yuyv")" -eq "$consumer_bytes" ]

ffmpeg -hide_banner -loglevel error -f rawvideo -pixel_format yuyv422 \
    -video_size 1280x960 -i "$run_dir/consumer.yuyv" \
    -frames:v "$frames" -f framemd5 "$run_dir/consumer.framemd5"
dd if="$run_dir/consumer.yuyv" of="$run_dir/consumer-first-frame.yuyv" \
    bs="$YUYV_FRAME_BYTES" count=1 status=none
ffmpeg -hide_banner -loglevel error -f rawvideo -pixel_format yuyv422 \
    -video_size 1280x960 -i "$run_dir/consumer-first-frame.yuyv" \
    -frames:v 1 "$run_dir/consumer-first-frame.png"

kill -TERM "$bridge_pid"
set +e
wait "$bridge_pid"
bridge_status=$?
set -e
bridge_pid=0
printf '%s\n' "$bridge_status" >"$run_dir/bridge-exit-status.txt"
[ "$bridge_status" -eq 143 ] || [ "$bridge_status" -eq 0 ]
[ ! -e "$device" ]
if grep -q '^v4l2loopback ' /proc/modules 2>/dev/null; then
    printf 'v4l2loopback remained loaded after bridge cleanup\n' >&2
    exit 1
fi

"$timing_analyzer" "$timestamps" --json "$run_dir/reader-timing.json"
producer_frames=$(grep -c '^[0-9][0-9]*,' "$timestamps")
[ "$producer_frames" -ge "$frames" ] || {
    printf 'producer sidecar has fewer frames than the consumer: %s < %s\n' \
        "$producer_frames" "$frames" >&2
    exit 1
}
pipeline_delta=$((producer_frames - frames))
consumer_seconds=$(awk '$1 == "real" { value=$2 } END { print value }' \
    "$run_dir/consumer.stderr-and-time.txt")
consumer_fps=$(awk -v count="$frames" -v seconds="$consumer_seconds" \
    'BEGIN { if (seconds <= 0) exit 1; printf "%.6f", count / seconds }')
digest_frames=$(grep -c '^[0-9]' "$run_dir/consumer.framemd5")
[ "$digest_frames" -eq "$frames" ]
distinct_digests=$(grep '^[0-9]' "$run_dir/consumer.framemd5" | \
    cut -d, -f6 | sort -u | wc -l | tr -d '[:space:]')
{
    printf 'consumer_frames=%s\n' "$frames"
    printf 'consumer_bytes=%s\n' "$consumer_bytes"
    printf 'consumer_elapsed_seconds=%s\n' "$consumer_seconds"
    printf 'consumer_fps=%s\n' "$consumer_fps"
    printf 'consumer_digest_frames=%s\n' "$digest_frames"
    printf 'consumer_distinct_digests=%s\n' "$distinct_digests"
    printf 'producer_frames=%s\n' "$producer_frames"
    printf 'producer_minus_consumer=%s\n' "$pipeline_delta"
    printf 'interpretation=delta includes bounded in-flight pipeline frames and is not by itself a proven drop count\n'
} >"$run_dir/producer-consumer-summary.txt"

"$reader" capture --mode 2 --frames 1 \
    --raw-first "$run_dir/reopen-first-device.raw" \
    --bayer "$run_dir/reopen-one-frame.bayer" \
    --exposure-ms "$exposure_ms" --gain "$gain" \
    >"$run_dir/reopen.stdout.txt" 2>"$run_dir/reopen.stderr.txt"
[ "$(file_bytes "$run_dir/reopen-first-device.raw")" -eq "$MODE2_RAW_BYTES" ]
[ "$(file_bytes "$run_dir/reopen-one-frame.bayer")" -eq "$MODE2_FRAME_BYTES" ]
grep -Fx 'frames=1 status=ok' "$run_dir/reopen.stderr.txt" >/dev/null
"$analyzer" "$run_dir/reopen-one-frame.bayer" --mode 2 \
    --json "$run_dir/reopen-one-frame.stats.json"

date -u '+%Y-%m-%dT%H:%M:%SZ' >"$run_dir/end-utc.txt"
printf 'linux_v4l2_acceptance=PASS\n'
printf 'evidence_directory=%s\n' "$run_dir"
