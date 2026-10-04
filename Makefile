CC ?= cc
CFLAGS ?= -O2
PKG_CONFIG ?= pkg-config
LIBUSB_PKG_CONFIG_PATH ?=
PREFIX ?= /usr/local
DESTDIR ?=

TARGET = build/tca-camera
FLAT_FIELD_TARGET = build/tca-flat-field
LIBUSB_PKG_CONFIG_ENV = $(if $(strip $(LIBUSB_PKG_CONFIG_PATH)),env PKG_CONFIG_PATH="$(LIBUSB_PKG_CONFIG_PATH)",)
LIBUSB_CFLAGS := $(shell $(LIBUSB_PKG_CONFIG_ENV) $(PKG_CONFIG) --cflags libusb-1.0 2>/dev/null)
LIBUSB_LIBS := $(shell $(LIBUSB_PKG_CONFIG_ENV) $(PKG_CONFIG) --libs libusb-1.0 2>/dev/null)

.PHONY: all
all: $(TARGET) $(FLAT_FIELD_TARGET)

$(TARGET): src/tca_camera.c
	@mkdir -p build
	@$(LIBUSB_PKG_CONFIG_ENV) $(PKG_CONFIG) --exists libusb-1.0 || { \
		echo "libusb-1.0 development files were not found (pkg-config)"; \
		exit 1; \
	}
	$(CC) $(CFLAGS) -std=c17 -Wall -Wextra -Werror -pedantic \
		$(LIBUSB_CFLAGS) $< $(LIBUSB_LIBS) -o $@

$(FLAT_FIELD_TARGET): src/tca_flat_field.c
	@mkdir -p build
	$(CC) $(CFLAGS) -std=c17 -Wall -Wextra -Werror -pedantic $< -o $@

.PHONY: test
test: $(TARGET) $(FLAT_FIELD_TARGET)
	python3 tests/test_static.py $(TARGET) src/tca_camera.c
	python3 tests/test_makefile_pkg_config.py .
	python3 tests/test_v4l2_static.py scripts/tca-v4l2
	python3 tests/test_ffmpeg_helper.py scripts/tca-ffmpeg
	python3 tests/test_frame_stats.py scripts/tca-frame-stats
	python3 tests/test_timing_stats.py scripts/tca-timing-stats
	python3 tests/test_white_balance.py scripts/tca-white-balance
	python3 tests/test_flat_field.py $(FLAT_FIELD_TARGET)
	python3 tests/test_flat_field_v4l2_static.py tools/run_flat_field_v4l2_preflight.sh
	python3 tests/test_flat_field_capture_session.py \
		tools/run_flat_field_capture_session.sh $(FLAT_FIELD_TARGET) scripts/tca-frame-stats
	python3 tests/test_linux_v4l2_acceptance_static.py \
		tools/run_linux_v4l2_acceptance.sh
	python3 tests/test_fake_tca_reader.py tests/fake_tca_reader.py
	python3 tests/test_v4l2_bridge_synthetic_acceptance_static.py \
		tools/run_v4l2_bridge_synthetic_acceptance.sh
	python3 tests/test_install.py .
	python3 tests/test_publication_policy.py .
	python3 tests/test_pages_static.py .

.PHONY: install
install: $(TARGET)
	install -d "$(DESTDIR)$(PREFIX)/bin"
	install -m 0755 $(TARGET) "$(DESTDIR)$(PREFIX)/bin/tca-camera"
	install -m 0755 scripts/tca-v4l2 "$(DESTDIR)$(PREFIX)/bin/tca-v4l2"
	install -m 0755 scripts/tca-ffmpeg "$(DESTDIR)$(PREFIX)/bin/tca-ffmpeg"
	install -m 0755 scripts/tca-frame-stats "$(DESTDIR)$(PREFIX)/bin/tca-frame-stats"
	install -m 0755 scripts/tca-timing-stats "$(DESTDIR)$(PREFIX)/bin/tca-timing-stats"
	install -m 0755 scripts/tca-white-balance "$(DESTDIR)$(PREFIX)/bin/tca-white-balance"
	install -m 0755 $(FLAT_FIELD_TARGET) "$(DESTDIR)$(PREFIX)/bin/tca-flat-field"

.PHONY: uninstall
uninstall:
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-camera"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-v4l2"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-ffmpeg"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-frame-stats"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-timing-stats"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-white-balance"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-flat-field"

.PHONY: clean
clean:
	rm -rf build
