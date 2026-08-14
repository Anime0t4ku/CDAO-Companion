\
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

case "$TARGET_NAME" in
    windows-*)
        ARCHIVE="$DIST/cdrdao-$VERSION-$TARGET_NAME.zip"
        (
          cd "$ROOT/stage"
          python - "$TARGET_NAME" "$ARCHIVE" <<'PY'
import os, sys, zipfile
target, archive = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
    for base, _, files in os.walk(target):
        for name in files:
            path = os.path.join(base, name)
            z.write(path, os.path.relpath(path, target))
PY
        )
        ;;
    *)
        ARCHIVE="$DIST/cdrdao-$VERSION-$TARGET_NAME.tar.gz"
        tar -C "$STAGE" -czf "$ARCHIVE" .
        ;;
esac

echo "$ARCHIVE"
