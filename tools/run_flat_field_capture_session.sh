#!/bin/sh

set -eu

TOKEN=--run-flat-field-capture-session
FRAME_BYTES=1228800
DEVICE_BYTES=1229312

usage() {
    cat >&2 <<EOF
usage: $0 $TOKEN --output DIRECTORY [OPTIONS]

Guided, interactive capture of one preview-mode flat-field calibration and
fresh blank/specimen validation set. With no token, sends no USB transfer.

Options:
  --exposure-ms N          camera exposure, 1..480 (default: 250)
  --gain N                 normalized camera gain, 0..320 (default: 0)
  --phase PHASE            rggb, grbg, gbrg, or bggr (default: grbg)
  --dark-frames N          blocked-light frames, 1..64 (default: 16)
  --flat-batches N         separately positioned flat batches, 1..16 (default: 4)
  --flat-frames-per-batch N  frames per flat batch, 1..64 (default: 4)
EOF
}

no_transfer() {
    echo "NO USB TRANSFER SENT. NO FILE OR SYSTEM CHANGE MADE." >&2
}

if [ "$#" -eq 0 ]; then
    usage
    no_transfer
    exit 0
fi
if [ "$1" != "$TOKEN" ]; then
    usage
    no_transfer
    exit 64
fi
shift

output_dir=
exposure_ms=250
camera_gain=0
phase=grbg
dark_frames=16
flat_batches=4
flat_frames_per_batch=4

while [ "$#" -gt 0 ]; do
    case "$1" in
        --output)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            output_dir=$2
            shift 2
            ;;
        --exposure-ms)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            exposure_ms=$2
            shift 2
            ;;
        --gain)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            camera_gain=$2
            shift 2
            ;;
        --phase)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            phase=$2
            shift 2
            ;;
        --dark-frames)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            dark_frames=$2
            shift 2
            ;;
        --flat-batches)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            flat_batches=$2
            shift 2
            ;;
        --flat-frames-per-batch)
            [ "$#" -ge 2 ] || { usage; no_transfer; exit 64; }
            flat_frames_per_batch=$2
            shift 2
            ;;
        *)
            echo "unknown option: $1" >&2
            usage
            no_transfer
            exit 64
            ;;
    esac
done

is_uint() {
    case "$1" in
        0|[1-9]|[1-9][0-9]*) return 0 ;;
        *) return 1 ;;
    esac
}

require_range() {
    label=$1
    value=$2
    minimum=$3
    maximum=$4
    if ! is_uint "$value" || [ "$value" -lt "$minimum" ] ||
       [ "$value" -gt "$maximum" ]; then
        echo "$label must be an integer in $minimum..$maximum" >&2
        no_transfer
        exit 64
    fi
}

if [ -z "$output_dir" ]; then
    echo "--output is required" >&2
    no_transfer
    exit 64
fi
require_range --exposure-ms "$exposure_ms" 1 480
require_range --gain "$camera_gain" 0 320
require_range --dark-frames "$dark_frames" 1 64
require_range --flat-batches "$flat_batches" 1 16
require_range --flat-frames-per-batch "$flat_frames_per_batch" 1 64
case "$phase" in
    rggb|grbg|gbrg|bggr) ;;
    *)
        echo "--phase must be rggb, grbg, gbrg, or bggr" >&2
        no_transfer
        exit 64
        ;;
esac
if [ -e "$output_dir" ]; then
    echo "output directory already exists: $output_dir" >&2
    no_transfer
    exit 73
fi

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
camera=${TCA_CAMERA:-$project_dir/build/tca-camera}
flat_tool=${TCA_FLAT_FIELD_TOOL:-$project_dir/build/tca-flat-field}
stats_tool=${TCA_FRAME_STATS_TOOL:-$project_dir/scripts/tca-frame-stats}
ffmpeg=${TCA_FFMPEG:-ffmpeg}

for tool in "$camera" "$flat_tool" "$stats_tool"; do
    if [ ! -x "$tool" ]; then
        echo "missing executable: $tool" >&2
        no_transfer
        exit 69
    fi
done
if ! command -v "$ffmpeg" >/dev/null 2>&1 && [ ! -x "$ffmpeg" ]; then
    echo "missing ffmpeg executable: $ffmpeg" >&2
    no_transfer
    exit 69
fi
for command in cat date find mkdir sort tr uname wc; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "missing command: $command" >&2
        no_transfer
        exit 69
    fi
done
if command -v sha256sum >/dev/null 2>&1; then
    hash_file() { sha256sum "$1"; }
elif command -v shasum >/dev/null 2>&1; then
    hash_file() { shasum -a 256 "$1"; }
else
    echo "missing sha256sum or shasum" >&2
    no_transfer
    exit 69
fi

mkdir -m 0755 "$output_dir"

cleanup_incomplete() {
    status=$?
    trap - EXIT
    if [ "$status" -ne 0 ]; then
        printf 'status=incomplete exit=%s\n' "$status" \
            > "$output_dir/SESSION-INCOMPLETE.txt"
    fi
    exit "$status"
}
trap cleanup_incomplete EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

printf '%s\n' "$project_dir" > "$output_dir/project-directory.txt"
git_commit=not-a-git-checkout
if command -v git >/dev/null 2>&1; then
    git_commit=$(git -C "$project_dir" rev-parse HEAD 2>/dev/null ||
        printf '%s' not-a-git-checkout)
