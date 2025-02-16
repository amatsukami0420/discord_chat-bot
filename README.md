# Discord AI Assistant Bot

A Discord bot powered by Google's Gemini AI that provides chat capabilities with multiple personas and command functionalities.

## Features

- 🤖 AI-powered conversations using Gemini Pro
- 🎭 Multiple personas with unique personalities
- 💬 Channel-specific chat sessions
- ⌨️ Support for both slash commands and prefix commands
- 🔧 Comprehensive help system with categories

## Available Personas

- 🤓 **Sheldon**: A witty and sarcastic physicist
- 😎 **Jeremiah**: Street-smart tech entrepreneur
- 🌸 **Hanabi**: Anime-loving Japanese student
- 🙏 **Ashok**: Knowledgeable Indian electrician

## Commands

### 🔧 Basic Commands
- `/help` or `!help`: Show all commands or get help for a specific command
- `/chat` or `!chat`: Enable or disable AI chat in the current channel

### 🤖 AI Commands
- `/ask` or `!ask`: Ask the AI a specific question and get a response
- `/imagine` or `!imagine`: Get an AI-generated description of an imagined scene

### 🎭 Persona System
- `/persona` or `!persona`: List available personas or change the AI's personality

## Setup

1. Clone this repository
2. Install required dependencies:
```bash
pip install discord.py google-generativeai python-dotenv
```

3. Create a `.env` file with your tokens:
```
DISCORD_TOKEN=your_discord_token
GEMINI_API_KEY=your_gemini_api_key
```

4. Run the bot:
```bash
python bot.py
```

## Configuration

The bot uses the following default settings:
- Command prefix: `!`
- Default system prompt: "You are a helpful AI assistant."
- Message context: Maintains last 10 messages per channel
- Character limit: 2000 characters per message

## Safety Settings

The bot is configured with minimal content filtering to allow for more natural conversations. All safety categories are set to `BLOCK_NONE`:
- Harassment
- Hate Speech
- Sexually Explicit
- Dangerous Content

## Error Handling

The bot includes basic error handling for:
- Empty messages
- Message length limits
- API errors
- Response generation failures

## Contributing

Feel free to submit issues and enhancement requests!
