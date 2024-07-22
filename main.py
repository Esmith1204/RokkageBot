from typing import Final
import os
import discord
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from responses import get_responses

#Message stuff
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

word_responses = {}

awaiting_responses = {}


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled)')
        return
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    
    try:
        response: str = get_responses(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

#Slash commands
@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is up")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

#Adds a word to the list
@bot.tree.command(name="addword", description="add a trigger word")
@app_commands.describe(word="the word you want to add")
async def addword(interaction: discord.Interaction, word: str):
    if word in word_responses:
        await interaction.response.send_message(f"'{word}' is already in the list. Current list: {list(word_responses.keys())}")
    else:
        awaiting_responses[interaction.user.id] = word
        await interaction.response.send_message(f"'Added {word}'. Current list: {list(word_responses.keys())}")

#Deletes a word from the list
@bot.tree.command(name="delword", description="delete a word")
@app_commands.describe(word="the word you want to delete")
async def addword(interaction: discord.Interaction, word: str):
    if word in word_responses:
        del word_responses[word]
        await interaction.response.send_message(f"Deleted '{word}'. Current list: {list(word_responses.keys())}")
    else:
        await interaction.response.send_message(f"'{word}' is not in the fucking list bruh. Current list: {list(word_responses.keys())}")

#Creates a response for the bot to maek
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    
    if message.author.id in awaiting_responses:
        word = awaiting_responses.pop(message.author.id)
        word_responses[word] = message.content
        await message.channel.send(f"Response for '{word}' has been created. Current list: {list(word_responses.keys())}")
    else:
        for word, response in word_responses.items():
            if word in message.content.lower():
                await message.content.lower()
                break
    
    await bot.process_commands(message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()