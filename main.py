import discord, os, logging, asyncio, random, datetime
from typing import Optional
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

try:
    DEV_ID = int(os.getenv("dev"))
    print("Running the bot in developer mode.")
except Exception as e:
    DEV_ID = int(0)
    print("Running the bot in guest mode.")

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
    
    if interaction.user.id != DEV_ID:
        await interaction.response.send_message("This command is available only to approved developers.", ephemeral=True)
        return

    await client.tree.sync()
    await interaction.response.send_message("✅ Slash commands synced!", ephemeral=True)

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

    embed.set_thumbnail(url="https://files.catbox.moe/ou2v7l.jpg")
    embed.add_field(name="☕ Buy me a coffee.", value="https://ko-fi.com/ga1_ahad", inline=False)
    embed.add_field(name="💰 Bitcoin address", value="bc1q5lcdg3g78786hdueh8702xgv9l2dv3fz9mlgun")
    embed.set_footer(text="Even the smallest bits mean a lot! 💖")

    await interaction.response.send_message(embed=embed)

# owner
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
        {"name": "🎮 Discord", "value": "Ga1_ahad", "inline": False},
        {"name": "🪽 Twitter", "value": "[_Gal_ahad](https://x.com/_Gal_ahad)", "inline": False},
        {"name": "🦋 Bluesky", "value": "[Gal-ahad](https://bsky.app/profile/gal-ahad.bsky.social)", "inline": False},
        {"name": "🐘 Mastodon", "value": "[Sir_Ga1ahad](https://mastodon.social/@Sir_Ga1ahad)", "inline": False},
        {"name": "👽 Reddit", "value": "[Storyshifting](https://www.reddit.com/user/Storyshifting/)", "inline": False},
        {"name": "‎", "value": "\u200b", "inline": False},  # Invisible spacer to break the section

        # 📬 Contact
        {"name": "📬 Direct Contact", "value": " ", "inline": False},
        {"name": "📧 Email me", "value": "sebmiller03@proton.me", "inline": False},
        {"name": "‎", "value": "\u200b", "inline": False},  # Spacer

        # 🛠️ Support
        {"name": "🛠️ Feedback", "value": " ", "inline": False},
        {"name": "🪲 Report an Issue", "value": "[Open an Issue on Github](https://github.com/Gal-ahad/Carmen/issues)", "inline": False}
    ]

    for field in fields:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

    await interaction.response.send_message(embed=embed)



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