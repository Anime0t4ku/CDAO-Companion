#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$ROOT/UPSTREAM_VERSION")"
TAG="$(tr -d '\r\n' < "$ROOT/UPSTREAM_TAG")"

: "${TARGET_NAME:?TARGET_NAME must be set}"

WORK="$ROOT/build/$TARGET_NAME"
SRC="$WORK/cdrdao"
PREFIX="$WORK/install"
STAGE="$ROOT/stage/$TARGET_NAME"

rm -rf "$WORK" "$STAGE"
mkdir -p "$WORK" "$STAGE"

git clone --depth 1 --branch "$TAG" https://github.com/cdrdao/cdrdao.git "$SRC"

cd "$SRC"

# Git tags are developer checkouts, so generate configure if needed.
if [[ ! -f configure ]]; then
    ./autogen.sh
fi

# Companion only needs cdrdao, toc2cue and cue2toc.
# Avoid optional GUI/audio codec dependencies to keep packages portable.
./configure \
    --prefix="$PREFIX" \
    --without-gcdmaster \
    --without-ogg-support \
    --without-mp3-support

make -j"$(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu)"
make install

mkdir -p "$STAGE/bin" "$STAGE/licenses"

for tool in cdrdao toc2cue cue2toc; do
    if [[ ! -x "$PREFIX/bin/$tool" ]]; then
        echo "Expected tool not found: $PREFIX/bin/$tool" >&2
        exit 1
    fi
    cp "$PREFIX/bin/$tool" "$STAGE/bin/"
done

cp "$SRC/COPYING" "$STAGE/licenses/cdrdao-COPYING"
cp "$SRC/AUTHORS" "$STAGE/licenses/cdrdao-AUTHORS"
cp "$SRC/README" "$STAGE/licenses/cdrdao-README"
printf '%s\n' "$VERSION" > "$STAGE/VERSION"

# Smoke tests that do not require an optical drive.
"$STAGE/bin/cdrdao" version >/dev/null 2>&1 || "$STAGE/bin/cdrdao" --version >/dev/null 2>&1
"$STAGE/bin/toc2cue" -h >/dev/null 2>&1 || true
"$STAGE/bin/cue2toc" -h >/dev/null 2>&1 || true

echo "Built $TARGET_NAME cdrdao $VERSION"
