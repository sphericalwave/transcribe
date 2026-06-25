# All-in-One Transcription Tool Setup

This is a single command that does everything: speaker identification + transcription + timecodes.

---

## What You Need First

Make sure you have both tools installed:

```bash
brew install pipx
pipx install openai-whisper
pipx install pyannote.audio
```

---

## Setup (One Time)

1. **Download the script**
   - Save the transcribe.py file to your home directory: `~/transcribe.py`

2. **Make it executable**
   ```bash
   chmod +x ~/transcribe.py
   ```

3. **Create a shell alias** (so you can just type `transcribe filename`)
   
   Open Terminal and run:
   ```bash
   echo "alias transcribe='~/transcribe.py'" >> ~/.zshrc
   source ~/.zshrc
   ```

   (If you're on an older Mac with bash, use `~/.bash_profile` instead of `~/.zshrc`)

4. **Get a HuggingFace token** (free, takes 5 minutes)

   **a. Create an account and token**
   - Go to https://huggingface.co and sign up (free)
   - Once logged in, go to: https://huggingface.co/settings/tokens
   - Click **New token**
   - Give it any name (e.g. "transcribe")
   - Role: **Read** is sufficient
   - Click **Generate a token** and copy it somewhere safe

   **b. Accept the model license** (required — the tool won't work without this)
   - Go to: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Click **Agree and access repository**
   - Also go to: https://huggingface.co/pyannote/segmentation-3.0
   - Click **Agree and access repository** there too

   **c. First run**
   - When you run `transcribe` for the first time, it will prompt you to paste the token
   - It saves the token locally so you only need to do this once

---

## How to Use It

```bash
transcribe yourfile.mp4
```

That's it. The tool will:
1. Ask for your HuggingFace token (first time only)
2. Identify different speakers
3. Transcribe the audio
4. Merge everything together
5. Save a `.txt` file with timestamps and speaker labels

---

## Output Example

```
TRANSCRIPT: meeting.mp4
============================================================
[00:00:15] Speaker 1: "Hey, did you get the report?"
[00:00:22] Speaker 2: "Yeah, I sent it yesterday"
[00:00:30] Speaker 1: "Great, thanks"
[00:00:35] Speaker 2: "No problem, let me know if you need anything else"
```

---

## Supported Formats

Video: MP4, MOV, AVI, WebM, MKV, FLV
Audio: MP3, WAV, M4A, OGG, FLAC

---

## How Long Does It Take?

Processing time depends on file length:
- 10-minute file: ~15-20 minutes
- 1-hour file: ~1.5-2 hours
- Keep Terminal open while it runs

---

## Troubleshooting

**Q: "command not found: transcribe"**
A: The alias didn't set up right. Run this again:
```bash
echo "alias transcribe='~/transcribe.py'" >> ~/.zshrc
source ~/.zshrc
```

**Q: "pyannote-speaker-diarization: command not found"**
A: Make sure you installed it: `pipx install pyannote.audio`

**Q: It's taking forever**
A: Normal. Speaker identification is slower than transcription alone. 1 hour of audio = 1.5-2 hours of processing.

**Q: Can I close Terminal while it's running?**
A: No. Keep it open until you see "✅ Done!"

---

## Notes

- The first time you run it, you'll paste a HuggingFace token. That's normal and one-time only.
- Speaker identification works best with clearly different voices (different genders, accents).
- If voices are very similar, it might label them as the same speaker. It's not perfect, but it's good.
- The output is plain text, so you can edit it in any text editor.
