#!/usr/bin/env python3
"""
Whisper + Pyannote all-in-one transcription tool
Usage: transcribe yourfile.mp4
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import timedelta


def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(int(td.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_hf_token():
    """Get HuggingFace token from environment or ask user"""
    import os
    token = os.environ.get('HF_TOKEN')
    if token:
        return token
    
    print("\n⚠️  First time setup: You need a HuggingFace token for speaker diarization.")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Create a new token (read access is fine)")
    print("3. Paste it here:")
    token = input().strip()
    
    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
    
    print("✓ Token saved. You won't need to paste it again (set HF_TOKEN env var to skip this).")
    return token


def transcribe_with_speakers(file_path):
    """Transcribe with speaker diarization and timecodes"""
    
    file_path = Path(file_path).resolve()
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"\n📹 Transcribing: {file_path.name}")
    print("This may take a while depending on file length...\n")
    
    # Get HF token
    hf_token = get_hf_token()
    
    # Step 1: Get speaker diarization
    print("🎤 Identifying speakers...")
    try:
        diarization_result = subprocess.run(
            ['pyannote-speaker-diarization', str(file_path), '--token', hf_token],
            capture_output=True,
            text=True,
            timeout=7200
        )
        if diarization_result.returncode != 0:
            print(f"❌ Speaker diarization failed: {diarization_result.stderr}")
            sys.exit(1)
        
        diarization_data = json.loads(diarization_result.stdout)
    except subprocess.TimeoutExpired:
        print("❌ Diarization timed out (file too long)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Diarization error: {e}")
        sys.exit(1)
    
    # Step 2: Transcribe with Whisper
    print("🎙️  Transcribing audio...")
    try:
        whisper_result = subprocess.run(
            ['whisper', str(file_path), '--output_format', 'json', '--quiet'],
            capture_output=True,
            text=True,
            timeout=7200
        )
        if whisper_result.returncode != 0:
            print(f"❌ Whisper transcription failed: {whisper_result.stderr}")
            sys.exit(1)
        
        whisper_data = json.loads(whisper_result.stdout)
    except subprocess.TimeoutExpired:
        print("❌ Transcription timed out (file too long)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        sys.exit(1)
    
    # Step 3: Merge speaker info with transcription
    print("🔗 Merging speaker info with transcript...")
    
    segments = whisper_data.get('segments', [])
    speakers = diarization_data.get('speakers', {})
    
    # Build output transcript
    transcript_lines = []
    transcript_lines.append(f"TRANSCRIPT: {file_path.name}\n")
    transcript_lines.append("=" * 60 + "\n")
    
    for segment in segments:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip()
        
        if not text:
            continue
        
        # Find which speaker is active at this time
        speaker_label = "Unknown"
        for spk, (spk_start, spk_end) in speakers.items():
            if spk_start <= start_time < spk_end:
                speaker_label = spk
                break
        
        timestamp = format_time(start_time)
        transcript_lines.append(f"[{timestamp}] {speaker_label}: {text}\n")
    
    # Write output
    output_file = file_path.with_suffix('.txt')
    with open(output_file, 'w') as f:
        f.writelines(transcript_lines)
    
    print(f"\n✅ Done! Transcript saved to: {output_file}\n")
    
    # Show preview
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
    
    file_path = sys.argv[1]
    transcribe_with_speakers(file_path)
