import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
import openai

# Load environment variables
called = False
load_dotenv()
conversation = []
history = []

# Create a new Discord bot instance
bot = discord.Client(intents=discord.Intents.all())

# Load the Discord bot token from the environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set up OpenAI API client
openai.api_key = os.getenv('OPENAI_API_KEY')

async def fetch_conversation(channel):
    """Fetches the chat history of the given channel and initializes the conversation list"""
    global history
    async for message in channel.history(limit=20):
        if message.author != bot.user:
            history.append({"role": "user", "content": message.content})
        else:
            history.append({"role": "assistant", "content": message.content})

# Define on_ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

# Define on_message event
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Fetch the conversation history
    global called
    global conversation
    if not called:
        await fetch_conversation(message.channel)
        called = True
        # Print the conversation history
        for line in history:
            print("Role: " + line["role"] + " Content: " + line["content"])
        conversation = history
    else:
        conversation.append({"role": "user", "content": message.content})

    # Generate a response
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = conversation)
    except openai.error.InvalidRequestError:
        # If the conversation is too long, truncate it by removing around 2/3 of the messages
        conversation = conversation[:len(conversation)//3]

        # Generate a response
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = conversation)
    
    # Displaying the number of tokens used for the response in the console using adequate UI string formatting
    completion_tokens = response.usage["completion_tokens"]
    prompt_tokens = response.usage["prompt_tokens"]
    total_tokens = completion_tokens + prompt_tokens
    print("#######")
    print("Tokens used: " + str(total_tokens))
    print("Prompt tokens: " + str(prompt_tokens))
    print("Completion tokens: " + str(completion_tokens))
    print("#######")

    # Add the response to the conversation
    gpt_response = response.choices[0]["message"]["content"]
    conversation.append({"role": "assistant", "content": gpt_response})
    
    # Send response to Discord
    if len(gpt_response) > 2000:
        for i in range(0, len(gpt_response), 2000):
            if i + 2000 < len(gpt_response):
                await message.channel.send(gpt_response[i:i+2000])
            else:
                await message.channel.send(gpt_response[i:])
    else:
        await message.channel.send(gpt_response)
    return

# Run the Discord bot
bot.run(DISCORD_TOKEN)
