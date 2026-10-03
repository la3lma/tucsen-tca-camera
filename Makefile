CC ?= cc
CFLAGS ?= -O2
PKG_CONFIG ?= pkg-config
PREFIX ?= /usr/local
DESTDIR ?=

TARGET = build/tca-camera
LIBUSB_CFLAGS := $(shell $(PKG_CONFIG) --cflags libusb-1.0 2>/dev/null)
LIBUSB_LIBS := $(shell $(PKG_CONFIG) --libs libusb-1.0 2>/dev/null)

.PHONY: all
all: $(TARGET)

$(TARGET): src/tca_camera.c
	@mkdir -p build
	@$(PKG_CONFIG) --exists libusb-1.0 || { \
		echo "libusb-1.0 development files were not found (pkg-config)"; \
		exit 1; \
	}
	$(CC) $(CFLAGS) -std=c17 -Wall -Wextra -Werror -pedantic \
		$(LIBUSB_CFLAGS) $< $(LIBUSB_LIBS) -o $@

.PHONY: test
test: $(TARGET)
	python3 tests/test_static.py $(TARGET) src/tca_camera.c
	python3 tests/test_v4l2_static.py scripts/tca-v4l2
	python3 tests/test_frame_stats.py scripts/tca-frame-stats
	python3 tests/test_install.py .

.PHONY: install
install: $(TARGET)
	install -d "$(DESTDIR)$(PREFIX)/bin"
	install -m 0755 $(TARGET) "$(DESTDIR)$(PREFIX)/bin/tca-camera"
	install -m 0755 scripts/tca-v4l2 "$(DESTDIR)$(PREFIX)/bin/tca-v4l2"
	install -m 0755 scripts/tca-frame-stats "$(DESTDIR)$(PREFIX)/bin/tca-frame-stats"

.PHONY: uninstall
uninstall:
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-camera"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-v4l2"
	rm -f "$(DESTDIR)$(PREFIX)/bin/tca-frame-stats"

.PHONY: clean
clean:
	rm -rf build
