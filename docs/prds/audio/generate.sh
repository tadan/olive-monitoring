#!/usr/bin/env bash
# Generate story-style PRD audio episodes from the text scripts using macOS `say`.
#
# Usage:
#   ./generate.sh                       # default voice (Samantha), output to ./episodes
#   VOICE="Daniel" ./generate.sh        # pick another installed voice
#   RATE=180 ./generate.sh              # words per minute (default 175)
#   OUT="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OliveAudio" ./generate.sh
#                                       # write straight into iCloud Drive so it syncs to your phone
#
# List installed voices:  say -v '?'
# Better quality: System Settings > Accessibility > Spoken Content > System Voice >
#                 Manage Voices… > download an English *Premium* voice (e.g. Ava, Zoe, Evan),
#                 then run with VOICE="Ava (Premium)".

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/scripts"
OUT="${OUT:-$HERE/episodes}"
VOICE="${VOICE:-Samantha}"
RATE="${RATE:-175}"

mkdir -p "$OUT"

# Verify the chosen voice exists; fall back with a clear message.
if ! say -v '?' | grep -qiF "$VOICE"; then
  echo "WARNING: voice '$VOICE' not found. Available English voices:"
  say -v '?' | grep -iE 'en_|en-' | awk '{print "  - "$1}' | sort -u
  echo "Falling back to Samantha. Set VOICE=... to override."
  VOICE="Samantha"
fi

echo "Voice: $VOICE   Rate: $RATE wpm   Output: $OUT"
echo

count=0
for f in "$SCRIPTS"/*.txt; do
  [ -e "$f" ] || { echo "No scripts found in $SCRIPTS"; exit 1; }
  base="$(basename "$f" .txt)"
  outfile="$OUT/$base.m4a"
  echo "→ $base.m4a"
  say -v "$VOICE" -r "$RATE" -f "$f" \
      -o "$outfile" --file-format=m4af --data-format=aac
  count=$((count+1))
done

echo
echo "Done. $count episode(s) written to: $OUT"
echo "Tip: set OUT to an iCloud Drive path to auto-sync to your iPhone's Files app."
