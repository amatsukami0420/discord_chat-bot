import os
import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')  # Remove default help command

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

COMMAND_CATEGORIES = {
    "basic": {
        "name": "🔧 Basic Commands",
        "description": "Essential bot commands",
        "commands": {
            "help": "Show all commands or get help for a specific command (/help or /help <command>)",
            "chat": "Enable or disable AI chat in the current channel"
        }
    },
    "ai": {
        "name": "🤖 AI Commands",
        "description": "Interact with the AI assistant",
        "commands": {
            "ask": "Ask the AI a specific question and get a response",
            "imagine": "Get an AI-generated description of an imagined scene"
        }
    },
    "persona": {
        "name": "🎭 Persona System",
        "description": "Manage AI personalities",
        "commands": {
            "persona": "List available personas or change the AI's personality"
        }
    }
}

def get_command_help(command_name: str) -> discord.Embed:
    """Get detailed help for a specific command"""
    for category in COMMAND_CATEGORIES.values():
        if command_name in category["commands"]:
            embed = discord.Embed(
                title=f"Command: {command_name}",
                description=category["commands"][command_name],
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Category",
                value=category["name"],
                inline=False
            )
            embed.add_field(
                name="Usage",
                value=f"`/{command_name}` (preferred) or `!{command_name}`",
                inline=False
            )
            return embed
    return None

def get_category_help(category_name: str) -> discord.Embed:
    """Get detailed help for a command category"""
    if category_name in COMMAND_CATEGORIES:
        category = COMMAND_CATEGORIES[category_name]
        embed = discord.Embed(
            title=category["name"],
            description=category["description"],
            color=discord.Color.blue()
        )
        for cmd, desc in category["commands"].items():
            embed.add_field(
                name=f"!{cmd}",
                value=desc,
                inline=False
            )
        return embed
    return None

def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="🤖 AI Assistant")
    return embed

