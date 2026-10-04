#!/bin/sh
# Camera-free lifecycle and backpressure acceptance for the real V4L2 bridge.

set -eu
LC_ALL=C
export LC_ALL

TOKEN=--run-v4l2-bridge-synthetic-acceptance
DEFAULT_VIDEO_NUMBER=44
MAX_RSS_GROWTH_KIB=65536

usage()
{
    printf 'usage: sudo %s %s [OUTPUT_DIRECTORY [VIDEO_NUMBER [MODE]]]\n' "$0" "$TOKEN"
    printf '       exercises the real bridge with a USB-inert synthetic reader\n'
}

is_decimal()
{
    case "$1" in
        ''|*[!0-9]*) return 1 ;;
        *) return 0 ;;
    esac
}

if [ "$#" -eq 0 ]; then
    printf 'harness=dry-run target=v4l2-bridge transfer=none system_change=none\n'
    usage
    printf 'NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE.\n'
    exit 0
fi
if [ "$#" -gt 4 ] || [ "$1" != "$TOKEN" ]; then
    usage >&2
    printf 'NO USB TRANSFER SENT. NO SYSTEM CHANGE MADE.\n' >&2
    exit 64
fi
if [ "$(uname -s)" != Linux ] || [ "$(id -u)" -ne 0 ]; then
    printf 'this acceptance requires Linux root for temporary v4l2loopback\n' >&2
    exit 69
fi

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
bridge=$project_dir/scripts/tca-v4l2
fake_reader=$project_dir/tests/fake_tca_reader.py
flat_field_tool=$project_dir/build/tca-flat-field
timing_analyzer=$project_dir/scripts/tca-timing-stats
video_number=${3:-$DEFAULT_VIDEO_NUMBER}
mode=${4:-2}
is_decimal "$video_number" && is_decimal "$mode" || {
    printf 'VIDEO_NUMBER and MODE must be decimal integers\n' >&2
    exit 64
}
case "$mode" in
    0)
        width=3664
        height=2748
        frame_bytes=10068672
        raw_bytes=10068992
        yuyv_frame_bytes=20137344
        normal_frames=2
        slow_frames=3
        consumer_timeout=60
        ;;
    2)
        width=1280
        height=960
        frame_bytes=1228800
        raw_bytes=1229312
        yuyv_frame_bytes=2457600
        normal_frames=4
        slow_frames=8
        consumer_timeout=30
        ;;
    *)
        printf 'MODE must be 0 or 2\n' >&2
        exit 64
        ;;
esac
device=/dev/video$video_number

git -C "$project_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    printf 'project is not a Git worktree: %s\n' "$project_dir" >&2
    exit 66
}
if [ -n "$(git -C "$project_dir" status --porcelain)" ]; then
    printf 'project worktree must be clean: %s\n' "$project_dir" >&2
    exit 73
fi
for executable in "$bridge" "$fake_reader" "$flat_field_tool" \
                  "$timing_analyzer"; do
    [ -x "$executable" ] || {
        printf 'missing executable: %s\n' "$executable" >&2
        exit 69
    }
done
for command_name in dd ffmpeg find git grep mktemp pgrep ps python3 \
                    sha256sum sort stat timeout tr v4l2-ctl wc xargs; do
    command -v "$command_name" >/dev/null 2>&1 || {
        printf 'missing required command: %s\n' "$command_name" >&2
        exit 69
    }
done
[ -x /usr/sbin/modprobe ] || {
    printf 'missing /usr/sbin/modprobe\n' >&2
    exit 69
}
if grep -q '^v4l2loopback ' /proc/modules 2>/dev/null || [ -e "$device" ]; then
    printf 'refusing an existing loopback setup or device: %s\n' "$device" >&2
    exit 73
fi

if [ "$#" -ge 2 ]; then
    output_dir=$2
    [ ! -e "$output_dir" ] || {
        printf 'output directory already exists: %s\n' "$output_dir" >&2
        exit 73
    }
    mkdir -m 0755 "$output_dir"
else
    output_dir=$(mktemp -d "${TMPDIR:-/tmp}/tca-v4l2-synthetic.XXXXXX")
fi

