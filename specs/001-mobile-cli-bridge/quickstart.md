# Quickstart: Claude Mobile Bridge

## Prerequisites

- Python 3.11+ installed
- Claude CLI installed and working (`claude -p "hello"` should respond)
- A Telegram account on your phone
- A Telegram Bot token (create one via [@BotFather](https://t.me/BotFather))

## Setup

1. **Clone and install**:
   ```bash
   cd clawFrancois
   pip install -r requirements.txt
   ```

2. **Configure the bridge**:
   ```bash
   cp config.example.json ~/.claude-bridge/config.json
   ```
   Edit `~/.claude-bridge/config.json` and set your `bot_token` from
   BotFather.

3. **Start the bridge**:
   ```bash
   python -m claude_bridge
   ```
   The bridge prints a pairing secret to the terminal:
   ```
   Bridge started. Pairing secret: a1b2c3d4
   Send "/pair a1b2c3d4" to your bot in Telegram.
   ```

4. **Pair from your phone**:
   - Open Telegram and find your bot.
   - Send: `/pair a1b2c3d4` (using the secret from step 3).
   - The bot confirms: "Paired successfully! Send any message as a
     prompt."

5. **Send a prompt**:
   - Type any message in the Telegram chat.
   - Watch the response stream in — the bot message updates
     progressively as Claude generates output.

## Verify It Works

- [ ] Bridge starts without errors
- [ ] Pairing secret is displayed in terminal
- [ ] `/pair <secret>` succeeds in Telegram
- [ ] Sending a text prompt returns streamed Claude output
- [ ] Sending `/stop` during execution cancels the CLI process
- [ ] Sending `/status` shows current bridge state
- [ ] Sending a message without pairing is rejected

## Troubleshooting

- **"Claude CLI not found"**: Ensure `claude` is in your PATH.
- **"Connection refused"**: The bridge binds to localhost by default.
  Ensure your Telegram bot can reach the internet (it communicates
  with Telegram servers, not directly with your phone).
- **Bot not responding**: Check the bot token is correct and the bridge
  process is running.
- **Flood errors**: The bridge throttles edits to 1/sec. If you still
  see errors, increase `edit_interval_ms` in config.