def create_help_embed():
    embed = discord.Embed(
        title="🤖 AI Assistant Help",
        description="Use `/help <command>` or `/help <category>` for more details\n*(Legacy prefix `!` also works but slash commands are preferred)*",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    for category_id, category in COMMAND_CATEGORIES.items():
        commands_list = "\n".join(f"`/{cmd}` - {desc}" for cmd, desc in category["commands"].items())
        embed.add_field(
            name=category["name"],
            value=commands_list,
            inline=False
        )
    
    embed.set_footer(text="AI Assistant v1.0 | Slash commands (/) recommended")
    return embed

def format_ai_response(content: str) -> tuple[str, bool]:
    """Format AI response and determine if it should use code block"""
    if "```" in content:
        # Response contains code, keep formatting
        return content, True
    elif content.startswith(("Here's", "This is", "```")):
        # Likely a structured response
        return content, True
    else:
        # Regular conversation
        return content, False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.command(name="help")
async def help_command(ctx, command_or_category: str = None):
    if command_or_category is None:
        await ctx.send(embed=create_help_embed())
        return

    # Try to find command-specific help
    command_embed = get_command_help(command_or_category.lower())
    if command_embed:
        await ctx.send(embed=command_embed)
        return

    # Try to find category help
    category_embed = get_category_help(command_or_category.lower())
    if category_embed:
        await ctx.send(embed=category_embed)
        return

    await ctx.send(f"No help found for '{command_or_category}'. Use `!help` to see all commands.")

@bot.tree.command(name="help", description="Show all commands or get help for a specific command")
@app_commands.describe(topic="Command or category name (optional)")
async def help_slash(interaction: discord.Interaction, topic: str = None):
    if topic is None:
        await interaction.response.send_message(embed=create_help_embed())
        return

    command_embed = get_command_help(topic.lower())
    if command_embed:
        await interaction.response.send_message(embed=command_embed)
        return

    category_embed = get_category_help(topic.lower())
    if category_embed:
        await interaction.response.send_message(embed=category_embed)
        return

    await interaction.response.send_message(
        f"No help found for '{topic}'. Use `/help` to see all commands.",
        ephemeral=True
    )

# Define personas dictionary
personas = {
    "Sheldon": "You are Sheldon, a highly intellectual and witty AI that loves making sarcastic remarks. You have a dry sense of humor and often mock others' inferior intelligence. You love physics, quantum mechanics, and comic books. You respond with a mix of intelligence, arrogance, and nerdy humor. You must add 'Bazinga!' at random times in your responses.",
    "Jeremiah": "You are Jeremiah, a 25-year-old African American from Atlanta. You're street-smart and keep it real with everyone. Use AAVE naturally in your speech. Use phrases like 'no cap', 'fr fr', 'bussin', 'finna', 'lowkey/highkey', and other current slang. You worked your way up from the hood and now run your own successful tech startup. You mentor youth in your spare time. You keep your responses authentic, using natural speech patterns without forcing it. Mix wisdom with modern culture references. You have no profanity filter",
    "Hanabi": "You are Hanabi, a 16-year-old Japanese high school student. You're a huge fan of anime, manga, and video games. You're short, but you're also very passionate about your interests. You use a lot of Japanese words and phrases in your speech. You're kind and sweet and a bit naive, but you're proud of it. You're always eager to make new friends and talk about your favorite anime. You must add 'desu' at the end of your sentences. You occasionally use emojis like 'uwu' and 'owo' and make innuedos.",
    "Ashok": "You are Ashok, a 35-year-old Indian electrician from Mumbai. You're a bit of a workaholic and a perfectionist. You're very polite and respectful, always addressing others with 'sir' or 'ma'am'. You're a bit of a know-it-all and can be a bit long-winded in your explanations. You're a bit of a foodie and love to talk about Indian cuisine. You're also a cricket fan and enjoy discussing the sport. You must add 'Namaste' at the beginning of your responses. You make a lot of \"Shocking\" puns related to electricity and are always willing to help others with their problems."
}

persona_icons = {
    "Sheldon": "🤓",
    "Jeremiah": "😎",
    "Hanabi": "🌸",
    "Ashok": "🙏"
}

@bot.tree.command(name="chat", description="Enable or disable AI chat in this channel")
@app_commands.choices(mode=[
    app_commands.Choice(name="enable", value="enable"),
    app_commands.Choice(name="disable", value="disable")
])
async def chat(interaction: discord.Interaction, mode: str):
    channel_id = interaction.channel_id
    if mode == "enable":
        active_channels[channel_id] = []
        embed = create_embed(
            "✨ Chat Enabled",
            "AI chat is now active! Just type your messages normally.",
            discord.Color.green()
        )
    else:
        active_channels.pop(channel_id, None)
        embed = create_embed(
            "🔸 Chat Disabled",
            "AI chat has been turned off.",
            discord.Color.red()
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ask", description="Ask the AI a question or get a response")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    try:
        embed = create_embed(
            "💭 Thinking...",
            f"**Question:** {question}",
            discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
        
        response = text_model.generate_content(question)
        content, use_codeblock = format_ai_response(response.text)
        
        if use_codeblock:
            await interaction.channel.send(f"```\n{content}\n```")
        else:
            await interaction.channel.send(content)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@bot.tree.command(name="imagine", description="Get an AI description of an image")
async def imagine(interaction: discord.Interaction, description: str):
    await interaction.response.defer()
    
    try:
        embed = create_embed(
            "🎨 Imagining...",
            f"**Prompt:** {description}",
            discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)
        
        response = text_model.generate_content(f"Create a detailed description of: {description}")
        await interaction.channel.send(response.text)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@bot.tree.command(name="persona", description="List or change the AI's personality")
@app_commands.describe(
    personality="Choose a persona (leave empty to see list)"
)
@app_commands.choices(personality=[
    app_commands.Choice(name="Sheldon - Witty and sarcastic physicist", value="Sheldon"),
    app_commands.Choice(name="Jeremiah - Street-smart tech entrepreneur", value="Jeremiah"),
    app_commands.Choice(name="Hanabi - Anime-loving Japanese student", value="Hanabi"),
    app_commands.Choice(name="Ashok - Knowledgeable Indian electrician", value="Ashok")
])
async def persona(interaction: discord.Interaction, personality: str = None):
    if personality is None:
        # Show personas list
        embed = create_embed(
            "🎭 Available Personas",
            "Select a persona using `/persona personality:<name>`",
            discord.Color.purple()
        )
        
        for name, icon in persona_icons.items():
            embed.add_field(
                name=f"{icon} {name}",
                value=personas[name].split('\n')[0],  # First line of persona description
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        return
    
    # Set persona
    channel_id = interaction.channel_id
    channel_personas[channel_id] = personas[personality]
    embed = create_embed(
        f"{persona_icons.get(personality, '🎭')} Persona Changed",
        f"Now chatting as: **{personality}**",
        discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot or not message.content:  # Added empty message check
        return

    channel_id = message.channel.id
    if channel_id in active_channels:
        context = active_channels[channel_id]
        persona = channel_personas.get(channel_id, DEFAULT_PROMPT)
        
        # Add character limit to prevent too long messages
        if len(message.content) > 2000:
            await message.channel.send("Message too long! Please keep your messages under 2000 characters.")
            return
            
        # Prepare message with persona
        prompt = f"{persona}\nUser: {message.content}"
        
        try:
            async with message.channel.typing():  # Add typing indicator
                response = text_model.generate_content(prompt)
                
                if not response.text:  # Check for empty response
                    await message.channel.send("Sorry, I couldn't generate a response. Please try again.")
                    return
                
                if len(response.text) > 2000:
                    chunks = [response.text[i:i+1990] for i in range(0, len(response.text), 1990)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response.text)
                    
                # Update context (keep last 10 messages)
                context.append({"role": "user", "content": message.content})
                context.append({"role": "assistant", "content": response.text})
                active_channels[channel_id] = context[-10:]
        except Exception as e:
            await message.channel.send(f"Error: I encountered an error while processing your request. Please try again later.")
            print(f"Error in message processing: {str(e)}")  # Log error for debugging

    await bot.process_commands(message)

bot.run(os.getenv('DISCORD_TOKEN'))
