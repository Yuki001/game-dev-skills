#!/usr/bin/env sh
set -eu

if command -v magick >/dev/null 2>&1; then
  command -v magick
  exit 0
fi

for candidate in \
  /usr/local/bin/magick \
  /opt/homebrew/bin/magick \
  /opt/local/bin/magick \
  /snap/bin/magick
do
  if [ -x "$candidate" ]; then
    printf '%s\n' "$candidate"
    exit 0
  fi
done

printf '%s\n' 'ImageMagick 7 executable not found on PATH or in common installation locations.' >&2
exit 1
