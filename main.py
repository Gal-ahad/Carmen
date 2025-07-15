import discord, os, logging, asyncio, random, datetime, requests, aiohttp, psutil, time, openai, base64, re
from typing import Optional
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from types import SimpleNamespace
import filter_module
from urllib.parse import urlparse

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

# sync
@client.tree.command(name="sync", description="DEV ONLY: Manually sync slash commands.")
async def sync(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)
    
    if interaction.user.id != DEV_ID:
        await interaction.followup.send("This command is available only to approved developers.", ephemeral=True)
        return

    disclaimer_msg = await interaction.followup.send("This process might take 1 or 2 minute max, i'll message you when im done")

    await asyncio.sleep(10)
    await disclaimer_msg.delete()

    await client.tree.sync()

    await interaction.followup.send("✅ Slash commands have been synced!", ephemeral=True)

# magic 8 Ball
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

# bait token
@client.tree.command(name="token", description="Displays the bot's token")
async def token(interaction: discord.Interaction):
    await asyncio.sleep(2)
    await interaction.response.send_message("https://tenor.com/biqA0.gif")

# support development
@client.tree.command(name="donate", description="Thanks a lot if you decide to support me 💞")
async def donate(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❤️ Help Keep the Project Going!",
        description="If you like what I do and want to support me, here are a few ways you can help! 😊",
        color=discord.Color.gold()
    )
	
    embed.add_field(name="☕ Buy me a coffee.", value="https://ko-fi.com/ga1_ahad", inline=False)
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

# clean the chat
@client.tree.command(name="clean", description="Bulk delete messages (max:100)")
async def clean(interaction: discord.Interaction, amount: int):

    max_amount = 100

    await interaction.response.defer(ephemeral=True)
    
    if amount == 0:
        await interaction.followup.send("No messages were deleted.", ephemeral=True)
        return
    
    if amount > max_amount:
        await interaction.followup.send(f"Sorry, I can only purge up to {max_amount} messages at once.", ephemeral=True)
        return
    
    await interaction.channel.purge(limit=amount)

    if amount == 1:
        await interaction.followup.send("Deleted 1 message", ephemeral=True)
    else:
        await interaction.followup.send(f"{amount} messages have been deleted.", ephemeral=True)

# help
@client.tree.command(name="help", description="Prints out a list of available commands")
async def help(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Command List",
        description="Here's everything you can ask me to do!",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.now()
    )

    embed.set_thumbnail(url="https://files.catbox.moe/4eorkn.png")

    fields = [
        {"Name": "😆 Fun", "value": " ", "inline": False},
        {"Name": "`/jokes` - Sends a joke in the chat", "value": " ", "inline": False},
        {"Name": "`/token` - Shows the bot's token", "value": " ", "inline": False},
        {"Name": "`/magic_8_ball` - Ask anything to the magic 8 ball", "value": " ", "inline": False},
        {"Name": "`/coinflip` - Flips a coin if you don't have any", "value": " ", "inline": False},

        {"Name": "⚙️ Functional", "value": " ", "inline": False},
        {"Name": "`/exchange` - Converts EUR into other currencies", "value": " ", "inline": False},
        {"Name": "`/ping` - Check the ping latency and RAM", "value": " ", "inline": False},
        {"Name": "`/weather` - Get weather conditions for a given city", "value": " ", "inline": False},
        {"Name": "`/ask` - Get AI powered responses", "value": " ", "inline": False},
        {"Name": "`/spotify` - Search Spotify tracks without leaving Discord", "value": " ", "inline": False},
        {"Name": "`/die_roll` - Roll a dice", "value": " ", "inline": False},

        {"Name": "🚨 Moderation", "value": " ", "inline": False},
        {"Name": "`/clean` - Bulk delete messages", "value": " ", "inline": False},

        {"Name": "🎲 Misc", "value": " ", "inline": False},
        {"Name": "`/owner` - Get in contact with the developer", "value": " ", "inline": False},
        {"Name": "`/donate` - Support the project", "value": " ", "inline": False}

    ]

    for field in fields:
        embed.add_field(name=field["Name"], value=field["value"], inline=field["inline"])

    await interaction.response.send_message(embed=embed)