bridge_pid=0
slow_consumer_pid=0
cleanup()
{
    if [ "$slow_consumer_pid" -ne 0 ]; then
        kill "$slow_consumer_pid" 2>/dev/null || true
        wait "$slow_consumer_pid" 2>/dev/null || true
        slow_consumer_pid=0
    fi
    if [ "$bridge_pid" -ne 0 ]; then
        kill -TERM "$bridge_pid" 2>/dev/null || true
        wait "$bridge_pid" 2>/dev/null || true
        bridge_pid=0
    fi
    if grep -q '^v4l2loopback ' /proc/modules 2>/dev/null; then
        /usr/sbin/modprobe -r v4l2loopback 2>/dev/null || true
    fi
    if [ -d "$output_dir" ]; then
        (
            cd "$output_dir"
            find . -type f ! -name manifest.sha256 -print0 | sort -z | \
                xargs -0 sha256sum >manifest.sha256
        )
    fi
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

collect_tree_pids()
{
    tree_root=$1
    printf '%s\n' "$tree_root"
    for tree_child in $(pgrep -P "$tree_root" 2>/dev/null || true); do
        collect_tree_pids "$tree_child"
    done
}

tree_rss_kib()
{
    rss_total=0
    for rss_pid in $(collect_tree_pids "$1"); do
        rss_value=$(ps -o rss= -p "$rss_pid" 2>/dev/null | tr -d '[:space:]')
        case "$rss_value" in
            ''|*[!0-9]*) ;;
            *) rss_total=$((rss_total + rss_value)) ;;
        esac
    done
    printf '%s\n' "$rss_total"
}

commit=$(git -C "$project_dir" rev-parse HEAD)
{
    printf 'profile=tca-v4l2-synthetic-lifecycle-v4\n'
    printf 'usb_transfer=none\n'
    printf 'project_commit=%s\n' "$commit"
    printf 'video_device=%s\n' "$device"
    printf 'mode=%s\n' "$mode"
    printf 'geometry=%sx%s\n' "$width" "$height"
    printf 'normal_consumer_frames=%s\n' "$normal_frames"
    printf 'slow_consumer_frames=%s\n' "$slow_frames"
    printf 'slow_consumer_sleep_ms=350\n'
    printf 'max_rss_growth_kib=%s\n' "$MAX_RSS_GROWTH_KIB"
} >"$output_dir/session.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' >"$output_dir/start-utc.txt"
uname -a >"$output_dir/uname.txt"

dd if=/dev/zero bs=$frame_bytes count=2 status=none | \
    tr '\000' '\012' >"$output_dir/darks.bayer"
dd if=/dev/zero bs=$frame_bytes count=2 status=none | \
    tr '\000' '\156' >"$output_dir/flats.bayer"
"$flat_field_tool" calibrate --mode "$mode" --phase grbg \
    --dark "$output_dir/darks.bayer" --dark-frames 2 \
    --flat "$output_dir/flats.bayer" --flat-frames 2 \
    --exposure-ms 100 --camera-gain 20 \
    --output "$output_dir/uniform.tca-flat" \
    2>"$output_dir/calibrate.stderr.txt"
"$flat_field_tool" inspect --calibration "$output_dir/uniform.tca-flat" \
    >"$output_dir/calibration.json"

TCA_CAMERA_READER="$fake_reader" TCA_FAKE_FRAME_DELAY_MS=50 \
TCA_FLAT_FIELD="$output_dir/uniform.tca-flat" \
TCA_TIMESTAMPS="$output_dir/reader-timestamps.csv" \
    "$bridge" --serve "$output_dir/first-device.raw" \
    "$video_number" 100 20 "$mode" >"$output_dir/bridge.stdout.txt" \
    2>"$output_dir/bridge.stderr.txt" &
bridge_pid=$!

attempt=0
while [ "$attempt" -lt 100 ]; do
    if v4l2-ctl -d "$device" --all >"$output_dir/device.txt" 2>/dev/null &&
       grep -q "Pixel Format.*'YUYV'" "$output_dir/device.txt"; then
        break
    fi
    kill -0 "$bridge_pid" 2>/dev/null || {
        printf 'bridge exited before readiness\n' >&2
        exit 1
    }
    sleep 0.1
    attempt=$((attempt + 1))
done
[ "$attempt" -lt 100 ] || {
    printf 'timed out waiting for %s\n' "$device" >&2
    exit 1
}

