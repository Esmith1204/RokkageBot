import json
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
DATA_FILE: Final[str] = 'word_responses.json'

# Initialize bot with necessary intents
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store word-response pairs
word_responses = {}

# Counts user words to limit
user_word_count = {}

# Track users being prompted for responses
awaiting_responses = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({"word_responses": word_responses, "user_word_count": user_word_count}, f)

def load_data():
    global word_responses, user_word_count
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            word_responses = data.get('word_responses', {})
            user_word_count = data.get('user_word_count', {})

load_data()

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
@app_commands.describe(word="The word you want to add", response="The response you want to add")
async def addword(interaction: discord.Interaction, word: str, response: str):
    user_id = str(interaction.user.id)
    user_count = user_word_count.get(user_id, 0)

    if user_count >= 4:
        await interaction.response.send_message("Can't make anymore words datebayo baka")
        return

    if word in word_responses:
        await interaction.response.send_message(f"'{word}' is already in the list.", ephemeral=True)
    else:
        word_responses[word] = response
        user_word_count[user_id] = user_count + 1
        save_data()
        await interaction.response.send_message(f"Added '{word}' and response '{response}'.", ephemeral=True)
    print(f"{interaction.user} added word '{word}'")

# Deletes a word from the list
@bot.tree.command(name="delword", description="Delete a word")
@app_commands.describe(word="The word you want to delete")
async def delword(interaction: discord.Interaction, word: str):
    if word in word_responses:
        del word_responses[word]
        user_id = str(interaction.user.id)
        user_word_count[user_id] = max(0, user_word_count.get(user_id, 0) - 1)
        save_data()
        await interaction.response.send_message(f"Deleted '{word}'.", ephemeral=True)
    else:
        await interaction.response.send_message(f"'{word}' is not in the list.", ephemeral=True)
    print(f"{interaction.user} deleted word '{word}'")

# List all words in the list
@bot.tree.command(name="listwords", description="List all trigger words")
async def listwords(interaction: discord.Interaction):
    if word_responses:
        word_list = ', '.join(word_responses.keys())
        await interaction.response.send_message(f"Current words: {word_list}")
    else:
        await interaction.response.send_message("No words have been added yet.")
    print(f"{interaction.user} requested the list of words")

# Hard resest all saved chat responses
@bot.tree.command(name="hardreset", description="Clear all saved words and responses")
async def hardreset(interaction: discord.Interaction):
    global word_responses, user_word_count

    await interaction.response.send_message(
        "Are you sure you want reset every saved response sigma?"
    )

    def check(m: discord.Message):
        return m.author == interaction.user and m.channel == interaction.channel
    
    try:
        confirmation = await bot.wait_for("message", check=check, timeout=30)
        if confirmation.content.lower() == "yes":
            word_responses.clear()
            user_word_count.clear()
            save_data()
            await interaction.followup.send("Reset successful.", ephemeral=True)
            print(f"{interaction.user} performed a hard reset of all responses.")
        else:
            await interaction.followup.send("Reset was canceled", ephemeral=True)

    except Exception as e:
        await interaction.followup.send("No response received. Reset canceled.", ephemeral=True)
        print(f"Hard reset timed out {e}")

# Handle messages
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    print(f"Message received from {message.author}: {message.content}")

    await bot.process_commands(message)  # Ensure this is called once

    if message.author.id in awaiting_responses:
        word = awaiting_responses.pop(message.author.id)
        word_responses[word] = message.content
        save_data()
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

@bot.tree.command(name="secret", description="Secret access: Invite only")
@app_commands.describe(code="4 Digit Code")
async def secret(interaction: discord.Interaction, code: str)
    secret_code = "1221"
    secret_message = """
    Hi, You’re 20 now just like me. I hope fatherhood 
    is treating you well. Hope the kid is doing well too. 

    My family always told me to surround myself with good people. I guess I wasn’t too good at, that when I was in high school, 
    because I had degenerate friends who played League all day. Probably explains why I was still 'bro' presenting when you 
    first saw me. I was slowly morphing out of that phase but meeting you must’ve been some kind of butterfly effect. I have 
    become the best version of myself because of you. I can’t pinpoint exactly what it is but I think it’s because I see how 
    much you’ve done to get where you are and I tell myself “I want to be like that and live that life.” 
    We’ve shared so many experiences together, both good and bad. We’re so close that I see your achievements in school and 
    I get happy seeing you happy and I’m sure it’s the same way for you too. Thanks for saving my dumbass from comfort. I want 
    to continue seeing you go up in life. I see so much of the work you do and dedication you have and you 
    deserve everything good that comes at you.

    Here’s to being 20.
    Obviously the best wishes from me,

    Rokkage
    """
    if code == secret_code:
        await interaction.response.send_message(secret_message, ephemeral=True)
        print(f"{interaction.user} entered the correct code.")
    else:
        await interaction.response.send_message("Incorrect code.", ephemeral=True)
        print(f"{interaction.user} entered the incorrect code.")

def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
