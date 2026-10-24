#!/Users/darkknight/.transcribe-venv/bin/python3
"""
Whisper + Pyannote all-in-one transcription tool
Usage: transcribe yourfile.mp4
"""

import sys
import os
from pathlib import Path
from datetime import timedelta


def format_time(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_hf_token():
    token = os.environ.get('HF_TOKEN')
    if token:
        return token

    token_file = Path.home() / '.hf_token'
    if token_file.exists():
        return token_file.read_text().strip()

    print("\n⚠️  First time setup: You need a HuggingFace token for speaker diarization.")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Create a new token (read access is fine)")
    print("3. Paste it here:")
    token = input().strip()

    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)

    token_file.write_text(token)
    print(f"✓ Token saved to {token_file}. You won't need to paste it again.")
    return token


def transcribe_with_speakers(file_path):
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"\n📹 Transcribing: {file_path.name}")
    print("This may take a while depending on file length...\n")

    hf_token = get_hf_token()

    # Step 1: Speaker diarization
    print("🎤 Identifying speakers...")
    try:
        from pyannote.audio import Pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token
        )
        result = pipeline(str(file_path))
        annotation = result.diarization if hasattr(result, 'diarization') else result
    except Exception as e:
        print(f"❌ Diarization error: {e}")
        sys.exit(1)

    speaker_segments = [
        (turn.start, turn.end, speaker)
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]

    # Step 2: Transcribe with Whisper
    print("🎙️  Transcribing audio...")
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(str(file_path))
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        sys.exit(1)

    # Step 3: Merge
    print("🔗 Merging speaker info with transcript...")

    def get_speaker(time):
        for start, end, speaker in speaker_segments:
            if start <= time < end:
                return speaker
        return "Unknown"

    transcript_lines = [
        f"TRANSCRIPT: {file_path.name}\n",
        "=" * 60 + "\n",
    ]

    for segment in result.get('segments', []):
        text = segment['text'].strip()
        if not text:
            continue
        timestamp = format_time(segment['start'])
        speaker = get_speaker(segment['start'])
        transcript_lines.append(f"[{timestamp}] {speaker}: {text}\n")

    output_file = file_path.with_suffix('.txt')
    with open(output_file, 'w') as f:
        f.writelines(transcript_lines)

    print(f"\n✅ Done! Transcript saved to: {output_file}\n")

    print("Preview:")
    print("=" * 60)
    for line in transcript_lines[:20]:
        print(line.rstrip())
    if len(transcript_lines) > 20:
        print(f"\n... ({len(transcript_lines) - 20} more lines)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: transcribe yourfile.mp4")
        sys.exit(1)

    transcribe_with_speakers(sys.argv[1])
