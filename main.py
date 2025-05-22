import discord, os, logging, asyncio, random, datetime, requests, aiohttp
from typing import Optional
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

try:
    DEV_ID = int(os.getenv("dev"))
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
@client.tree.command(name="sync", description="DEV ONLY: Manually sync slash commands.")
async def sync(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)
    
    if interaction.user.id != DEV_ID:
        await interaction.response.send_message("This command is available only to approved developers.", ephemeral=True)
        return

    await client.tree.sync()
    await interaction.followup.send("✅ Slash commands synced!", ephemeral=True)

# Magic 8 Ball
@client.tree.command(name="magic_8_ball", description= "Get predictions about the future.")
@app_commands.describe(question="Enter your question.")
async def magic_8_ball(interaction: discord.Interaction, question: str):

    if question.endswith("?") == False:
        await interaction.response.send_message("That's not a question, try again!")
    
    else:
        responses = ["It is certain! 🥳", "It is decidedly so 😌", "Without a doubt 😌", "Yes, definitely 👍", "You may rely on it 🤔",
                    "As I see it, yes 🤔", "Most likely 🙂‍↕️", "Outlook is good", "Yes ✅", "Signs point to yes ✅", "Reply hazy, try again",
                    "Ask again later 🕝", "Better not tell you now 😉", "I can't say for now", "Concentrate and ask again",
                    "Don't count on it 🙂‍↔️", "My reply is no 😑", "My sources say no", "Outlook is not so good", "Very doubtful 😒", "That's a no ❌",
                    "No ❌", "Maybe ❓", "Ask me again", "I don't feel like telling you"]

        await interaction.response.send_message(f"You asked: {question}\n And my answer is: {random.choice(responses)}")

# Bait token
@client.tree.command(name="token", description="Displays the bot's token")
async def token(interaction: discord.Interaction):
    await asyncio.sleep(2)
    await interaction.response.send_message("https://tenor.com/biqA0.gif")

# Support Development
@client.tree.command(name="donate", description="Thanks a lot if you decide to support me 💞")
async def donate(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❤️ Help Keep the Project Going!",
        description="If you like what I do and want to support me, here are a few ways you can help! 😊",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url="https://drive.usercontent.google.com/download?id=1BB3M3a1QnEZ9mtPQ3ZHdeRgMwDEy5kPa")
    embed.add_field(name="☕ Buy me a coffee.", value="https://ko-fi.com/ga1_ahad", inline=False)
    embed.add_field(name="💰 Bitcoin address", value="bc1q5lcdg3g78786hdueh8702xgv9l2dv3fz9mlgun\nAlternatively you can use the QR code provided")
    embed.set_footer(text="Even the smallest bits mean a lot! 💖")

    await interaction.response.send_message(embed=embed)

# Owner
@client.tree.command(name="owner", description="Get in contact with the dev")
async def owner(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Credits",
        description="Some places where you can contact me.",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.now()
    )

    embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/172686127?v=4")

    fields = [
        # 🧭 Socials
        {"name": "🧭 Social Profiles", "value": " ", "inline": False},
        {"name": "🎮 Discord", "value": "Ga1_ahad", "inline": True},
        {"name": "🪽 Twitter", "value": "[_Gal_ahad](https://x.com/_Gal_ahad)", "inline": True},
        {"name": "🦋 Bluesky", "value": "[Gal-ahad](https://bsky.app/profile/gal-ahad.bsky.social)", "inline": True},
        {"name": "🐘 Mastodon", "value": "[Sir_Ga1ahad](https://mastodon.social/@Sir_Ga1ahad)", "inline": True},
        {"name": "👽 Reddit", "value": "[Storyshifting](https://www.reddit.com/user/Storyshifting/)", "inline": True},

        # 📬 Contact
        {"name": "📬 Direct Contact", "value": " ", "inline": False},
        {"name": "📧 Email me", "value": "AethericKnight@proton.me", "inline": False},

        # 🛠️ Support
        {"name": "🛠️ Feedback", "value": " ", "inline": False},
        {"name": "🪲 Report a bug", "value": "[Open an Issue on Github](https://github.com/Gal-ahad/Carmen/issues)", "inline": False}
    ]

    for field in fields:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

    await interaction.response.send_message(embed=embed)

# Clean the chat
@client.tree.command(name="clean", description="Bulk delete messages (max:100)")
async def clean(interaction: discord.Interaction, amount: int):

    max_amount = 100
    
    if amount == 0:
        await interaction.response.send_message("No messages were deleted.", ephemeral=True)
        return
    
    if amount > max_amount:
        await interaction.response.send_message(f"Sorry, I can only purge up to {max_amount} messages at once.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    await interaction.channel.purge(limit=amount)

    if amount == 1:
        await interaction.followup.send("Deleted 1 message", ephemeral=True)
    else:
        await interaction.followup.send(f"{amount} messages have been deleted.", ephemeral=True)

# Help
@client.tree.command(name="help", description="Prints out a list of available commands")
async def help(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Command List",
        description="Here's everything i can do!",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.now()
    )

    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/6621/6621597.png")

    fields = [
        {"Name": "😆 Fun", "value": " ", "inline": False},
        {"Name": "`/joke`", "value": "Retrieves a joke to share in the chat", "inline": False},
        {"Name": "`/token`", "value": "Prints out the bot's token", "inline": False},
        {"Name": "`/magic_8_ball`", "value": "Get predictions about the future", "inline": False},

        {"Name": "⚙️ Functional", "value": " ", "inline": False},
        {"Name": "`/sync`", "value": "DEV ONLY: Manually syncs slash commands tree", "inline": False},

        {"Name": "🚨 Moderation", "value": " ", "inline": False},
        {"Name": "`/clean`", "value": "Purges no more than 100 messages from the chat", "inline": False},

        {"Name": "🎲 Misc", "value": " ", "inline": False},
        {"Name": "`/owner`", "value": "Get my contact info", "inline": False},
        {"Name": "`/donate`", "value": "Support the project!", "inline": False}

    ]

    for field in fields:
        embed.add_field(name=field["Name"], value=field["value"], inline=field["inline"])

    await interaction.response.send_message(embed=embed)

# Tell a joke
@client.tree.command(name="jokes", description="Wanna hear a joke?")
async def joke(interaction: discord.Interaction):
    await interaction.response.defer()  # In case the API takes a moment

    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await interaction.followup.send("Couldn't fetch a joke right now 😞")
                return

            data = await response.json()

            if data["type"] == "single":
                await interaction.followup.send(data["joke"])
            elif data["type"] == "twopart":
                await interaction.followup.send(f"{data['setup']}\n{data['delivery']}")
            else:
                await interaction.followup.send("Got a weird joke format I can't handle 😅. Could you ask me again?")

# ==== EVENTS =====
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("Fetching and deleting global commands...")

    try:
        app_id = client.user.id
        global_commands = await client.http.get_global_commands(app_id)

        print(f"Found {len(global_commands)} global commands.")

        for cmd in global_commands:
            await client.http.delete_global_command(app_id, cmd["id"])

        # Resync the current in-code commands (if any)
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands after wipe.")

    except Exception as e:
        print(f"Failed to wipe global commands: {e}")

    print("Bot is now online\n------------------")

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