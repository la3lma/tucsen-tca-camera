/* Trace-confirmed Linux stream reader for the AmScope/Tucsen 0547:c003. */
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <libusb.h>

#ifndef TCA_VERSION
#define TCA_VERSION "0.0.0+unknown"
#endif

#define TCA_VID 0x0547u
#define TCA_PID 0xc003u
#define TCA_INTERFACE 0
#define TCA_ENDPOINT 0x82u
#define TCA_REQUEST_TYPE 0xc0u
#define TCA_CONTROL_LENGTH 10u
#define TCA_TIMEOUT_MS 3000u
#define TCA_MODE2_WIDTH 1280u
#define TCA_MODE2_HEIGHT 960u
#define TCA_MODE2_DEVICE_BYTES 1229312u
#define TCA_MODE2_ROW_TIME_US 120u
#define TCA_MODE0_WIDTH 3664u
#define TCA_MODE0_HEIGHT 2748u
#define TCA_MODE0_DEVICE_BYTES 10068992u
#define TCA_MODE0_ROW_TIME_US 309u
#define TCA_MAX_DEVICE_BYTES TCA_MODE0_DEVICE_BYTES
#define TCA_PREFIX_MARKER_BYTES 10u
#define TCA_INITIAL_RESYNC_LIMIT 2u
#define TCA_EXPOSURE_MAX_LINES 4000u
#define TCA_GAIN_MAX 320u
#define TCA_NEXT_PACKET_BYTES(value) ((((value) >> 9u) + 1u) << 9u)

_Static_assert(TCA_MODE2_DEVICE_BYTES ==
                   TCA_NEXT_PACKET_BYTES(TCA_MODE2_WIDTH * TCA_MODE2_HEIGHT),
               "mode 2 size must match the recovered next-packet formula");
_Static_assert(TCA_MODE0_DEVICE_BYTES ==
                   TCA_NEXT_PACKET_BYTES(TCA_MODE0_WIDTH * TCA_MODE0_HEIGHT),
               "mode 0 record size must match the packet formula");
_Static_assert(TCA_MODE2_DEVICE_BYTES -
                       TCA_MODE2_WIDTH * TCA_MODE2_HEIGHT ==
                   512u,
               "mode 2 record prefix must be 512 bytes");
_Static_assert(TCA_MODE0_DEVICE_BYTES - 512u + 192u ==
                   TCA_MODE0_WIDTH * TCA_MODE0_HEIGHT,
               "mode 0 head plus next-record continuation must be one frame");

struct init_step {
    uint8_t request;
    uint16_t value;
    uint16_t index;
    unsigned delay_after_ms;
};

struct mode_profile {
    unsigned number;
    uint16_t selector;
    unsigned width;
    unsigned height;
    size_t device_bytes;
    size_t head_offset;
    size_t continuation_offset;
    size_t continuation_bytes;
    unsigned row_time_us;
};

static const struct mode_profile mode_profiles[] = {
    {0u, 0x00c0u, TCA_MODE0_WIDTH, TCA_MODE0_HEIGHT,
     TCA_MODE0_DEVICE_BYTES, 512u, 320u, 192u, TCA_MODE0_ROW_TIME_US},
    {2u, 0x00c2u, TCA_MODE2_WIDTH, TCA_MODE2_HEIGHT,
     TCA_MODE2_DEVICE_BYTES, 512u, 0u, 0u, TCA_MODE2_ROW_TIME_US},
};

static const struct init_step init_steps[] = {
    {0xb4u, 0x00c2u, 0x0000u, 500u},
    {0xb5u, 0x00a2u, 0x0000u, 30u},
    {0xb7u, 0x1054u, 0x305eu, 30u},
    {0xb7u, 0x0064u, 0x3012u, 30u},
    {0xb5u, 0x00a1u, 0x0000u, 30u},
    {0xb7u, 0x1054u, 0x305eu, 30u},
    {0xb7u, 0x0d0fu, 0x3012u, 120u},
};

static const char execution_token[] = "capture";
static const char version[] = TCA_VERSION;
static volatile sig_atomic_t stop_requested;

static size_t pixel_bytes(const struct mode_profile *mode)
{
    return (size_t)mode->width * (size_t)mode->height;
}

