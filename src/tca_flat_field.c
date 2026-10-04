#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define TCFF_HEADER_BYTES 64u
#define TCFF_VERSION 1u
#define TCFF_RECORD_BYTES 4u
#define TCFF_HISTOGRAM_BINS 65536u

static const uint8_t tcff_magic[8] = {'T', 'C', 'A', 'F', 'F', '0', '1', 0};

struct geometry {
    uint32_t width;
    uint32_t height;
};

struct calibration_header {
    uint32_t width;
    uint32_t height;
    uint32_t phase;
    uint32_t dark_frames;
    uint32_t flat_frames;
    uint32_t min_signal_q8;
    uint32_t max_gain_q8;
    uint32_t references_q8[4];
};

static void usage(FILE *stream)
{
    fprintf(stream,
            "usage:\n"
            "  tca-flat-field calibrate (--mode 0|2 | --width W --height H)\\\n\n"
            "      --phase rggb|grbg|gbrg|bggr --dark DARK_STREAM --dark-frames N\\\n\n"
            "      --flat FLAT_STREAM --flat-frames N --output CALIBRATION\\\n\n"
            "      [--min-signal 8] [--max-gain 8]\n"
            "  tca-flat-field apply --calibration CALIBRATION\\\n\n"
            "      [--input BAYER_STREAM|-] [--output BAYER_STREAM|-]\n"
            "  tca-flat-field inspect --calibration CALIBRATION\n");
}

static int parse_u32(const char *text, uint32_t *value)
{
    char *end = NULL;
    unsigned long parsed;

    if (text == NULL || text[0] == 0 || text[0] == '-') {
        return -1;
    }
    errno = 0;
    parsed = strtoul(text, &end, 10);
    if (errno != 0 || end == text || *end != 0 || parsed > UINT32_MAX) {
        return -1;
    }
    *value = (uint32_t)parsed;
    return 0;
}

static int checked_pixels(struct geometry geometry, size_t *pixels)
{
    if (geometry.width == 0 || geometry.height == 0 ||
        (size_t)geometry.width > SIZE_MAX / (size_t)geometry.height) {
        return -1;
    }
    *pixels = (size_t)geometry.width * (size_t)geometry.height;
    return *pixels == 0 ? -1 : 0;
}

static void put_u16_le(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)(value & 0xffu);
    destination[1] = (uint8_t)((value >> 8u) & 0xffu);
}

static uint32_t get_u16_le(const uint8_t *source)
{
    return (uint32_t)source[0] | ((uint32_t)source[1] << 8u);
}

static void put_u32_le(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)(value & 0xffu);
    destination[1] = (uint8_t)((value >> 8u) & 0xffu);
    destination[2] = (uint8_t)((value >> 16u) & 0xffu);
    destination[3] = (uint8_t)((value >> 24u) & 0xffu);
}

static uint32_t get_u32_le(const uint8_t *source)
{
    return (uint32_t)source[0] |
           ((uint32_t)source[1] << 8u) |
           ((uint32_t)source[2] << 16u) |
           ((uint32_t)source[3] << 24u);
}

static int write_all(FILE *stream, const void *buffer, size_t length)
{
    const uint8_t *position = buffer;
    size_t remaining = length;

    while (remaining != 0) {
        size_t written = fwrite(position, 1, remaining, stream);
        if (written == 0) {
            return -1;
        }
        position += written;
        remaining -= written;
    }
    return 0;
}

static int read_exact(FILE *stream, void *buffer, size_t length, int allow_eof)
{
    uint8_t *position = buffer;
    size_t received = 0;

    while (received != length) {
        size_t result = fread(position + received, 1, length - received, stream);
        if (result == 0) {
            if (ferror(stream)) {
                return -1;
            }
            if (allow_eof && received == 0 && feof(stream)) {
                return 0;
            }
            return -2;
        }
        received += result;
    }
    return 1;
}

static FILE *open_input(const char *path)
{
    FILE *stream;

    if (strcmp(path, "-") == 0) {
        return stdin;
    }
    stream = fopen(path, "rb");
    if (stream == NULL) {
        fprintf(stderr, "cannot open input %s: %s\n", path, strerror(errno));
    }
    return stream;
}

