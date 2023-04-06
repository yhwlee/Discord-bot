import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
conversation = []

# Create a new Discord bot instance
bot = discord.Client(intents=discord.Intents.all())

# Load the Discord bot token from the environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set up OpenAI API client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

# Define on_message event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    conversation.append({"role": "user", "content": message.content})
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = conversation)
    gpt_response = response.choices[0]["message"]["content"]
    conversation.append({"role": "assistant", "content": gpt_response})
    # Send response to Discord
    await message.channel.send(gpt_response)
    return
# Run the Discord bot
bot.run(DISCORD_TOKEN)