static size_t head_bytes(const struct mode_profile *mode)
{
    return mode->device_bytes - mode->head_offset;
}

static unsigned max_exposure_ms(const struct mode_profile *mode)
{
    return (TCA_EXPOSURE_MAX_LINES * mode->row_time_us) / 1000u;
}

static const struct mode_profile *find_mode(unsigned number)
{
    size_t index;

    for (index = 0; index < sizeof(mode_profiles) / sizeof(mode_profiles[0]);
         ++index) {
        if (mode_profiles[index].number == number) {
            return &mode_profiles[index];
        }
    }
    return NULL;
}

static void request_stop(int signal_number)
{
    (void)signal_number;
    stop_requested = 1;
}

static int delay_ms(unsigned milliseconds)
{
    struct timespec requested;

    requested.tv_sec = (time_t)(milliseconds / 1000u);
    requested.tv_nsec = (long)(milliseconds % 1000u) * 1000000L;
    while (nanosleep(&requested, &requested) != 0) {
        if (errno != EINTR) {
            return -1;
        }
    }
    return 0;
}

static int parse_frames(const char *text, uint64_t *frames)
{
    char *end = NULL;
    const char *cursor;
    unsigned long long value;

    if (text == NULL || *text == '\0') {
        return 0;
    }
    for (cursor = text; *cursor != '\0'; ++cursor) {
        if (*cursor < '0' || *cursor > '9') {
            return 0;
        }
    }
    errno = 0;
    value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }
    *frames = (uint64_t)value;
    return 1;
}

static int parse_u32(const char *text, uint32_t minimum, uint32_t maximum,
                     uint32_t *parsed)
{
    char *end = NULL;
    const char *cursor;
    unsigned long value;

    if (text == NULL || *text == '\0') {
        return 0;
    }
    for (cursor = text; *cursor != '\0'; ++cursor) {
        if (*cursor < '0' || *cursor > '9') {
            return 0;
        }
    }
    errno = 0;
    value = strtoul(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' ||
        value < minimum || value > maximum) {
        return 0;
    }
    *parsed = (uint32_t)value;
    return 1;
}

static uint16_t encode_gain(uint32_t gain)
{
    if (gain < 64u) {
        return (uint16_t)(0x1040u + gain);
    }
    if (gain < 128u) {
        return (uint16_t)(0x1800u + gain);
    }
    if (gain < 192u) {
        return (uint16_t)(0x1bc0u + gain);
    }
    if (gain < 256u) {
        return (uint16_t)(0x1c00u + gain);
    }
    if (gain < 320u) {
        return (uint16_t)(0x1cc0u + gain);
    }
    return 0x1dffu;
}

static void print_plan(FILE *output, const struct mode_profile *mode)
{
    size_t pixels = pixel_bytes(mode);
    fprintf(output, "profile=tca-userspace-mode%u-stream-v1 target=0547:c003\n",
            mode->number);
    fprintf(output,
            "frame=%ux%u Bayer8 application-bytes=%zu device-bytes=%zu\n",
            mode->width, mode->height, pixels, mode->device_bytes);
    fprintf(output,
            "startup=seven fixed controls with selector=0x%04x; expected "
            "data-stage result is PIPE\n",
            mode->selector);
    fprintf(output,
            "capture=endpoint-0x82 record request=%zu; validate ten-byte "
            "0x88 marker; frame=head[%zu..%zu) plus %zu bytes at offset %zu "
            "in the next record\n",
            mode->device_bytes, mode->head_offset, mode->device_bytes,
            mode->continuation_bytes, mode->continuation_offset);
    fprintf(output,
            "raw-first=unmodified %zu-byte device frame; Bayer output "
            "contains the following %zu-byte raster\n",
            mode->device_bytes, pixels);
    fprintf(output,
          "controls=optional exposure-ms 1..%u and normalized-gain 0..320; "
          "each becomes one trace-confirmed b7 register write\n",
          max_exposure_ms(mode));
}

static int trace_command_result_accepted(
    uint8_t request, const unsigned char response[TCA_CONTROL_LENGTH],
    int result)
{
    if (result == LIBUSB_ERROR_PIPE || result == (int)TCA_CONTROL_LENGTH) {
        return 1;
    }
    return result == 1 && response[0] == request;
}