rss_cold=$(tree_rss_kib "$bridge_pid")
ps -eo pid=,ppid=,rss=,stat=,comm=,args= >"$output_dir/processes-ready.txt"
timeout "$consumer_timeout" v4l2-ctl -d "$device" --stream-mmap=3 \
    --stream-count="$normal_frames" \
    --stream-to="$output_dir/normal-consumer.yuyv" \
    >"$output_dir/normal-consumer.stdout.txt" \
    2>"$output_dir/normal-consumer.stderr.txt"
[ "$(stat -c %s "$output_dir/normal-consumer.yuyv")" -eq \
   "$((normal_frames * yuyv_frame_bytes))" ]
kill -0 "$bridge_pid"

sleep 1
kill -0 "$bridge_pid"
rss_baseline=$(tree_rss_kib "$bridge_pid")
ps -eo pid=,ppid=,rss=,stat=,comm=,args= \
    >"$output_dir/processes-warm-baseline.txt"
timeout "$consumer_timeout" v4l2-ctl -d "$device" --stream-mmap=3 \
    --stream-count="$slow_frames" \
    --stream-sleep=count=1,sleep=350,mode=1 \
    --stream-to="$output_dir/slow-consumer.yuyv" \
    >"$output_dir/slow-consumer.stdout.txt" \
    2>"$output_dir/slow-consumer.stderr.txt" &
slow_consumer_pid=$!
sleep 1
rss_slow=$(tree_rss_kib "$bridge_pid")
ps -eo pid=,ppid=,rss=,stat=,comm=,args= >"$output_dir/processes-slow.txt"
wait "$slow_consumer_pid"
slow_consumer_pid=0
[ "$(stat -c %s "$output_dir/slow-consumer.yuyv")" -eq \
   "$((slow_frames * yuyv_frame_bytes))" ]
kill -0 "$bridge_pid"

rss_growth=$((rss_slow - rss_baseline))
[ "$rss_growth" -le "$MAX_RSS_GROWTH_KIB" ] || {
    printf 'bridge tree RSS grew beyond bound: %s KiB\n' "$rss_growth" >&2
    exit 1
}

ffmpeg -hide_banner -loglevel error -f rawvideo -pixel_format yuyv422 \
    -video_size "${width}x${height}" -i "$output_dir/normal-consumer.yuyv" \
    -frames:v "$normal_frames" -f framemd5 "$output_dir/normal.framemd5"
ffmpeg -hide_banner -loglevel error -f rawvideo -pixel_format yuyv422 \
    -video_size "${width}x${height}" -i "$output_dir/slow-consumer.yuyv" \
    -frames:v "$slow_frames" -f framemd5 "$output_dir/slow.framemd5"

kill -TERM "$bridge_pid"
set +e
wait "$bridge_pid"
bridge_status=$?
set -e
bridge_pid=0
[ "$bridge_status" -eq 143 ] || {
    printf 'bridge did not report deterministic TERM status: %s\n' \
        "$bridge_status" >&2
    exit 1
}
printf '%s\n' "$bridge_status" >"$output_dir/bridge-exit-status.txt"
[ ! -e "$device" ]
! grep -q '^v4l2loopback ' /proc/modules 2>/dev/null
[ "$(stat -c %s "$output_dir/first-device.raw")" -eq "$raw_bytes" ]
"$timing_analyzer" "$output_dir/reader-timestamps.csv" \
    --json "$output_dir/reader-timing.json"

normal_digests=$(grep -c '^[0-9]' "$output_dir/normal.framemd5")
slow_digests=$(grep -c '^[0-9]' "$output_dir/slow.framemd5")
[ "$normal_digests" -eq "$normal_frames" ]
[ "$slow_digests" -eq "$slow_frames" ]

/usr/sbin/modprobe v4l2loopback video_nr="$video_number" \
    card_label="TCA Camera 0547:c003" exclusive_caps=1 max_buffers=4
attempt=0
while [ ! -e "$device" ] && [ "$attempt" -lt 50 ]; do
    sleep 0.1
    attempt=$((attempt + 1))
done
[ -e "$device" ] || {
    printf 'pre-created loopback device did not appear: %s\n' "$device" >&2
    exit 1
}
grep -qx 'TCA Camera 0547:c003' \
    "/sys/class/video4linux/video${video_number}/name"

