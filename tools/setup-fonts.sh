#!/bin/sh
# Pobiera czcionki identyfikacji Avufu Event (Manrope + Playfair Display) do tools/fonts
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
npm pack @fontsource/manrope@5.1.0 @fontsource/playfair-display@5.1.0 >/dev/null
for f in *.tgz; do tar xzf "$f" && rm -rf "${f%.tgz}" && mv package "${f%.tgz}"; done
