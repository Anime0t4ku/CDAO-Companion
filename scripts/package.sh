#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$ROOT/UPSTREAM_VERSION")"
: "${TARGET_NAME:?TARGET_NAME must be set}"

STAGE="$ROOT/stage/$TARGET_NAME"
DIST="$ROOT/dist"
mkdir -p "$DIST"

if [[ ! -d "$STAGE" ]]; then
    echo "Stage directory missing: $STAGE" >&2
    exit 1
fi

ARCHIVE="$DIST/cdrdao-$VERSION-$TARGET_NAME.tar.gz"
tar -C "$STAGE" -czf "$ARCHIVE" .

echo "$ARCHIVE"