TCA_CAMERA_READER="$fake_reader" TCA_FAKE_FRAME_DELAY_MS=50 \
TCA_TIMESTAMPS="$output_dir/existing-reader-timestamps.csv" \
    "$bridge" --serve-existing "$output_dir/existing-first-device.raw" \
    "$video_number" 100 20 "$mode" \
    >"$output_dir/existing-bridge.stdout.txt" \
    2>"$output_dir/existing-bridge.stderr.txt" &
bridge_pid=$!

attempt=0
while [ "$attempt" -lt 100 ]; do
    if v4l2-ctl -d "$device" --all \
           >"$output_dir/existing-device.txt" 2>/dev/null &&
       grep -q "Pixel Format.*'YUYV'" "$output_dir/existing-device.txt"; then
        break
    fi
    kill -0 "$bridge_pid" 2>/dev/null || {
        printf 'existing-device bridge exited before readiness\n' >&2
        exit 1
    }
    sleep 0.1
    attempt=$((attempt + 1))
done
[ "$attempt" -lt 100 ] || {
    printf 'timed out waiting for existing device %s\n' "$device" >&2
    exit 1
}

timeout "$consumer_timeout" v4l2-ctl -d "$device" --stream-mmap=3 \
    --stream-count="$normal_frames" \
    --stream-to="$output_dir/existing-consumer.yuyv" \
    >"$output_dir/existing-consumer.stdout.txt" \
    2>"$output_dir/existing-consumer.stderr.txt"
[ "$(stat -c %s "$output_dir/existing-consumer.yuyv")" -eq \
   "$((normal_frames * yuyv_frame_bytes))" ]
kill -TERM "$bridge_pid"
set +e
wait "$bridge_pid"
existing_bridge_status=$?
set -e
bridge_pid=0
[ "$existing_bridge_status" -eq 143 ] || {
    printf 'existing-device bridge did not report TERM status: %s\n' \
        "$existing_bridge_status" >&2
    exit 1
}
printf '%s\n' "$existing_bridge_status" \
    >"$output_dir/existing-bridge-exit-status.txt"
[ -c "$device" ]
grep -q '^v4l2loopback ' /proc/modules
grep -qx 'TCA Camera 0547:c003' \
    "/sys/class/video4linux/video${video_number}/name"
[ "$(stat -c %s "$output_dir/existing-first-device.raw")" -eq "$raw_bytes" ]
"$timing_analyzer" "$output_dir/existing-reader-timestamps.csv" \
    --json "$output_dir/existing-reader-timing.json"
ffmpeg -hide_banner -loglevel error -f rawvideo -pixel_format yuyv422 \
    -video_size "${width}x${height}" \
    -i "$output_dir/existing-consumer.yuyv" \
    -frames:v "$normal_frames" -f framemd5 \
    "$output_dir/existing.framemd5"
existing_digests=$(grep -c '^[0-9]' "$output_dir/existing.framemd5")
[ "$existing_digests" -eq "$normal_frames" ]

/usr/sbin/modprobe -r v4l2loopback
[ ! -e "$device" ]
! grep -q '^v4l2loopback ' /proc/modules 2>/dev/null
{
    printf 'mode=%s\n' "$mode"
    printf 'geometry=%sx%s\n' "$width" "$height"
    printf 'normal_consumer_frames=%s\n' "$normal_digests"
    printf 'slow_consumer_frames=%s\n' "$slow_digests"
    printf 'consumer_detach_reattach=pass\n'
    printf 'bridge_alive_after_slow_consumer=pass\n'
    printf 'bridge_tree_rss_cold_kib=%s\n' "$rss_cold"
    printf 'bridge_tree_rss_baseline_kib=%s\n' "$rss_baseline"
    printf 'bridge_tree_rss_slow_kib=%s\n' "$rss_slow"
    printf 'bridge_tree_rss_growth_kib=%s\n' "$rss_growth"
    printf 'device_cleanup=pass\n'
    printf 'module_cleanup=pass\n'
    printf 'precreated_consumer_frames=%s\n' "$existing_digests"
    printf 'precreated_device_survived_bridge=pass\n'
    printf 'precreated_module_survived_bridge=pass\n'
    printf 'precreated_harness_cleanup=pass\n'
    printf 'usb_transfer=none\n'
} >"$output_dir/summary.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ' >"$output_dir/end-utc.txt"

printf 'v4l2_bridge_synthetic_acceptance=PASS\n'
printf 'evidence_directory=%s\n' "$output_dir"