# tell a joke
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

# wipe the command tre
@client.tree.command(name="wipe", description="DEV ONLY: Wipes command tree")
async def wipe(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)

    if interaction.user.id != DEV_ID:
        await interaction.followup.send("This command is available only to approved developers.", ephemeral=True)
        return

    try:
        app_id = client.user.id
        global_commands = await client.http.get_global_commands(app_id)

        for cmd in global_commands:
            await client.http.delete_global_command(app_id, cmd["id"])

        await client.tree.sync()

    except Exception as e:
        print(f"Failed to wipe global commands: {e}")

    await interaction.followup.send("✅ Command tree has been wiped and resynced!\n Don't forget to restart Discord to apply your changes.")

# flip a coin
@client.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):

    outcomes = ["head", "tail"]

    await interaction.response.defer()

    flip = random.choice(outcomes)

    if flip == "head":
        await interaction.followup.send("I got head!")
    else:
        await interaction.followup.send("I got tails!")

# exchange EUR
async def exchange_function(target_currency: str) -> Optional[float]:

    api_key = os.getenv("fixer_api")
    if not api_key:
        return None

    base_url = "http://data.fixer.io/api/latest"
    params = {
        "access_key": api_key,
        "symbols": target_currency
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if not data.get("success", False):
            return None


        rates = data.get("rates", {})
        target_rate = rates.get(target_currency)

        if target_rate is None:
            return None

        # Since Fixer always returns EUR as base, EUR ➔ target rate is direct
        return target_rate

    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None
def get_flag_url(currency_code: str) -> Optional[str]:

    CURRENCY_TO_COUNTRY = {
        "USD": "US","GBP": "GB","JPY": "JP","CHF": "CH",
        "AUD": "AU","CAD": "CA","CNY": "CN","INR": "IN","BRL": "BR",
        "MXN": "MX",}

    country_code = CURRENCY_TO_COUNTRY.get(currency_code.upper())

    if not country_code:
        return None

    return f"https://flagcdn.com/w80/{country_code.lower()}.png"

# exchange command
@client.tree.command(name="exchange", description="Convert EUR into other currencies")
async def exchange(interaction: discord.Interaction,amount: float,target_currency: str):
    await interaction.response.defer()

    target = target_currency.upper()
    source = "EUR"

    # Get the rate from EUR to target
    rate = await exchange_function(target)

    if rate is not None:
        converted_amount = amount * rate

        embed = discord.Embed(
            title="Currency Conversion",
            description=f"Conversion from {source} to {target}",
            color=discord.Color.yellow(),
            timestamp=discord.utils.utcnow()
        )

        fields = [
            {"name": "Amount", "value": f"{amount:,.2f} {source}", "inline": True},
            {"name": "Exchange Rate", "value": f"1 {source} = {rate:,.4f} {target}", "inline": True},
            {"name": "Converted Amount", "value": f"{converted_amount:,.2f} {target}", "inline": True}
        ]

        for field in fields:
            embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

        flag_url = get_flag_url(target)
        if flag_url:
            embed.set_thumbnail(url=flag_url)

        embed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    else:
        await interaction.followup.send(f"Failed to get exchange rate for {target}. Please check the currency code and try again.")

# ping and ram
def set_client(client):

    global _client
    _client = client

@client.tree.command(name="ping", description="Check RAM usage and ping latency")
async def stats(interaction: discord.Interaction):


    client = interaction.client

    start_time = time.time()
    await interaction.response.defer(ephemeral=False)
    end_time = time.time()
    api_latency = round((end_time - start_time) * 1000)

    try:
        if client.latency and not (client.latency != client.latency):
            websocket_latency = f"{round(client.latency * 1000)} ms"
        else:
            websocket_latency = "Calculating..."
    except (TypeError, AttributeError) as error:
        websocket_latency = f"Unavailable: {error}"

    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024

    embed = discord.Embed(
        title="Bot Stats",
        description="Current performance statistics",
        color=discord.Color.light_grey()
    )

    fields = [
        {"name": "API Latency", "value": f"{api_latency} ms", "inline": False},
        {"name": "WebSocket Latency", "value": websocket_latency, "inline": False},
        {"name": "Memory Usage", "value": f"{memory_usage:.2f} MB", "inline": False}
    ]

    for field in fields:
        embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

    embed.set_footer(text=f"Requested by {interaction.user.name}")
    embed.set_thumbnail(url="https://i.postimg.cc/R0JPmnpn/fast-internet-speed-icon-1.png")
    embed.timestamp = discord.utils.utcnow()

    await interaction.followup.send(embed=embed)

# weather forecast
@client.tree.command(name="weather", description="Get weather info on a given city")
@app_commands.describe(city="Which city do you want to check?")
async def weather(interaction: discord.Interaction, city: str):

    # Defer the response since API calls might take some time
    await interaction.response.defer()

    if city.isdigit() or city.isalnum():
        await interaction.followup.send("Numbers are not allowed. Only text")
        return

    weather_api_key = os.getenv("weather_api")
    if not weather_api_key:
        await interaction.followup.send("weather API key not found. Please check your environment variables.")
        return

    weather_base_url = 'http://api.weatherstack.com/current'

    # Fetch and display the weather for a given location
    params = {'access_key': weather_api_key, 'query': city.lower()}

    try:
        # Make a request to the weatherstack API
        response = requests.get(weather_base_url, params=params)
        data = response.json()

        # Check for an error from the API
        if 'error' in data:
            error_info = data['error']
            if error_info.get('code') == 104:  # Code 104 = Monthly quota reached
                weather_info = "I'm sorry, but I'm operating on a free plan and I have reached the limit for this month's requests."
                await interaction.followup.send(weather_info)
                return
            else:
                weather_info = f"Error fetching weather data: {error_info.get('info', 'Unknown error')}"
                await interaction.follow.send(weather_info)
                return

        elif 'current' in data and 'location' in data:
            current_weather = data['current']
            location_name = data['location']['name']
            temperature = current_weather['temperature']
            weather_descriptions = ', '.join(current_weather.get('weather_descriptions', ['Unknown']))
            humidity = current_weather.get('humidity', 'Unknown')
            wind_speed = current_weather.get('wind_speed', 'Unknown')

            # Create a response message
            weather_embed = discord.Embed(
                title=f"Results for {location_name}",
                description="Here's what i could find.",
                color=discord.Color.blurple(),
                timestamp=datetime.datetime.now()
            )

            fields = [
                {"name": "Temperature", "value": f"{temperature}°C \\ {int(temperature)*9/5+32}°F", "inline": False},
                {"name": "Sky's Conditions", "value": weather_descriptions, "inline":False},
                {"name": "Humidity", "value": f"{humidity}%", "inline": False},
                {"name": "Wind Speed", "value": f"{wind_speed} km/h \\ {wind_speed * 0.621371:.2f} mph", "inline": False}
            ]

            for field in fields:
                weather_embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])

            weather_embed.set_thumbnail(url="https://i.postimg.cc/vHKcp1Jn/purepng-com-weather-iconsymbolsiconsapple-iosiosios-8-iconsios-8-721522596142qx4ep.png")

            await interaction.followup.send(embed=weather_embed)

        else:
            weather_info = "Sorry, I couldn't retrieve the weather information. Please check the location and try again."
    
    except Exception as e:
        weather_info = f"Error processing weather data: {str(e)}"

