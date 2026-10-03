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

#define TCA_VID 0x0547u
#define TCA_PID 0xc003u
#define TCA_INTERFACE 0
#define TCA_ENDPOINT 0x82u
#define TCA_REQUEST_TYPE 0xc0u
#define TCA_CONTROL_LENGTH 10u
#define TCA_TIMEOUT_MS 3000u
#define TCA_WIDTH 1280u
#define TCA_HEIGHT 960u
#define TCA_PIXEL_BYTES ((size_t)TCA_WIDTH * (size_t)TCA_HEIGHT)
#define TCA_DEVICE_BYTES 1229312u
#define TCA_MARKER_BYTES 10u
#define TCA_MODE2_ROW_TIME_US 120u
#define TCA_EXPOSURE_MAX_LINES 4000u
#define TCA_GAIN_MAX 320u

struct init_step {
    uint8_t request;
    uint16_t value;
    uint16_t index;
    unsigned delay_after_ms;
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

static const size_t read_lengths[] = {524288u, 524288u, 180736u};
static const size_t marker_offsets[] = {0u, 524288u, 1048576u};
static const char execution_token[] = "capture";
static const char version[] = "0.1.0-alpha.1";
static volatile sig_atomic_t stop_requested;

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

static void print_plan(FILE *output)
{
    fprintf(output, "profile=tca-userspace-mode2-stream-v1 target=0547:c003\n");
    fprintf(output,
            "frame=1280x960 Bayer8 application-bytes=%zu "
            "device-bytes=%u\n",
            TCA_PIXEL_BYTES, TCA_DEVICE_BYTES);
    fputs("startup=seven exact trace-confirmed controls; expected data-stage "
          "result is PIPE\n", output);
    fputs("capture=endpoint-0x82 reads 524288,524288,180736; validate and "
          "repair ten-byte 0x88 markers\n", output);
    fputs("raw-first=unmodified 1229312-byte device frame; Bayer output "
          "discards final 512-byte alignment surplus\n", output);
    fputs("controls=optional exposure-ms 1..480 and normalized-gain 0..320; "
          "each becomes one trace-confirmed b7 register write\n", output);
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

    fprintf(stderr,
            "%s=%zu request=0x%02x value=0x%04x index=0x%04x "
            "result=%s (%d)\n",
            role, sequence, request, value, index,
            libusb_error_name(result), result);
    if (result != LIBUSB_ERROR_PIPE && result != (int)TCA_CONTROL_LENGTH) {
        return result == 0 ? LIBUSB_ERROR_OTHER : result;
    }
    if (delay_ms(delay_after_ms) != 0) {
        return LIBUSB_ERROR_OTHER;
    }
    return 0;
}

static int apply_initialization(libusb_device_handle *handle)
{
    size_t index;

    for (index = 0;
         index < sizeof(init_steps) / sizeof(init_steps[0]); ++index) {
        const struct init_step *step = &init_steps[index];
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
                             unsigned char *frame, size_t *received)
{
    size_t index;

    *received = 0u;
    for (index = 0;
         index < sizeof(read_lengths) / sizeof(read_lengths[0]); ++index) {
        int transferred = 0;
        int requested = (int)read_lengths[index];
        int result = libusb_bulk_transfer(
            handle, TCA_ENDPOINT, frame + *received, requested, &transferred,
            TCA_TIMEOUT_MS);

        if (transferred > 0) {
            *received += (size_t)transferred;
        }
        if (result != 0) {
            fprintf(stderr, "bulk=%zu result=%s (%d) transferred=%d\n",
                    index, libusb_error_name(result), result, transferred);
            return result;
        }
        if (transferred != requested) {
            fprintf(stderr, "bulk=%zu short requested=%d transferred=%d\n",
                    index, requested, transferred);
            return LIBUSB_ERROR_IO;
        }
    }
    return *received == TCA_DEVICE_BYTES ? 0 : LIBUSB_ERROR_IO;
}

static int validate_and_repair_markers(unsigned char *pixels)
{
    size_t marker_index;

    for (marker_index = 0;
         marker_index < sizeof(marker_offsets) / sizeof(marker_offsets[0]);
         ++marker_index) {
        size_t offset = marker_offsets[marker_index];
        size_t byte_index;

        if (offset + 2u * TCA_MARKER_BYTES > TCA_PIXEL_BYTES) {
            return 0;
        }
        for (byte_index = 0; byte_index < TCA_MARKER_BYTES; ++byte_index) {
            if (pixels[offset + byte_index] != 0x88u) {
                return 0;
            }
        }
        memcpy(pixels + offset, pixels + offset + TCA_MARKER_BYTES,
               TCA_MARKER_BYTES);
    }
    return 1;
}

int main(int argc, char **argv)
{
    libusb_context *context = NULL;
    libusb_device_handle *handle = NULL;
    unsigned char *device_frame = NULL;
    unsigned char *pixels = NULL;
    FILE *raw_first = NULL;
    FILE *bayer = NULL;
    uint64_t requested_frames = 0;
    uint64_t frames = 0;
    const char *raw_path = NULL;
    const char *bayer_path = NULL;
    uint32_t exposure_ms = 0u;
    uint32_t gain = 0u;
    int exposure_set = 0;
    int gain_set = 0;
    int frames_set = 0;
    int claimed = 0;
    int argument;
    int result;
    int status = EXIT_FAILURE;

    if (argc == 1 ||
        (argc == 2 && strcmp(argv[1], "--help") == 0)) {
        print_plan(stdout);
        fprintf(stdout,
                "NO TRANSFER SENT. usage: %s %s --frames COUNT "
                "--raw-first RAW --bayer OUTPUT|- "
                "[--exposure-ms 1..480] [--gain 0..320]\n",
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
        if (strcmp(argv[argument], "--exposure-ms") == 0 && !exposure_set &&
            parse_u32(argv[argument + 1], 1u, 480u, &exposure_ms)) {
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
        strcmp(raw_path, bayer_path) == 0) {
        fputs("NO TRANSFER SENT: missing or conflicting output paths\n", stderr);
        return 64;
    }
    print_plan(stderr);
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
    if (signal(SIGINT, request_stop) == SIG_ERR ||
        signal(SIGTERM, request_stop) == SIG_ERR ||
        signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        fputs("cannot install signal handlers\n", stderr);
        goto done;
    }
    device_frame = malloc(TCA_DEVICE_BYTES);
    pixels = malloc(TCA_PIXEL_BYTES);
    if (device_frame == NULL || pixels == NULL) {
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
    result = apply_initialization(handle);
    if (result != 0) {
        fprintf(stderr, "initialization: %s (%d)\n",
                libusb_error_name(result), result);
        goto done;
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
    if (exposure_set) {
        uint32_t lines = (exposure_ms * 1000u + TCA_MODE2_ROW_TIME_US - 1u) /
                         TCA_MODE2_ROW_TIME_US;
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

    while (!stop_requested &&
           (requested_frames == 0u || frames < requested_frames)) {
        size_t received = 0;

        result = read_device_frame(handle, device_frame, &received);
        if (result != 0) {
            if (frames == 0u && received > 0u) {
                (void)fwrite(device_frame, 1, received, raw_first);
            }
            goto done;
        }
        if (frames == 0u &&
            fwrite(device_frame, 1, TCA_DEVICE_BYTES, raw_first) !=
                TCA_DEVICE_BYTES) {
            perror("write raw-first");
            goto done;
        }
        memcpy(pixels, device_frame, TCA_PIXEL_BYTES);
        if (!validate_and_repair_markers(pixels)) {
            fputs("frame marker validation failed\n", stderr);
            goto done;
        }
        if (fwrite(pixels, 1, TCA_PIXEL_BYTES, bayer) != TCA_PIXEL_BYTES) {
            perror("write Bayer stream");
            goto done;
        }
        ++frames;
    }
    if (fflush(raw_first) != 0 || fflush(bayer) != 0) {
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
    free(device_frame);
    if (bayer != NULL && bayer != stdout && fclose(bayer) != 0) {
        status = EXIT_FAILURE;
    }
    if (raw_first != NULL && fclose(raw_first) != 0) {
        status = EXIT_FAILURE;
    }
    return status;
}
