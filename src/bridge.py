"""Core CLI bridge: spawn Claude subprocess, stream output, buffer tokens."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from src.session import Session

logger = logging.getLogger(__name__)


async def run_prompt(
    prompt: str, session: Session
) -> AsyncGenerator[str, None]:
    """Spawn Claude CLI and yield text chunks as they arrive.

    The caller is responsible for calling session.complete_execution()
    after this generator is exhausted.
    """
    cmd = [
        "claude",
        "-p",
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
        prompt,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=1024 * 1024,  # 1MB line buffer for large stream-json events
        )
    except FileNotFoundError:
        session.complete_execution(127)
        raise RuntimeError("Claude CLI not found. Ensure 'claude' is in your PATH.")

    session.current_process = process

    accumulated = ""

    try:
        async for chunk in _parse_stream(process.stdout):
            # stream-json gives us the full message content so far,
            # yield only the new part
            if len(chunk) > len(accumulated):
                delta = chunk[len(accumulated):]
                accumulated = chunk
                yield delta
            elif chunk != accumulated:
                # Different content entirely (shouldn't happen normally)
                accumulated = chunk
                yield chunk

        # Wait for process to finish
        await process.wait()
        exit_code = process.returncode or 0

        if session.current_execution:
            session.current_execution.exit_code = exit_code

    except asyncio.CancelledError:
        process.terminate()
        await process.wait()
        session.complete_execution(1)
        raise
    except Exception:
        try:
            process.terminate()
            await process.wait()
        except ProcessLookupError:
            pass
        session.complete_execution(1)
        raise


async def _parse_stream(
    stdout: asyncio.StreamReader,
) -> AsyncGenerator[str, None]:
    """Parse stream-json lines from Claude CLI stdout, yield accumulated text."""
    async for raw_line in stdout:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("Non-JSON line from CLI: %s", line)
            continue

        text = _extract_text(event)
        if text is not None:
            yield text


def _extract_text(event: dict) -> str | None:
    """Extract text content from a stream-json event."""
    # assistant message with content blocks
    if event.get("type") == "assistant":
        content = event.get("message", {}).get("content", [])
        parts = []
        for block in content:
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        if parts:
            return "".join(parts)

    # content_block_delta
    if event.get("type") == "content_block_delta":
        delta = event.get("delta", {})
        if delta.get("type") == "text_delta":
            return delta.get("text")

    # result event at the end — "result" is a plain string
    if event.get("type") == "result":
        result = event.get("result")
        if isinstance(result, str) and result:
            return result

    return None
