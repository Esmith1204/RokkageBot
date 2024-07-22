from typing import Final
import os
import discord
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from responses import get_responses

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Initialize bot with necessary intents
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store word-response pairs
word_responses = {}

# Track users being prompted for responses
awaiting_responses = {}

# Function to send message responses
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled)')
        return

    is_private = user_message.startswith('?')
    user_message = user_message[1:] if is_private else user_message

    try:
        response: str = get_responses(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(f"Error sending message: {e}")

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Adds a word to the list
@bot.tree.command(name="addword", description="Add a trigger word")
@app_commands.describe(word="The word you want to add")
async def addword(interaction: discord.Interaction, word: str):
    if word in word_responses:
        await interaction.response.send_message(f"'{word}' is already in the list.", ephemeral=True, delete_after=5)
    else:
        awaiting_responses[interaction.user.id] = word
        await interaction.response.send_message(f"Added '{word}'. Please provide a response for this word.", ephemeral=True, delete_after=5)
    print(f"{interaction.user} added word '{word}'")

# Deletes a word from the list
@bot.tree.command(name="delword", description="Delete a word")
@app_commands.describe(word="The word you want to delete")
async def delword(interaction: discord.Interaction, word: str):
    if word in word_responses:
        del word_responses[word]
        await interaction.response.send_message(f"Deleted '{word}'.", ephemeral=True, delete_after=5)
    else:
        await interaction.response.send_message(f"'{word}' is not in the list.", ephemeral=True, delete_after=5)
    print(f"{interaction.user} deleted word '{word}'", ephemeral=True, delete_after=5)

# List all words in the list
@bot.tree.command(name="listwords", description="List all trigger words")
async def listwords(interaction: discord.Interaction):
    if word_responses:
        word_list = ', '.join(word_responses.keys())
        await interaction.response.send_message(f"Current words: {word_list}")
    else:
        await interaction.response.send_message("No words have been added yet.")
    print(f"{interaction.user} requested the list of words")

# Handle messages
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    print(f"Message received from {message.author}: {message.content}")

    if message.author.id in awaiting_responses:
        word = awaiting_responses.pop(message.author.id)
        word_responses[word] = message.content
        await message.channel.send(f"Response for '{word}' has been created.")
        print(f"Response for '{word}' set by {message.author}: {message.content}")
    else:
        # Check if the message contains any custom response words
        for word, response in word_responses.items():
            if word in message.content.lower():
                await message.channel.send(response)
                print(f"Custom response triggered for '{word}': {response}")
                break
        else:
            # Use get_responses for predefined responses
            response = get_responses(message.content)
            if response:
                await message.channel.send(response)
                print("")

    await bot.process_commands(message)

def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
