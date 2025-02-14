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

## Usage

- Use `!chat <message>` to interact with the Gemini AI
- The bot will respond with AI-generated content

## Requirements
- Python 3.7+
- Discord.py
- Google Generative AI library
- python-dotenv
