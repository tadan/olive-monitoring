# PRD Audio Episodes

Story-style audio walkthroughs of the PRDs — for listening on a walk. One ~1.5 min episode per PRD.

## Generate / regenerate

```bash
./generate.sh
```

- Default voice **Samantha**, 175 wpm, output to `episodes/`.
- Override: `VOICE="Daniel" RATE=185 ./generate.sh`
- Write straight to your phone via iCloud Drive:
  ```bash
  OUT="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OliveAudio" ./generate.sh
  ```
  Then open the **Files** app on your iPhone → iCloud Drive → OliveAudio.

## Better voice (one-time)

The Premium voices sound far more natural than the built-ins:
System Settings → Accessibility → Spoken Content → System Voice → **Manage Voices…** →
download an English **Premium** voice (e.g. *Ava*, *Zoe*, *Evan*). Then:

```bash
VOICE="Ava (Premium)" ./generate.sh
```

## Editing the narration

The scripts in `scripts/*.txt` are the source. Edit the wording, tweak `[[slnc 400]]` pauses
(milliseconds of silence), then re-run `generate.sh`. The `.m4a` files are gitignored — they're
regenerable artifacts, not source.
