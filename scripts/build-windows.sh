\
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$ROOT/UPSTREAM_VERSION")"
TAG="$(tr -d '\r\n' < "$ROOT/UPSTREAM_TAG")"

: "${TARGET_NAME:?TARGET_NAME must be set}"
: "${HOST_TRIPLET:?HOST_TRIPLET must be set}"

WORK="$ROOT/build/$TARGET_NAME"
SRC="$WORK/cdrdao"
PREFIX="$WORK/install"
STAGE="$ROOT/stage/$TARGET_NAME"

rm -rf "$WORK" "$STAGE"
mkdir -p "$WORK" "$STAGE"

git clone --depth 1 --branch "$TAG" https://github.com/cdrdao/cdrdao.git "$SRC"

cd "$SRC"

python "$ROOT/scripts/apply-windows-portability.py" "$SRC"

if [[ ! -f configure ]]; then
    ./autogen.sh
fi

./configure \
    --host="$HOST_TRIPLET" \
    --prefix="$PREFIX" \
    --without-gcdmaster \
    --without-ogg-support \
    --without-mp3-support \
    --without-flac-support

make -j"${NUMBER_OF_PROCESSORS:-2}"
make install

mkdir -p "$STAGE/bin" "$STAGE/licenses"

for tool in cdrdao toc2cue cue2toc; do
    exe="$PREFIX/bin/$tool.exe"
    if [[ ! -f "$exe" ]]; then
        echo "Expected tool not found: $exe" >&2
        exit 1
    fi
    cp "$exe" "$STAGE/bin/"
done

# Copy MinGW/LLVM runtime DLLs needed by the three executables.
# Windows system DLLs are intentionally not bundled.
copy_runtime_dlls() {
    local exe="$1"
    ldd "$exe" 2>/dev/null \
      | awk '/=> \// {print $3} /^[[:space:]]*\/.*\.dll/ {print $1}' \
      | while read -r dll; do
            [[ -f "$dll" ]] || continue
            case "$dll" in
                /c/Windows/*|/C/Windows/*) continue ;;
            esac
            cp -n "$dll" "$STAGE/bin/" || true
        done
}

copy_runtime_dlls "$STAGE/bin/cdrdao.exe"
copy_runtime_dlls "$STAGE/bin/toc2cue.exe"
copy_runtime_dlls "$STAGE/bin/cue2toc.exe"

cp "$SRC/COPYING" "$STAGE/licenses/cdrdao-COPYING"
cp "$SRC/AUTHORS" "$STAGE/licenses/cdrdao-AUTHORS"
cp "$SRC/README.md" "$STAGE/licenses/cdrdao-README.md"
printf '%s\n' "$VERSION" > "$STAGE/VERSION"

# Native smoke test. The ARM64 workflow runs on a native Windows ARM64 runner.
"$STAGE/bin/cdrdao.exe" version >/dev/null 2>&1 || "$STAGE/bin/cdrdao.exe" --version >/dev/null 2>&1

echo "Built $TARGET_NAME cdrdao $VERSION"