# AI responses
# fetch the API key from the .env file
try:
    openai.api_key = os.getenv("openai_key")
    openai_key = openai.api_key
    
    openai_available = True
except ImportError as imperr:
    openai_available = False
    print(f"OpenAI package not installed, reason: {imperr} - /ask command will not be available")

# ask command
def is_direct_image_link(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if not parsed.scheme.startswith("http"):
            return False
        return re.search(r"\.(png|jpe?g|webp|gif|bmp)$", parsed.path.lower()) is not None
    except:
        return False

@client.tree.command(name="ask", description="Get AI powered responses")
@app_commands.describe(
    prompt="The prompt to send",
    image_mode="Enable image input (choose 'on' to activate)"
)
@app_commands.choices(image_mode=[
    app_commands.Choice(name="on", value="on"),
    app_commands.Choice(name="off", value="off")
])
async def ask(
    interaction: discord.Interaction,
    prompt: str,
    image_mode: app_commands.Choice[str] = None
):
    if not openai_available:
        await interaction.response.send_message("AI integration is currently unavailable. 😔")
        return

    await interaction.response.defer()

    prompt_msg = None
    image_url = None

    try:
        if image_mode and image_mode.value == "on":
            prompt_msg = await interaction.followup.send(
                "Alright, I'm in image mode!\n"
                "Please either:\n"
                "- Upload an image **directly here** (preferred)\n"
                "- Or paste a **direct link** to a supported image (e.g. ends in .jpg, .png — no Twitter/X links please)\n\n"
                "You have **2 minutes**. Type `abort` to cancel image mode."
            )

            def check(m: discord.Message):
                return (
                    m.author.id == interaction.user.id and
                    m.channel.id == interaction.channel.id
                )

            try:
                msg = await client.wait_for("message", timeout=120.0, check=check)

                if msg.content.strip().lower() == "abort":
                    await interaction.followup.send("Image mode aborted. No worries!")
                    if prompt_msg:
                        try:
                            await prompt_msg.delete()
                        except (discord.Forbidden, discord.HTTPException):
                            pass
                    return

                if msg.attachments:
                    for attachment in msg.attachments:
                        if attachment.content_type and attachment.content_type.startswith("image/"):
                            image_url = attachment.url
                            break

                if not image_url:
                    url_candidate = msg.content.strip()
                    if is_direct_image_link(url_candidate):
                        image_url = url_candidate

                if image_url and prompt_msg:
                    try:
                        await prompt_msg.delete()
                    except (discord.Forbidden, discord.HTTPException):
                        pass

                if not image_url:
                    await interaction.followup.send("Hmm... that doesn't seem like a usable image. Image mode cancelled.")
                    return

            except asyncio.TimeoutError:
                await interaction.followup.send("Timed out waiting for an image. You can try again anytime.")
                if prompt_msg:
                    try:
                        await prompt_msg.delete()
                    except (discord.Forbidden, discord.HTTPException):
                        pass
                return

        # Compose content for OpenAI
        content_block = [{"type": "text", "text": prompt}]
        if image_url:
            content_block.insert(0, {
                "type": "image_url",
                "image_url": {"url": image_url}
            })

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "You are a helpful assistant, but keep it casual like amongst friends. "
                    "Do not use more than 2k characters. Avoid lists; respond naturally in a paragraph. You are allowed to sprinkle some emojis to make the conversation friendlier."
                )},
                {"role": "user", "content": content_block}
            ],
            max_tokens=1000
        )

        answer = response.choices[0].message["content"]

        await interaction.followup.send(answer)
        await asyncio.sleep(2)
        await interaction.channel.send(
            "Just a disclaimer: I am not perfect, even a machine like me can get things wrong. Don't forget to fact check this stuff if it's important 🧐",
            allowed_mentions=discord.AllowedMentions.none()
        )

    except Exception as e:
        await interaction.followup.send(f"Sorry, something went wrong: `{str(e)}`")

