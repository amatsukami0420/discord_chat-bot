# Discord Bot with Gemini AI Integration

A Discord bot that uses Google's Gemini AI for chat interactions.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Create a `.env` file
   - Add your Discord bot token: `DISCORD_TOKEN=your_token_here`
   - Add your Gemini API key: `GEMINI_API_KEY=your_key_here`

3. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

The bot uses slash commands:

- `/enable_chat [true/false]` - Enable or disable AI chat in the current channel
- `/generate [text/image] [prompt]` - Generate content based on a prompt
- `/set_persona [persona]` - Set the AI's conversation style
  - Available personas: default, friendly, professional, casual

When chat is enabled in a channel, the bot will respond to all messages automatically.

## Requirements
- Python 3.7+
- Discord.py
- Google Generative AI library
- python-dotenv