static FILE *open_new_output(const char *path)
{
    int descriptor;
    FILE *stream;

    if (strcmp(path, "-") == 0) {
        return stdout;
    }
    descriptor = open(path, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (descriptor < 0) {
        fprintf(stderr, "cannot create output %s: %s\n", path, strerror(errno));
        return NULL;
    }
    stream = fdopen(descriptor, "wb");
    if (stream == NULL) {
        fprintf(stderr, "cannot attach output %s: %s\n", path, strerror(errno));
        close(descriptor);
        return NULL;
    }
    return stream;
}

static int close_if_file(FILE *stream, FILE *standard)
{
    if (stream == NULL || stream == standard) {
        return 0;
    }
    return fclose(stream);
}

static int phase_code(const char *name, uint32_t *code)
{
    static const char *names[] = {"rggb", "grbg", "gbrg", "bggr"};
    size_t index;

    for (index = 0; index < sizeof(names) / sizeof(names[0]); ++index) {
        if (strcmp(name, names[index]) == 0) {
            *code = (uint32_t)index;
            return 0;
        }
    }
    return -1;
}

static const char *phase_name(uint32_t code)
{
    static const char *names[] = {"rggb", "grbg", "gbrg", "bggr"};
    return code < 4u ? names[code] : "invalid";
}

static uint32_t pixel_channel(uint32_t phase, uint32_t x, uint32_t y)
{
    static const uint8_t channels[4][2][2] = {
        {{0, 1}, {2, 3}},
        {{1, 0}, {3, 2}},
        {{1, 3}, {0, 2}},
        {{3, 1}, {2, 0}},
    };
    return channels[phase][y & 1u][x & 1u];
}

static int accumulate_stream(const char *path, uint32_t frames, size_t pixels,
                             uint64_t *sums)
{
    FILE *stream = open_input(path);
    uint8_t *frame;
    uint32_t frame_index;
    int status = -1;

    if (stream == NULL) {
        return -1;
    }
    frame = malloc(pixels);
    if (frame == NULL) {
        fprintf(stderr, "cannot allocate %zu-byte calibration frame\n", pixels);
        goto done;
    }
    for (frame_index = 0; frame_index < frames; ++frame_index) {
        size_t pixel;
        int result = read_exact(stream, frame, pixels, 0);
        if (result != 1) {
            fprintf(stderr, "%s ended during calibration frame %u of %u\n",
                    path, frame_index + 1u, frames);
            free(frame);
            goto done;
        }
        for (pixel = 0; pixel < pixels; ++pixel) {
            sums[pixel] += frame[pixel];
        }
    }
    {
        uint8_t extra;
        if (fread(&extra, 1, 1, stream) != 0) {
            fprintf(stderr, "%s contains bytes beyond %u frames\n", path, frames);
            free(frame);
            goto done;
        }
        if (ferror(stream)) {
            fprintf(stderr, "error checking %s: %s\n", path, strerror(errno));
            free(frame);
            goto done;
        }
    }
    free(frame);
    status = 0;

done:
    if (close_if_file(stream, stdin) != 0) {
        fprintf(stderr, "error closing %s: %s\n", path, strerror(errno));
        status = -1;
    }
    return status;
}

static uint32_t histogram_median(const uint64_t *histogram, uint64_t count)
{
    uint64_t target = (count - 1u) / 2u;
    uint64_t cumulative = 0;
    uint32_t value;

    for (value = 0; value < TCFF_HISTOGRAM_BINS; ++value) {
        cumulative += histogram[value];
        if (cumulative > target) {
            return value;
        }
    }
    return TCFF_HISTOGRAM_BINS - 1u;
}

static int write_header(FILE *stream, const struct calibration_header *header)
{
    uint8_t bytes[TCFF_HEADER_BYTES] = {0};
    uint32_t channel;

    memcpy(bytes, tcff_magic, sizeof(tcff_magic));
    put_u32_le(bytes + 8, TCFF_VERSION);
    put_u32_le(bytes + 12, TCFF_HEADER_BYTES);
    put_u32_le(bytes + 16, header->width);
    put_u32_le(bytes + 20, header->height);
    put_u32_le(bytes + 24, header->phase);
    put_u32_le(bytes + 28, header->dark_frames);
    put_u32_le(bytes + 32, header->flat_frames);
    put_u32_le(bytes + 36, header->min_signal_q8);
    put_u32_le(bytes + 40, header->max_gain_q8);
    for (channel = 0; channel < 4u; ++channel) {
        put_u32_le(bytes + 44u + channel * 4u,
                   header->references_q8[channel]);
    }
    return write_all(stream, bytes, sizeof(bytes));
}

static int read_calibration(const char *path, struct calibration_header *header,
                            uint8_t **records, size_t *pixels)
{
    FILE *stream = open_input(path);
    uint8_t bytes[TCFF_HEADER_BYTES];
    size_t record_bytes;
    uint8_t extra;
    int result = -1;
    uint32_t channel;

    if (stream == NULL) {
        return -1;
    }
    if (read_exact(stream, bytes, sizeof(bytes), 0) != 1) {
        fprintf(stderr, "calibration header is truncated: %s\n", path);
        goto done;
    }
    if (memcmp(bytes, tcff_magic, sizeof(tcff_magic)) != 0 ||
        get_u32_le(bytes + 8) != TCFF_VERSION ||
        get_u32_le(bytes + 12) != TCFF_HEADER_BYTES) {
        fprintf(stderr, "unsupported calibration format: %s\n", path);
        goto done;
    }
    header->width = get_u32_le(bytes + 16);
    header->height = get_u32_le(bytes + 20);
    header->phase = get_u32_le(bytes + 24);
    header->dark_frames = get_u32_le(bytes + 28);
    header->flat_frames = get_u32_le(bytes + 32);
    header->min_signal_q8 = get_u32_le(bytes + 36);
    header->max_gain_q8 = get_u32_le(bytes + 40);
    for (channel = 0; channel < 4u; ++channel) {
        header->references_q8[channel] = get_u32_le(bytes + 44u + channel * 4u);
    }
    if (header->phase >= 4u ||
        checked_pixels((struct geometry){header->width, header->height},
                       pixels) != 0 ||
        *pixels > SIZE_MAX / TCFF_RECORD_BYTES) {
        fprintf(stderr, "invalid calibration geometry or Bayer phase: %s\n", path);
        goto done;
    }
    record_bytes = *pixels * TCFF_RECORD_BYTES;
    *records = malloc(record_bytes);
    if (*records == NULL) {
        fprintf(stderr, "cannot allocate %zu-byte calibration map\n", record_bytes);
        goto done;
    }
    if (read_exact(stream, *records, record_bytes, 0) != 1) {
        fprintf(stderr, "calibration map is truncated: %s\n", path);
        free(*records);
        *records = NULL;
        goto done;
    }
    if (fread(&extra, 1, 1, stream) != 0) {
        fprintf(stderr, "calibration contains trailing bytes: %s\n", path);
        free(*records);
        *records = NULL;
        goto done;
    }
    result = 0;

done:
    if (close_if_file(stream, stdin) != 0) {
        fprintf(stderr, "error closing %s: %s\n", path, strerror(errno));
        result = -1;
    }
    return result;
}

static int command_calibrate(int argc, char **argv)
{
    struct geometry geometry = {0, 0};
    const char *dark_path = NULL;
    const char *flat_path = NULL;
    const char *output_path = NULL;
    uint32_t dark_frames = 0;
    uint32_t flat_frames = 0;
    uint32_t phase = UINT32_MAX;
    uint32_t mode = UINT32_MAX;
    uint32_t min_signal = 8u;
    uint32_t max_gain = 8u;
    uint64_t *sums = NULL;
    uint16_t *dark_q8 = NULL;
    uint64_t *histograms = NULL;
    uint64_t counts[4] = {0, 0, 0, 0};
    uint64_t invalid[4] = {0, 0, 0, 0};
    uint32_t references[4];
    size_t pixels;
    size_t pixel;
    FILE *output = NULL;
    int index;
    int status = 1;

    for (index = 2; index < argc; ++index) {
        const char *option = argv[index];
        const char *value;
        if (index + 1 >= argc) {
            fprintf(stderr, "missing value after %s\n", option);
            return 64;
        }
        value = argv[++index];
        if (strcmp(option, "--mode") == 0) {
            if (parse_u32(value, &mode) != 0 || (mode != 0u && mode != 2u)) {
                fprintf(stderr, "--mode must be 0 or 2\n");
                return 64;
            }
        } else if (strcmp(option, "--width") == 0) {
            if (parse_u32(value, &geometry.width) != 0) return 64;
        } else if (strcmp(option, "--height") == 0) {
            if (parse_u32(value, &geometry.height) != 0) return 64;
        } else if (strcmp(option, "--phase") == 0) {
            if (phase_code(value, &phase) != 0) {
                fprintf(stderr, "unknown Bayer phase: %s\n", value);
                return 64;
            }
        } else if (strcmp(option, "--dark") == 0) {
            dark_path = value;
        } else if (strcmp(option, "--dark-frames") == 0) {
            if (parse_u32(value, &dark_frames) != 0) return 64;
        } else if (strcmp(option, "--flat") == 0) {
            flat_path = value;
        } else if (strcmp(option, "--flat-frames") == 0) {
            if (parse_u32(value, &flat_frames) != 0) return 64;
        } else if (strcmp(option, "--output") == 0) {
            output_path = value;
        } else if (strcmp(option, "--min-signal") == 0) {
            if (parse_u32(value, &min_signal) != 0 || min_signal > 255u) return 64;
        } else if (strcmp(option, "--max-gain") == 0) {
            if (parse_u32(value, &max_gain) != 0 || max_gain > 255u) return 64;
        } else {
            fprintf(stderr, "unknown calibrate option: %s\n", option);
            return 64;
        }
    }
    if (mode != UINT32_MAX) {
        if (geometry.width != 0 || geometry.height != 0) {
            fprintf(stderr, "use either --mode or --width/--height\n");
            return 64;
        }
        geometry = mode == 0u ? (struct geometry){3664u, 2748u}
                              : (struct geometry){1280u, 960u};
    }
    if (checked_pixels(geometry, &pixels) != 0 || phase >= 4u ||
        dark_path == NULL || flat_path == NULL || output_path == NULL ||
        dark_frames == 0 || flat_frames == 0 || min_signal == 0 ||
        max_gain == 0 || strcmp(output_path, "-") == 0) {
        usage(stderr);
        return 64;
    }
    if (strcmp(dark_path, "-") == 0 && strcmp(flat_path, "-") == 0) {
        fprintf(stderr, "dark and flat streams cannot both be standard input\n");
        return 64;
    }
    sums = calloc(pixels, sizeof(*sums));
    dark_q8 = malloc(pixels * sizeof(*dark_q8));
    histograms = calloc(4u * TCFF_HISTOGRAM_BINS, sizeof(*histograms));
    if (sums == NULL || dark_q8 == NULL || histograms == NULL) {
        fprintf(stderr, "cannot allocate calibration workspace for %zu pixels\n",
                pixels);
        goto done;
    }
    if (accumulate_stream(dark_path, dark_frames, pixels, sums) != 0) goto done;
    for (pixel = 0; pixel < pixels; ++pixel) {
        uint64_t value = (sums[pixel] * 256u + dark_frames / 2u) / dark_frames;
        dark_q8[pixel] = (uint16_t)(value > 65535u ? 65535u : value);
    }
    memset(sums, 0, pixels * sizeof(*sums));
    if (accumulate_stream(flat_path, flat_frames, pixels, sums) != 0) goto done;
    for (pixel = 0; pixel < pixels; ++pixel) {
        uint32_t x = (uint32_t)(pixel % geometry.width);
        uint32_t y = (uint32_t)(pixel / geometry.width);
        uint32_t channel = pixel_channel(phase, x, y);
        uint64_t flat = (sums[pixel] * 256u + flat_frames / 2u) / flat_frames;
        uint32_t signal = flat > dark_q8[pixel]
                        ? (uint32_t)(flat - dark_q8[pixel]) : 0u;
        if (signal >= min_signal * 256u && signal < TCFF_HISTOGRAM_BINS) {
            histograms[channel * TCFF_HISTOGRAM_BINS + signal]++;
            counts[channel]++;
        } else {
            invalid[channel]++;
        }
    }
    for (uint32_t channel = 0; channel < 4u; ++channel) {
        if (counts[channel] == 0) {
            fprintf(stderr, "no valid flat pixels for Bayer channel %u\n", channel);
            goto done;
        }
        references[channel] = histogram_median(
            histograms + channel * TCFF_HISTOGRAM_BINS, counts[channel]);
    }
    output = open_new_output(output_path);
    if (output == NULL) goto done;
    {
        struct calibration_header header = {
            geometry.width, geometry.height, phase, dark_frames, flat_frames,
            min_signal * 256u, max_gain * 256u,
            {references[0], references[1], references[2], references[3]}
        };
        if (write_header(output, &header) != 0) goto write_failed;
    }
    for (pixel = 0; pixel < pixels; ++pixel) {
        uint32_t x = (uint32_t)(pixel % geometry.width);
        uint32_t y = (uint32_t)(pixel / geometry.width);
        uint32_t channel = pixel_channel(phase, x, y);
        uint64_t flat = (sums[pixel] * 256u + flat_frames / 2u) / flat_frames;
        uint32_t signal = flat > dark_q8[pixel]
                        ? (uint32_t)(flat - dark_q8[pixel]) : 0u;
        uint32_t gain = 0;
        uint8_t record[TCFF_RECORD_BYTES];
        if (signal >= min_signal * 256u) {
            uint64_t scaled = (uint64_t)references[channel] * 256u;
            gain = (uint32_t)((scaled + signal / 2u) / signal);
            if (gain > max_gain * 256u) gain = max_gain * 256u;
            if (gain > 65535u) gain = 65535u;
        }
        put_u16_le(record, dark_q8[pixel]);
        put_u16_le(record + 2, gain);
        if (write_all(output, record, sizeof(record)) != 0) goto write_failed;
    }
    if (fflush(output) != 0 || fclose(output) != 0) {
        output = NULL;
        fprintf(stderr, "cannot finish calibration %s: %s\n",
                output_path, strerror(errno));
        goto done;
    }
    output = NULL;
    fprintf(stderr,
            "calibration=%s geometry=%ux%u phase=%s dark_frames=%u "
            "flat_frames=%u references_q8=%u,%u,%u,%u "
            "invalid_pixels=%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
            " status=ok\n",
            output_path, geometry.width, geometry.height, phase_name(phase),
            dark_frames, flat_frames, references[0], references[1],
            references[2], references[3], invalid[0], invalid[1],
            invalid[2], invalid[3]);
    status = 0;
    goto done;

write_failed:
    fprintf(stderr, "cannot write calibration %s: %s\n",
            output_path, strerror(errno));

done:
    if (output != NULL) {
        fclose(output);
        unlink(output_path);
    }
    free(histograms);
    free(dark_q8);
    free(sums);
    return status;
}

static int command_apply(int argc, char **argv)
{
    const char *calibration_path = NULL;
    const char *input_path = "-";
    const char *output_path = "-";
    struct calibration_header header;
    uint8_t *records = NULL;
    uint8_t *frame = NULL;
    size_t pixels = 0;
    FILE *input = NULL;
    FILE *output = NULL;
    uint64_t frames = 0;
    int index;
    int status = 1;

    for (index = 2; index < argc; ++index) {
        const char *option = argv[index];
        const char *value;
        if (index + 1 >= argc) return 64;
        value = argv[++index];
        if (strcmp(option, "--calibration") == 0) calibration_path = value;
        else if (strcmp(option, "--input") == 0) input_path = value;
        else if (strcmp(option, "--output") == 0) output_path = value;
        else {
            fprintf(stderr, "unknown apply option: %s\n", option);
            return 64;
        }
    }
    if (calibration_path == NULL ||
        (strcmp(input_path, "-") == 0 && strcmp(calibration_path, "-") == 0)) {
        usage(stderr);
        return 64;
    }
    if (read_calibration(calibration_path, &header, &records, &pixels) != 0) {
        return 1;
    }
    frame = malloc(pixels);
    if (frame == NULL) {
        fprintf(stderr, "cannot allocate %zu-byte Bayer frame\n", pixels);
        goto done;
    }
    input = open_input(input_path);
    if (input == NULL) goto done;
    output = open_new_output(output_path);
    if (output == NULL) goto done;
    for (;;) {
        int read_result = read_exact(input, frame, pixels, 1);
        if (read_result == 0) break;
        if (read_result == -1) {
            fprintf(stderr, "error reading Bayer stream %s: %s\n",
                    input_path, strerror(errno));
            goto done;
        }
        if (read_result == -2) {
            fprintf(stderr, "truncated Bayer frame after %" PRIu64 " complete frames\n",
                    frames);
            goto done;
        }
        for (size_t pixel = 0; pixel < pixels; ++pixel) {
            const uint8_t *record = records + pixel * TCFF_RECORD_BYTES;
            int32_t signal_q8 = (int32_t)frame[pixel] * 256 -
                                (int32_t)get_u16_le(record);
            uint32_t gain_q8 = get_u16_le(record + 2);
            uint64_t corrected;
            if (signal_q8 <= 0 || gain_q8 == 0) {
                frame[pixel] = 0;
                continue;
            }
            corrected = ((uint64_t)(uint32_t)signal_q8 * gain_q8 + 32768u) /
                        65536u;
            frame[pixel] = (uint8_t)(corrected > 255u ? 255u : corrected);
        }
        if (write_all(output, frame, pixels) != 0) {
            fprintf(stderr, "error writing Bayer stream %s: %s\n",
                    output_path, strerror(errno));
            goto done;
        }
        frames++;
    }
    if (fflush(output) != 0) {
        fprintf(stderr, "error flushing Bayer stream %s: %s\n",
                output_path, strerror(errno));
        goto done;
    }
    fprintf(stderr, "frames=%" PRIu64 " geometry=%ux%u phase=%s status=ok\n",
            frames, header.width, header.height, phase_name(header.phase));
    status = 0;

done:
    if (close_if_file(output, stdout) != 0) status = 1;
    if (close_if_file(input, stdin) != 0) status = 1;
    if (status != 0 && output != NULL && output != stdout) unlink(output_path);
    free(frame);
    free(records);
    return status;
}

static int command_inspect(int argc, char **argv)
{
    const char *calibration_path = NULL;
    struct calibration_header header;
    uint8_t *records = NULL;
    size_t pixels = 0;
    int index;

    for (index = 2; index < argc; ++index) {
        if (strcmp(argv[index], "--calibration") != 0 || index + 1 >= argc) {
            usage(stderr);
            return 64;
        }
        calibration_path = argv[++index];
    }
    if (calibration_path == NULL ||
        read_calibration(calibration_path, &header, &records, &pixels) != 0) {
        return calibration_path == NULL ? 64 : 1;
    }
    printf("{\n"
           "  \"format\": \"tcaff01\",\n"
           "  \"width\": %u,\n"
           "  \"height\": %u,\n"
           "  \"phase\": \"%s\",\n"
           "  \"pixels\": %zu,\n"
           "  \"dark_frames\": %u,\n"
           "  \"flat_frames\": %u,\n"
           "  \"min_signal\": %.6f,\n"
           "  \"max_gain\": %.6f,\n"
           "  \"references\": {\"r\": %.6f, \"g1\": %.6f, "
           "\"g2\": %.6f, \"b\": %.6f}\n"
           "}\n",
           header.width, header.height, phase_name(header.phase), pixels,
           header.dark_frames, header.flat_frames,
           header.min_signal_q8 / 256.0, header.max_gain_q8 / 256.0,
           header.references_q8[0] / 256.0,
           header.references_q8[1] / 256.0,
           header.references_q8[2] / 256.0,
           header.references_q8[3] / 256.0);
    free(records);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2 || strcmp(argv[1], "--help") == 0) {
        usage(argc < 2 ? stderr : stdout);
        return argc < 2 ? 64 : 0;
    }
    if (strcmp(argv[1], "--version") == 0) {
        puts("tca-flat-field 0.1.0");
        return 0;
    }
    if (strcmp(argv[1], "calibrate") == 0) return command_calibrate(argc, argv);
    if (strcmp(argv[1], "apply") == 0) return command_apply(argc, argv);
    if (strcmp(argv[1], "inspect") == 0) return command_inspect(argc, argv);
    usage(stderr);
    return 64;
}