# spotify API
CLIENT_ID = os.getenv("spotify_client_id")
CLIENT_SECRET = os.getenv("spotify_client_secret")

def get_access_token():

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Could not get access token", response.text)

def search_spotify(track_name, artist_name, token):

    base_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    def make_request(query):
        params = {
            "q": query,
            "type": "track",
            "limit": 5
        }

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()["tracks"]["items"]
        return []

    if artist_name:
        exact_query = f"track:{track_name} artist:{artist_name}"
        results = make_request(exact_query)
    else:
        results = []

    if not results:
        fallback_query = f"{track_name}"

        if artist_name:
            fallback_query += f" {artist_name}"

        results = make_request(fallback_query)

    return results

@client.tree.command(name="spotify", description="Searches for songs on Spotify")
@app_commands.describe(track="The song's title", artist="The artist's name")
async def spotify_search(interaction: discord.Interaction, track: str, artist: Optional[str] = None):

    await interaction.response.defer()

    try:
        token = get_access_token()
        results = search_spotify(track, artist, token)

        if not results:
            await interaction.followup.send("😢 Couldn't find any matching tracks.")
            return

        album_images = results[0]["album"]["images"]
        if album_images:
            thumbnail_url = album_images[0]["url"]
        else:
            thumbnail_url = None

        title_text = f"Results for {track.title()}"
        if artist:
            title_text += f" by {artist.title()}"

        embed = discord.Embed(
            title=title_text,
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
            )

        for idx, item in enumerate(results, 1):
            track_name = item['name']
            artist_names = ", ".join([a['name'] for a in item['artists']])
            url = item['external_urls']['spotify']
            embed.add_field(name=f"{idx}. {track_name} by {artist_names}", value=f"[Listen on Spotify]({url})", inline=False)

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        else:
            embed.set_thumbnail(url="https://storage.googleapis.com/pr-newsroom-wp/1/2023/05/Spotify_Primary_Logo_RGB_Green.png")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"😬 Something went wrong: {e}")

