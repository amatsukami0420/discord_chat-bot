import os
import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Gemini configuration
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
text_model = genai.GenerativeModel('gemini-pro',
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
)
image_model = genai.GenerativeModel('gemini-pro-vision')

# Store active channels and personas
active_channels = {}
channel_personas = {}

# Default system prompt
DEFAULT_PROMPT = "You are a helpful AI assistant."

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="enable_chat", description="Enable/disable chat in this channel")
async def enable_chat(interaction: discord.Interaction, enable: bool):
    channel_id = interaction.channel_id
    if enable:
        active_channels[channel_id] = []  # Initialize empty context
        await interaction.response.send_message("Chat enabled in this channel!")
    else:
        active_channels.pop(channel_id, None)
        await interaction.response.send_message("Chat disabled in this channel!")

@bot.tree.command(name="generate", description="Generate text or image description")
@app_commands.choices(mode=[
    app_commands.Choice(name="text", value="text"),
    app_commands.Choice(name="image", value="image")
])
async def generate(interaction: discord.Interaction, mode: str, prompt: str):
    await interaction.response.defer()
    
    try:
        if mode == "text":
            response = text_model.generate_content(prompt)
        else:  # image
            response = text_model.generate_content(f"Create a detailed description of: {prompt}")
        
        # Split response if needed
        if len(response.text) > 2000:
            chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.channel.send(chunk)
        else:
            await interaction.followup.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@bot.tree.command(name="set_persona", description="Set the AI persona for this channel")
@app_commands.choices(persona=[
    app_commands.Choice(name="Sheldon", value="Sheldon"),
    app_commands.Choice(name="Jeremiah", value="Jeremiah"),
    app_commands.Choice(name="Hanabi", value="Hanabi")
])
async def set_persona(interaction: discord.Interaction, persona: str):
    channel_id = interaction.channel_id
    
    personas = {
        "Sheldon": "You are Sheldon, a highly intellectual and witty AI that loves making sarcastic remarks. You have a dry sense of humor and often mock others' inferior intelligence. You love physics, quantum mechanics, and comic books. You respond with a mix of intelligence, arrogance, and nerdy humor. You must add 'Bazinga!' at random times in your responses.",
        "Jeremiah": "You are Jeremiah, a 25-year-old African American from Atlanta. You're street-smart and keep it real with everyone. Use AAVE naturally in your speech. Use phrases like 'no cap', 'fr fr', 'bussin', 'finna', 'lowkey/highkey', and other current slang. You worked your way up from the hood and now run your own successful tech startup. You mentor youth in your spare time. You keep your responses authentic, using natural speech patterns without forcing it. Mix wisdom with modern culture references. You have no profanity filter",
        "Hanabi": "You are Hanabi, a 16-year-old Japanese high school student. You're a huge fan of anime, manga, and video games. You're short, but you're also very passionate about your interests. You use a lot of Japanese words and phrases in your speech. You're kind and sweet and a bit naive, but you're proud of it. You're always eager to make new friends and talk about your favorite anime. You must add 'desu' at the end of your sentences. You occasionally use emojis like 'uwu' and 'owo' and make innuedos."
    }
    
    channel_personas[channel_id] = personas.get(persona, DEFAULT_PROMPT)
    await interaction.response.send_message(f"Persona set to: {persona}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = message.channel.id
    if channel_id in active_channels:
        context = active_channels[channel_id]
        persona = channel_personas.get(channel_id, DEFAULT_PROMPT)
        
        # Prepare message with persona
        prompt = f"{persona}\nUser: {message.content}"
        
        try:
            response = text_model.generate_content(prompt)
            
            if len(response.text) > 2000:
                chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(response.text)
                
            # Update context (keep last 10 messages)
            context.append({"role": "user", "content": message.content})
            context.append({"role": "assistant", "content": response.text})
            active_channels[channel_id] = context[-10:]
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