static int apply_trace_command(libusb_device_handle *handle,
                               size_t sequence, const char *role,
                               uint8_t request, uint16_t value,
                               uint16_t index, unsigned delay_after_ms)
{
    unsigned char response[TCA_CONTROL_LENGTH] = {0};
    int result = libusb_control_transfer(
        handle, TCA_REQUEST_TYPE, request, value, index, response,
        TCA_CONTROL_LENGTH, TCA_TIMEOUT_MS);

    if (result >= 0) {
        fprintf(stderr,
                "%s=%zu request=0x%02x value=0x%04x index=0x%04x "
                "result=bytes (%d) first=0x%02x\n",
                role, sequence, request, value, index, result,
                result > 0 ? response[0] : 0u);
    } else {
        fprintf(stderr,
                "%s=%zu request=0x%02x value=0x%04x index=0x%04x "
                "result=%s (%d)\n",
                role, sequence, request, value, index,
                libusb_error_name(result), result);
    }
    if (!trace_command_result_accepted(request, response, result)) {
        return result == 0 ? LIBUSB_ERROR_OTHER : result;
    }
    if (delay_ms(delay_after_ms) != 0) {
        return LIBUSB_ERROR_OTHER;
    }
    return 0;
}

static int apply_initialization(libusb_device_handle *handle,
                                const struct mode_profile *mode)
{
    size_t index;

    for (index = 0;
         index < sizeof(init_steps) / sizeof(init_steps[0]); ++index) {
        struct init_step selected = init_steps[index];
        const struct init_step *step = &selected;
        if (index == 0u) {
            selected.value = mode->selector;
        }
        int result = apply_trace_command(
            handle, index + 1u, "init", step->request, step->value,
            step->index, step->delay_after_ms);
        if (result != 0) {
            return result;
        }
    }
    return 0;
}

static int read_device_frame(libusb_device_handle *handle,
                             const struct mode_profile *mode,
                             unsigned char *frame, size_t *received)
{
    int transferred = 0;
    int requested = (int)mode->device_bytes;
    int result;

    *received = 0u;
    result = libusb_bulk_transfer(handle, TCA_ENDPOINT, frame, requested,
                                  &transferred, TCA_TIMEOUT_MS);
    if (transferred > 0) {
        *received = (size_t)transferred;
    }
    if (result != 0) {
        fprintf(stderr, "bulk result=%s (%d) transferred=%d\n",
                libusb_error_name(result), result, transferred);
        return result;
    }
    if (transferred != requested) {
        fprintf(stderr, "bulk short requested=%d transferred=%d\n",
                requested, transferred);
        return LIBUSB_ERROR_IO;
    }
    return *received == mode->device_bytes ? 0 : LIBUSB_ERROR_IO;
}

