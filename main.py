import discord, os, logging, asyncio, random
from typing import Optional
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

try:
    DEV_ID = os.getenv("dev")
except Exception as e:
    DEV_ID = int(0)

# ==== INTENTS =====
intents = discord.Intents.default()
intents.message_content = True

# ==== CLIENT =====
client = commands.Bot(command_prefix='!',intents=intents)

# ==== LOGGING =====
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# ==== COMMANDS =====

# Sync
@client.tree.command(name="sync", description="DEV ONLY: Manually sync slash commands")
async def sync(interaction: discord.Interaction):
    if interaction.user.id != DEV_ID:
        await interaction.response.send_message("This command is available only to developers.", ephemeral=True)
        return

    await client.tree.sync()
    await interaction.response.send_message("✅ Slash commands synced!", ephemeral=True)

# ==== EVENTS =====
@client.event
async def on_ready():
    print(f"Successfully logged in as {client.user}")
    print("Syncing commands...")
    await client.tree.sync()

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)
        
    print("Bot is now online.\n--------------")

@client.event
async def on_message(message):
    if message.author == client.user:
        return # ignore messages from self

# ==== MAIN =====
def main():
	try:
		bot_token = os.getenv("bot_token")
		client.run(bot_token, log_handler=handler, log_level=logging.DEBUG)
		
		if not bot_token:
			print("Error: No Discord token found. Please set the the token environment variable")
		
	except Exception as error:
		print(f"An error occurred: {error}.")
		
if __name__ == "__main__":
	main()
else:
	print("Please run the bot directly")