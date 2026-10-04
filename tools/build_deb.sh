#!/bin/sh

# Build an architecture-native Debian binary package without root access.
# This stages only independently developed public files and never opens USB.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(CDPATH= cd -- "$script_dir/.." && pwd)
metadata_dir=$project_dir/packaging/debian
output_argument=${1:-$project_dir/dist}

for command_name in dpkg dpkg-deb du find install make sha256sum touch; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "required command not found: $command_name" >&2
        exit 69
    fi
done

version=${TCA_PACKAGE_VERSION:-$(sed -n '1p' "$metadata_dir/version")}
epoch=${SOURCE_DATE_EPOCH:-$(sed -n '1p' "$metadata_dir/source-date-epoch")}

if ! dpkg --validate-version "$version" >/dev/null 2>&1; then
    echo "invalid Debian package version: $version" >&2
    exit 64
fi
case "$epoch" in
    ''|*[!0-9]*)
        echo "SOURCE_DATE_EPOCH must be a nonnegative integer" >&2
        exit 64
        ;;
esac

architecture=$(dpkg --print-architecture)
case "$architecture" in
    ''|*[!a-z0-9-]*)
        echo "unexpected Debian architecture: $architecture" >&2
        exit 65
        ;;
esac

mkdir -p "$output_argument"
output_dir=$(CDPATH= cd -- "$output_argument" && pwd)
package_path=$output_dir/tucsen-tca-camera_${version}_${architecture}.deb
if [ -e "$package_path" ]; then
    echo "refusing to overwrite existing package: $package_path" >&2
    exit 73
fi

staging_root=$(mktemp -d "${TMPDIR:-/tmp}/tucsen-tca-camera-deb.XXXXXX")
cleanup()
{
    rm -rf "$staging_root"
}
trap cleanup EXIT HUP INT TERM

make -C "$project_dir" all
make -C "$project_dir" DESTDIR="$staging_root" PREFIX=/usr install

install -D -m 0644 "$project_dir/udev/99-tucsen-tca-camera.rules" \
    "$staging_root/usr/lib/udev/rules.d/99-tucsen-tca-camera.rules"
documentation_dir=$staging_root/usr/share/doc/tucsen-tca-camera
install -d "$documentation_dir"
install -m 0644 "$project_dir/README.md" "$documentation_dir/README.md"
install -m 0644 "$project_dir/VERSION" "$documentation_dir/VERSION"
install -m 0644 "$project_dir/CHANGELOG.md" "$documentation_dir/CHANGELOG.md"
install -m 0644 "$project_dir/LICENSE" "$documentation_dir/LICENSE"
install -m 0644 "$project_dir/NOTICE" "$documentation_dir/NOTICE"
install -m 0644 "$project_dir/docs/protocol.md" "$documentation_dir/protocol.md"
install -m 0644 "$project_dir/docs/validation.md" "$documentation_dir/validation.md"
install -m 0644 "$project_dir/docs/optical-validation.md" \
    "$documentation_dir/optical-validation.md"
install -m 0644 "$metadata_dir/copyright" "$documentation_dir/copyright"

install -d "$staging_root/DEBIAN"
installed_size=$(du -sk "$staging_root/usr" | awk '{print $1}')
cat >"$staging_root/DEBIAN/control" <<EOF
Package: tucsen-tca-camera
Version: $version
Section: video
Priority: optional
Architecture: $architecture
Maintainer: Bjørn Remseth <la3lma@gmail.com>
Installed-Size: $installed_size
Depends: libc6, libusb-1.0-0, python3
Recommends: ffmpeg, kmod, sudo, time, v4l-utils, v4l2loopback-dkms
Homepage: https://github.com/la3lma/tucsen-tca-camera
Description: userspace reader for the legacy Tucsen TCA microscope camera
 Captures Bayer8 preview and full-resolution frames from USB 0547:c003,
 exposes bounded exposure and gain controls, and includes optional FFmpeg and
 V4L2 application bridges. No camera-specific kernel driver is installed.
EOF
chmod 0644 "$staging_root/DEBIAN/control"
install -m 0755 "$metadata_dir/postinst" "$staging_root/DEBIAN/postinst"
install -m 0755 "$metadata_dir/postrm" "$staging_root/DEBIAN/postrm"

find "$staging_root" -exec touch -h -d "@$epoch" {} +
export SOURCE_DATE_EPOCH=$epoch
dpkg-deb --root-owner-group --build "$staging_root" "$package_path"
sha256sum "$package_path"
printf 'package=%s\n' "$package_path"
printf 'NO USB TRANSFER SENT.\n'
