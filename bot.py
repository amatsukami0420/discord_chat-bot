import os
import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='chat')
async def chat(ctx, *, message):
    try:
        # Generate response using Gemini
        response = model.generate_content(message)
        
        # Split response into chunks if it's too long
        if len(response.text) > 2000:
            chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f"Error: {str(error)}")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