static int validate_device_prefix(const struct mode_profile *mode,
                                  const unsigned char *device_frame)
{
    size_t byte_index;

    if (mode->head_offset < TCA_PREFIX_MARKER_BYTES) {
        return 0;
    }
    for (byte_index = 0; byte_index < TCA_PREFIX_MARKER_BYTES; ++byte_index) {
        if (device_frame[byte_index] != 0x88u) {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    libusb_context *context = NULL;
    libusb_device_handle *handle = NULL;
    unsigned char *device_frame = NULL;
    unsigned char *next_device_frame = NULL;
    unsigned char *pixels = NULL;
    FILE *raw_first = NULL;
    FILE *bayer = NULL;
    FILE *timestamps = NULL;
    uint64_t requested_frames = 0;
    uint64_t frames = 0;
    unsigned initial_resyncs = 0u;
    const char *raw_path = NULL;
    const char *bayer_path = NULL;
    const char *timestamps_path = NULL;
    uint32_t exposure_ms = 0u;
    uint32_t gain = 0u;
    uint32_t mode_number = 2u;
    const struct mode_profile *mode = NULL;
    int exposure_set = 0;
    int gain_set = 0;
    int mode_set = 0;
    int frames_set = 0;
    int raw_written = 0;
    int current_loaded = 0;
    int claimed = 0;
    int argument;
    int result;
    int status = EXIT_FAILURE;

    if (argc == 1 ||
        (argc == 2 && strcmp(argv[1], "--help") == 0)) {
        print_plan(stdout, find_mode(2u));
        fputs("available-modes=0:3664x2748-still,2:1280x960-preview "
              "(default=2)\n", stdout);
        fprintf(stdout,
                "NO TRANSFER SENT. usage: %s %s --frames COUNT "
                "--raw-first RAW --bayer OUTPUT|- "
                "[--timestamps CSV] [--mode 0|2] "
                "[--exposure-ms MS] [--gain 0..320]\n",
                argv[0], execution_token);
        return EXIT_SUCCESS;
    }
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        fprintf(stdout, "tca-camera %s\n", version);
        return EXIT_SUCCESS;
    }
    if (strcmp(argv[1], execution_token) != 0) {
        fputs("NO TRANSFER SENT: invalid arguments\n", stderr);
        return 64;
    }
    for (argument = 2; argument < argc; argument += 2) {
        if (argument + 1 >= argc) {
            fputs("NO TRANSFER SENT: option missing value\n", stderr);
            return 64;
        }
        if (strcmp(argv[argument], "--frames") == 0 &&
            !frames_set &&
            parse_frames(argv[argument + 1], &requested_frames)) {
            frames_set = 1;
            continue;
        }
        if (strcmp(argv[argument], "--raw-first") == 0 && raw_path == NULL) {
            raw_path = argv[argument + 1];
            continue;
        }
        if (strcmp(argv[argument], "--bayer") == 0 && bayer_path == NULL) {
            bayer_path = argv[argument + 1];
            continue;
        }
        if (strcmp(argv[argument], "--timestamps") == 0 &&
            timestamps_path == NULL) {
            timestamps_path = argv[argument + 1];
            continue;
        }
        if (strcmp(argv[argument], "--mode") == 0 && !mode_set &&
            parse_u32(argv[argument + 1], 0u, 2u, &mode_number) &&
            find_mode(mode_number) != NULL) {
            mode_set = 1;
            continue;
        }
        if (strcmp(argv[argument], "--exposure-ms") == 0 && !exposure_set &&
            parse_u32(argv[argument + 1], 1u,
                      (TCA_EXPOSURE_MAX_LINES * TCA_MODE0_ROW_TIME_US) /
                          1000u,
                      &exposure_ms)) {
            exposure_set = 1;
            continue;
        }
        if (strcmp(argv[argument], "--gain") == 0 && !gain_set &&
            parse_u32(argv[argument + 1], 0u, TCA_GAIN_MAX, &gain)) {
            gain_set = 1;
            continue;
        }
        fputs("NO TRANSFER SENT: invalid, duplicate, or out-of-range option\n",
              stderr);
        return 64;
    }
    if (!frames_set || raw_path == NULL || bayer_path == NULL ||
        strcmp(raw_path, "-") == 0 ||
        strcmp(raw_path, bayer_path) == 0 ||
        (timestamps_path != NULL &&
         (strcmp(timestamps_path, "-") == 0 ||
          strcmp(timestamps_path, raw_path) == 0 ||
          strcmp(timestamps_path, bayer_path) == 0))) {
        fputs("NO TRANSFER SENT: missing or conflicting output paths\n", stderr);
        return 64;
    }
    mode = find_mode(mode_number);
    if (mode == NULL ||
        (exposure_set && exposure_ms > max_exposure_ms(mode))) {
        fputs("NO TRANSFER SENT: exposure is out of range for selected mode\n",
              stderr);
        return 64;
    }
    print_plan(stderr, mode);
    raw_first = fopen(raw_path, "wbx");
    if (raw_first == NULL) {
        perror(raw_path);
        goto done;
    }
    bayer = strcmp(bayer_path, "-") == 0 ? stdout : fopen(bayer_path, "wbx");
    if (bayer == NULL) {
        perror(bayer_path);
        goto done;
    }
    if (timestamps_path != NULL) {
        timestamps = fopen(timestamps_path, "wx");
        if (timestamps == NULL) {
            perror(timestamps_path);
            goto done;
        }
        if (fputs("frame,monotonic_ns\n", timestamps) == EOF ||
            fflush(timestamps) != 0) {
            perror("write timestamp header");
            goto done;
        }
    }
    if (signal(SIGINT, request_stop) == SIG_ERR ||
        signal(SIGTERM, request_stop) == SIG_ERR ||
        signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        fputs("cannot install signal handlers\n", stderr);
        goto done;
    }
    device_frame = malloc(mode->device_bytes);
    if (mode->continuation_bytes > 0u) {
        next_device_frame = malloc(mode->device_bytes);
    }
    pixels = malloc(pixel_bytes(mode));
    if (device_frame == NULL || pixels == NULL ||
        (mode->continuation_bytes > 0u && next_device_frame == NULL)) {
        perror("malloc");
        goto done;
    }
    result = libusb_init(&context);
    if (result != 0) {
        fprintf(stderr, "libusb_init: %s\n", libusb_error_name(result));
        goto done;
    }
    handle = libusb_open_device_with_vid_pid(context, TCA_VID, TCA_PID);
    if (handle == NULL) {
        fputs("camera 0547:c003 not found or cannot be opened\n", stderr);
        goto done;
    }
    result = libusb_claim_interface(handle, TCA_INTERFACE);
    if (result != 0) {
        fprintf(stderr, "claim interface 0: %s\n", libusb_error_name(result));
        goto done;
    }
    claimed = 1;
    result = apply_initialization(handle, mode);
    if (result != 0) {
        fprintf(stderr, "initialization: %s (%d)\n",
                libusb_error_name(result), result);
        goto done;
    }
    if (exposure_set) {
        uint32_t lines = (exposure_ms * 1000u + mode->row_time_us - 1u) /
                         mode->row_time_us;
        if (lines == 0u || lines > TCA_EXPOSURE_MAX_LINES) {
            fputs("exposure conversion exceeded sensor range\n", stderr);
            goto done;
        }
        result = apply_trace_command(handle, 1u, "control-exposure", 0xb7u,
                                     (uint16_t)lines, 0x3012u, 30u);
        if (result != 0) {
            fprintf(stderr, "exposure control: %s (%d)\n",
                    libusb_error_name(result), result);
            goto done;
        }
        fprintf(stderr, "exposure-ms=%u programmed-lines=%u\n",
                exposure_ms, lines);
    }
    if (gain_set) {
        uint16_t encoded = encode_gain(gain);
        result = apply_trace_command(handle, 1u, "control-gain", 0xb7u,
                                     encoded, 0x305eu, 30u);
        if (result != 0) {
            fprintf(stderr, "gain control: %s (%d)\n",
                    libusb_error_name(result), result);
            goto done;
        }
        fprintf(stderr, "gain=%u programmed-register=0x%04x\n", gain,
                encoded);
    }

    if (exposure_set || gain_set) {
        size_t received = 0;

        result = read_device_frame(handle, mode, device_frame, &received);
        if (result != 0) {
            if (received > 0u &&
                (fwrite(device_frame, 1, received, raw_first) != received ||
                 fflush(raw_first) != 0)) {
                perror("write partial raw-first");
            }
            raw_written = received > 0u;
            goto done;
        }
        if (fwrite(device_frame, 1, mode->device_bytes, raw_first) !=
                mode->device_bytes ||
            fflush(raw_first) != 0) {
            perror("write control-settle raw-first");
            goto done;
        }
        raw_written = 1;
        fprintf(stderr,
                "control-settle discarded one pre-control buffered record\n");
    }

    while (!stop_requested &&
           (requested_frames == 0u || frames < requested_frames)) {
        if (!current_loaded) {
            size_t received = 0;

            result = read_device_frame(handle, mode, device_frame, &received);
            if (result != 0) {
                if (!raw_written && received > 0u) {
                    if (fwrite(device_frame, 1, received, raw_first) !=
                            received ||
                        fflush(raw_first) != 0) {
                        perror("write partial raw-first");
                    }
                    raw_written = 1;
                }
                goto done;
            }
            if (!raw_written &&
                fwrite(device_frame, 1, mode->device_bytes, raw_first) !=
                    mode->device_bytes) {
                perror("write raw-first");
                goto done;
            }
            if (!raw_written && fflush(raw_first) != 0) {
                perror("flush raw-first");
                goto done;
            }
            raw_written = 1;
            if (!validate_device_prefix(mode, device_frame)) {
                if (frames == 0u &&
                    initial_resyncs < TCA_INITIAL_RESYNC_LIMIT) {
                    ++initial_resyncs;
                    fprintf(stderr,
                            "initial frame marker validation failed; "
                            "discarding bounded warm-up record %u/%u\n",
                            initial_resyncs, TCA_INITIAL_RESYNC_LIMIT);
                    continue;
                }
                fputs("record marker validation failed\n", stderr);
                goto done;
            }
            current_loaded = 1;
        }
        memcpy(pixels, device_frame + mode->head_offset, head_bytes(mode));
        if (mode->continuation_bytes > 0u) {
            size_t received = 0;
            unsigned char *swap;

            result = read_device_frame(handle, mode, next_device_frame,
                                       &received);
            if (result != 0) {
                goto done;
            }
            if (!validate_device_prefix(mode, next_device_frame)) {
                if (frames == 0u &&
                    initial_resyncs < TCA_INITIAL_RESYNC_LIMIT) {
                    ++initial_resyncs;
                    current_loaded = 0;
                    fprintf(stderr,
                            "initial continuation marker validation failed; "
                            "discarding bounded warm-up pair %u/%u\n",
                            initial_resyncs, TCA_INITIAL_RESYNC_LIMIT);
                    continue;
                }
                fputs("continuation record marker validation failed\n",
                      stderr);
                goto done;
            }
            memcpy(pixels + head_bytes(mode),
                   next_device_frame + mode->continuation_offset,
                   mode->continuation_bytes);
            swap = device_frame;
            device_frame = next_device_frame;
            next_device_frame = swap;
            current_loaded = 1;
        } else {
            current_loaded = 0;
        }
        if (fwrite(pixels, 1, pixel_bytes(mode), bayer) !=
            pixel_bytes(mode)) {
            perror("write Bayer stream");
            goto done;
        }
        if (timestamps != NULL) {
            struct timespec delivered;
            uint64_t delivered_ns;

            if (clock_gettime(CLOCK_MONOTONIC, &delivered) != 0 ||
                delivered.tv_sec < 0 || delivered.tv_nsec < 0) {
                perror("clock_gettime(CLOCK_MONOTONIC)");
                goto done;
            }
            delivered_ns = (uint64_t)delivered.tv_sec * 1000000000ULL +
                           (uint64_t)delivered.tv_nsec;
            if (fprintf(timestamps, "%llu,%llu\n",
                        (unsigned long long)(frames + 1u),
                        (unsigned long long)delivered_ns) < 0 ||
                fflush(timestamps) != 0) {
                perror("write timestamp");
                goto done;
            }
        }
        ++frames;
    }
    if (fflush(raw_first) != 0 || fflush(bayer) != 0 ||
        (timestamps != NULL && fflush(timestamps) != 0)) {
        perror("flush output");
        goto done;
    }
    status = EXIT_SUCCESS;

done:
    fprintf(stderr, "frames=%llu status=%s\n",
            (unsigned long long)frames,
            status == EXIT_SUCCESS ? "ok" : "error");
    if (claimed) {
        result = libusb_release_interface(handle, TCA_INTERFACE);
        if (result != 0) {
            fprintf(stderr, "release interface 0: %s\n",
                    libusb_error_name(result));
            status = EXIT_FAILURE;
        }
    }
    if (handle != NULL) {
        libusb_close(handle);
    }
    if (context != NULL) {
        libusb_exit(context);
    }
    free(pixels);
    free(next_device_frame);
    free(device_frame);
    if (bayer != NULL && bayer != stdout && fclose(bayer) != 0) {
        status = EXIT_FAILURE;
    }
    if (raw_first != NULL && fclose(raw_first) != 0) {
        status = EXIT_FAILURE;
    }
    if (timestamps != NULL && fclose(timestamps) != 0) {
        status = EXIT_FAILURE;
    }
    return status;
}