fi
printf '%s\n' "$git_commit" > "$output_dir/reader-commit.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$output_dir/start-utc.txt"
uname -a > "$output_dir/uname.txt"
cat > "$output_dir/session-settings.txt" <<EOF
mode=2
width=1280
height=960
phase=$phase
exposure_ms=$exposure_ms
camera_gain=$camera_gain
dark_frames=$dark_frames
flat_batches=$flat_batches
flat_frames_per_batch=$flat_frames_per_batch
EOF

pause_for() {
    printf '\n%s\n' "$1" >&2
    printf 'Press Enter only when that physical state is ready: ' >&2
    IFS= read -r ignored
}

capture() {
    name=$1
    frames=$2
    "$camera" capture --mode 2 --frames "$frames" \
        --raw-first "$output_dir/$name-first-device.raw" \
        --bayer "$output_dir/$name.bayer" \
        --exposure-ms "$exposure_ms" --gain "$camera_gain" \
        > "$output_dir/$name.stdout.txt" \
        2> "$output_dir/$name.stderr.txt"

    raw_bytes=$(wc -c < "$output_dir/$name-first-device.raw" | tr -d ' ')
    bayer_bytes=$(wc -c < "$output_dir/$name.bayer" | tr -d ' ')
    expected_bayer_bytes=$((FRAME_BYTES * frames))
    if [ "$raw_bytes" -ne "$DEVICE_BYTES" ] ||
       [ "$bayer_bytes" -ne "$expected_bayer_bytes" ]; then
        echo "$name size mismatch: raw=$raw_bytes Bayer=$bayer_bytes" >&2
        exit 1
    fi
}

pause_for "BLOCK the microscope illumination completely. Keep every optical and camera setting fixed."
capture darks "$dark_frames"

: > "$output_dir/flats.bayer"
batch=1
while [ "$batch" -le "$flat_batches" ]; do
    if [ "$batch" -eq 1 ]; then
        instruction="RESTORE illumination and present a clean, unclipped, feature-free blank field. Defocus or translate it."
    else
        instruction="TRANSLATE or defocus the blank field to a new position without changing illumination, optics, exposure, or gain."
    fi
    pause_for "$instruction"
    batch_name=$(printf 'flat-batch-%02d' "$batch")
    capture "$batch_name" "$flat_frames_per_batch"
    cat "$output_dir/$batch_name.bayer" >> "$output_dir/flats.bayer"
    batch=$((batch + 1))
done
flat_frames=$((flat_batches * flat_frames_per_batch))

"$flat_tool" calibrate --mode 2 --phase "$phase" \
    --dark "$output_dir/darks.bayer" --dark-frames "$dark_frames" \
    --flat "$output_dir/flats.bayer" --flat-frames "$flat_frames" \
    --exposure-ms "$exposure_ms" --camera-gain "$camera_gain" \
    --output "$output_dir/mode2.tca-flat" \
    > "$output_dir/calibrate.stdout.txt" \
    2> "$output_dir/calibrate.stderr.txt"
"$flat_tool" inspect --calibration "$output_dir/mode2.tca-flat" \
    > "$output_dir/calibration.json"

pause_for "Present a FRESH blank field that was not held stationary during calibration. Keep all settings fixed."
capture validation-blank 1
"$flat_tool" apply --calibration "$output_dir/mode2.tca-flat" \
    --input "$output_dir/validation-blank.bayer" \
    --output "$output_dir/validation-blank-corrected.bayer" \
    > "$output_dir/validation-blank-apply.stdout.txt" \
    2> "$output_dir/validation-blank-apply.stderr.txt"
"$stats_tool" "$output_dir/validation-blank.bayer" --mode 2 \
    --json "$output_dir/validation-blank.stats.json"
"$stats_tool" "$output_dir/validation-blank-corrected.bayer" --mode 2 \
    --json "$output_dir/validation-blank-corrected.stats.json"

pause_for "Present a REAL specimen for the acceptance image. Keep illumination, optics, exposure, gain, and camera position fixed."
capture validation-specimen 1
"$flat_tool" apply --calibration "$output_dir/mode2.tca-flat" \
    --input "$output_dir/validation-specimen.bayer" \
    --output "$output_dir/validation-specimen-corrected.bayer" \
    > "$output_dir/validation-specimen-apply.stdout.txt" \
    2> "$output_dir/validation-specimen-apply.stderr.txt"
"$stats_tool" "$output_dir/validation-specimen.bayer" --mode 2 \
    --json "$output_dir/validation-specimen.stats.json"
"$stats_tool" "$output_dir/validation-specimen-corrected.bayer" --mode 2 \
    --json "$output_dir/validation-specimen-corrected.stats.json"

for name in validation-blank validation-blank-corrected \
    validation-specimen validation-specimen-corrected; do
    "$ffmpeg" -hide_banner -loglevel error -y \
        -f rawvideo -pixel_format "bayer_${phase}8" \
        -video_size 1280x960 -i "$output_dir/$name.bayer" \
        -frames:v 1 "$output_dir/$name.png"
done

(
    cd "$output_dir"
    find . -type f ! -name manifest.sha256 ! -name SESSION-INCOMPLETE.txt \
        -print | LC_ALL=C sort | while IFS= read -r file; do
            hash_file "$file"
        done > manifest.sha256
)

trap - EXIT
printf 'output=%s dark_frames=%s flat_frames=%s exposure_ms=%s gain=%s phase=%s status=ok\n' \
    "$output_dir" "$dark_frames" "$flat_frames" "$exposure_ms" \
    "$camera_gain" "$phase"
printf 'For corrected Linux preview, set TCA_FLAT_FIELD=%s/mode2.tca-flat with the same exposure and gain.\n' \
    "$output_dir"