# die roll
@client.tree.command(name="die_roll", description="Roll a die")
@app_commands.describe(die_type="How many faces does your die have?")
async def die_roll(interaction: discord.Interaction, die_type: int):

    faces = []

    for i in range(die_type):
        faces.append(i)

    await interaction.response.send_message(f"🎲 The die has chosen: it's a {random.choice(faces)}!")

@client.tree.command(name="filter_init", description="Initialize or check filter settings for this server")
async def init_filter(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    guild_id = interaction.guild.id if interaction.guild else None
    
    if not guild_id:
        await interaction.followup.send("❌ This command can only be used in a server.", ephemeral=True)
        return
    
    try:
        # Call the filter module's initialization function
        # You'll need to add this function to your filter_module.py
        result = await filter_module.initialize_server_filter(guild_id, interaction.guild.name)
        
        if result["created"]:
            embed = discord.Embed(
                title="✅ Filter Initialized",
                description=f"Created new filter configuration for **{interaction.guild.name}**",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(
                name="Default Settings",
                value="• All filters are disabled by default\n• Use `/filter_add` to start adding keywords",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="ℹ️ Filter Already Exists",
                description=f"Filter configurations for **{interaction.guild.name}** already exists",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
        
        embed.set_footer(text=f"Server ID: {guild_id}")
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error initializing filter: {str(e)}", ephemeral=True)
        print(f"Error in init_filter command: {e}")



# ==== EVENTS =====
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

    # Setup moderation commands
    moderation_group = discord.app_commands.Group(name="filter", description="Filter-related commands")
    moderation_group = filter_module.setup_moderation_commands(moderation_group, client)
    client.tree.add_command(moderation_group)

    print("Bot is now online\n------------------")

@client.event
async def on_message(message):
    if message.author == client.user:
        return # ignore messages from self

    # Process commands
    await client.process_commands(message)
    
    # Use the filter module
    await filter_module.on_message_filter(message, client)

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