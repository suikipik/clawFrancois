"""Voice message transcription using local Whisper CLI."""

from __future__ import annotations

import asyncio
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    text: str
    language: str | None
    duration_secs: float
    success: bool
    error_message: str | None


def check_whisper_available() -> bool:
    """Check whether the Whisper CLI is installed and accessible."""
    return shutil.which("whisper") is not None


async def transcribe_audio(
    audio_path: Path,
    model: str = "base",
    timeout: int = 120,
) -> TranscriptionResult:
    """Transcribe an audio file to text using the locally-installed Whisper CLI.

    Args:
        audio_path: Path to the audio file.
        model: Whisper model size (tiny, base, small, medium, large).
        timeout: Maximum seconds to wait for transcription.

    Returns:
        TranscriptionResult with transcribed text or error details.
    """
    if not check_whisper_available():
        return TranscriptionResult(
            text="",
            language=None,
            duration_secs=0.0,
            success=False,
            error_message="Voice transcription unavailable: whisper is not installed.",
        )

    output_dir = audio_path.parent
    cmd = [
        "whisper",
        str(audio_path),
        "--model", model,
        "--output_format", "txt",
        "--output_dir", str(output_dir),
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return TranscriptionResult(
                text="",
                language=None,
                duration_secs=0.0,
                success=False,
                error_message=f"Transcription timed out after {timeout} seconds.",
            )

        if process.returncode != 0:
            error_detail = stderr.decode("utf-8", errors="replace").strip()
            logger.error("Whisper CLI failed (exit %d): %s", process.returncode, error_detail)
            return TranscriptionResult(
                text="",
                language=None,
                duration_secs=0.0,
                success=False,
                error_message="Transcription failed. Please try again.",
            )

        # Read the output .txt file produced by Whisper
        txt_path = output_dir / (audio_path.stem + ".txt")
        if not txt_path.exists():
            return TranscriptionResult(
                text="",
                language=None,
                duration_secs=0.0,
                success=False,
                error_message="Transcription produced no output file.",
            )

        text = txt_path.read_text(encoding="utf-8").strip()

        # Parse language from stderr if available (Whisper prints "Detected language: xx")
        language = None
        stderr_text = stderr.decode("utf-8", errors="replace")
        for line in stderr_text.splitlines():
            if "detected language:" in line.lower():
                language = line.split(":")[-1].strip().lower()
                break

        return TranscriptionResult(
            text=text,
            language=language,
            duration_secs=0.0,  # Duration extracted from Telegram metadata, not Whisper
            success=bool(text),
            error_message=None if text else "Could not understand the audio. Try speaking clearly or type your message instead.",
        )

    except FileNotFoundError:
        return TranscriptionResult(
            text="",
            language=None,
            duration_secs=0.0,
            success=False,
            error_message="Voice transcription unavailable: whisper is not installed.",
        )
    finally:
        # Clean up Whisper output files
        for ext in (".txt", ".vtt", ".srt", ".json", ".tsv"):
            output_file = output_dir / (audio_path.stem + ext)
            if output_file.exists():
                try:
                    output_file.unlink()
                except OSError:
                    logger.debug("Failed to clean up %s", output_file)
