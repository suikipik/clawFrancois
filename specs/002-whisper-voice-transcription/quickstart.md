# Quickstart: Voice Message Transcription

## Prerequisites

1. **Existing bridge setup** — Feature 001 (Claude Mobile Bridge) must be installed and working
2. **Whisper** — Install OpenAI Whisper locally:
   ```bash
   pip install openai-whisper
   ```
3. **ffmpeg** — Required by Whisper for audio format conversion:
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

## Verify Installation

```bash
# Check Whisper is accessible
whisper --help

# Check ffmpeg is accessible
ffmpeg -version
```

## Configuration

Add optional voice settings to your config file (`~/.claude-bridge/config.json`):

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "pairing_secret": "YOUR_SECRET",
  "whisper_model": "base",
  "max_audio_duration": 300
}
```

| Field                | Default | Description                                          |
|----------------------|---------|------------------------------------------------------|
| `whisper_model`      | `"base"`| Whisper model: tiny, base, small, medium, large      |
| `max_audio_duration` | `300`   | Max voice message duration in seconds (5 min default) |

## Usage

1. Start the bridge as usual:
   ```bash
   python -m src
   ```

2. Open Telegram and send a voice message to the bot

3. The bot will:
   - Show "Transcribing..." while processing
   - Display the transcribed text (prefixed with "Voice:")
   - Forward the transcription to Claude CLI
   - Stream the response back as usual

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Voice transcription unavailable" | Install Whisper: `pip install openai-whisper` |
| Transcription is slow | Use a smaller model: set `whisper_model` to `"tiny"` |
| Poor transcription accuracy | Use a larger model: set `whisper_model` to `"small"` or `"medium"` |
| "Voice message too long" | Keep messages under the configured `max_audio_duration` |
| "Could not understand audio" | Speak clearly in a quiet environment and retry |
