import discord, os, logging, asyncio, random, datetime, requests, aiohttp, psutil, time, openai, base64
from typing import Optional
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from types import SimpleNamespace

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

    await client.tree.sync()
    await interaction.followup.send("✅ Slash commands synced!", ephemeral=True)

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

    embed.set_thumbnail(url="https://drive.usercontent.google.com/download?id=1BB3M3a1QnEZ9mtPQ3ZHdeRgMwDEy5kPa")
    embed.add_field(name="☕ Buy me a coffee.", value="https://ko-fi.com/ga1_ahad", inline=False)
    embed.add_field(name="💰 Bitcoin address", value="bc1q5lcdg3g78786hdueh8702xgv9l2dv3fz9mlgun\nAlternatively you can use the QR code provided")
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
class EmbedPaginator:
    def __init__(self, ctx, embeds, timeout=300):
        self.ctx = ctx
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        self.timeout = timeout
        self.controls = {
            "⬅️": self.previous_page,
            "➡️": self.next_page,
            "🔢": self.jump_to_page,
            "❌": self.stop
        }
        self.message = None

    async def start(self):
        if self.total_pages == 1:
            return await self.ctx.send(embed=self.embeds[0])

        self.message = await self.ctx.send(embed=self.embeds[self.current_page])

        for emoji in self.controls:
            try:
                await self.message.add_reaction(emoji)
            except discord.Forbidden:
                await self.ctx.send("I don't have permission to add reactions!")
                return

        def check(reaction, user):
            return (
                user == self.ctx.author
                and reaction.message.id == self.message.id
                and str(reaction.emoji) in self.controls
            )

        while True:
            try:
                reaction, user = await self.ctx.client.wait_for(
                    "reaction_add", timeout=self.timeout, check=check
                )
                await self.message.remove_reaction(reaction.emoji, user)
                await self.controls[str(reaction.emoji)]()

            except asyncio.TimeoutError:
                await interaction.followup.send(
                    "Looks like you haven't responded in a while, so I'll assume you don't need this anymore. "
                    "You can rerun the command whenever you're ready to start again!"
                )
                await self.end_session()
                break


    async def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            await self.message.edit(embed=self.embeds[self.current_page])

    async def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.message.edit(embed=self.embeds[self.current_page])

    async def jump_to_page(self):
        prompt = await self.ctx.send("Which page would you like to jump to? (1 - {})".format(self.total_pages))

        def msg_check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        try:
            msg = await self.ctx.client.wait_for("message", timeout=30.0, check=msg_check)
            page = int(msg.content)

            if 1 <= page <= self.total_pages:
                self.current_page = page - 1
                await self.message.edit(embed=self.embeds[self.current_page])

            await prompt.delete()
            await msg.delete()

        except (asyncio.TimeoutError, ValueError):
            await prompt.delete()

    async def stop(self):
        await self.end_session()

    async def end_session(self):
        try:
            await self.message.clear_reactions()
        except discord.Forbidden:
            pass

        # Optional: Update the embed to show it's inactive
        embed = self.embeds[self.current_page]
        embed.set_footer(text="Session ended.")
        await self.message.edit(embed=embed)

def build_help_embeds():
    embeds = []

    # Page 1: Fun
    embed1 = discord.Embed(
        title="Fun",
        description="**Kill some time with these commands built for entertainment**",
        color=discord.Color.yellow(),
        timestamp=discord.utils.utcnow()
    )
    fun_fields = [
        {"name": "`/jokes`", "value": "The bot will tell you a joke", "inline": False},
        {"name": "`/token`", "value": "Print the bot's token", "inline": False},
        {"name": "`/magic_8_ball`", "value": "Ask anything to the magic 8 ball", "inline": False},
        {"name": "`/coinflip`", "value": "Flips a coin. As simple as that", "inline": False}
    ]
    for field in fun_fields:
        embed1.add_field(**field)
    embed1.set_footer(text="Page 1/4")
    embed1.set_thumbnail(url="https://images.emojiterra.com/google/android-11/512px/1f389.png")
    embeds.append(embed1)

    # Page 2: Functional
    embed2 = discord.Embed(
        title="**Functional Commands**",
        description="These commands bring some extra utility to the server",
        color=discord.Color.lighter_grey(),
        timestamp=datetime.datetime.now()
    )

    func_fields = [
        {"Name": "`/exchange`", "value": "Convert EUR into other currencies", "inline": False},
        {"Name": "`/ping`", "value": "Check the bot's ping and RAM usage", "inline": False},
        {"Name": "`/weather`", "value": "Check the weather in a given city", "inline": False},
        {"Name": "`/ask`", "value": "Uses AI to answer your questions", "inline": False},
        {"Name": "`/spotify`", "value": "Search Spotify without leaving Discord", "inline": False}
    ]

    for field in func_fields:
        embed2.add_field(name=field["Name"], value=field["value"], inline=field["inline"])

    embed2.set_footer(text="You are currently on page 2/4")
    embed2.set_thumbnail(url="https://files.catbox.moe/rj6dmf.png")

    embeds.append(embed2)

    # Page 3: Moderation
    embed3 = discord.Embed(
        title="Moderation",
        description="**Manage your server with these commands**",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )

    mod_fields = [
        {"Name": "`/clean`", "value": "Mass deletes unwanted messages", "inline": False}
    ]

    for field in mod_fields:
        embed3.add_field(name=field["Name"], value=field["value"], inline=field["inline"])

    embed3.set_footer(text="You are currently on page 3/4")
    embed3.set_thumbnail(url="https://files.catbox.moe/mi68gv.png")

    embeds.append(embed3)

    # Page 4: Miscellaneous

    embed4 = discord.Embed(
        title="Miscellaneous",
        description="**Where the odd ones out reside**",
        color=discord.Color.from_rgb(255,255,255),
        timestamp=datetime.datetime.now()
    )

    misc_fields = [
        {"Name": "`/owner`", "value": "Get in contact with the dev", "inline": False},
        {"Name": "`/donate`", "value": "Support this project", "inline": False}
    ]

    for field in misc_fields:
        embed4.add_field(name=field["Name"], value=field["value"], inline=field["inline"])

    embed4.set_footer(text="You are currently on page 4/4")
    embed4.set_thumbnail(url="https://files.catbox.moe/o4epmf.png")

    embeds.append(embed4)

    return embeds

@client.tree.command(name="help", description="Prints out a list of available commands")
async def help(interaction: discord.Interaction):
    await interaction.response.defer()

    embeds = build_help_embeds()
    
    # Single-page fallback
    if len(embeds) == 1:
        return await interaction.followup.send(embed=embeds[0])

    await interaction.followup.send("Paginator loading...", ephemeral=True)

    ctx = SimpleNamespace(
        client=client,
        author=interaction.user,
        channel=interaction.channel,
        send=interaction.channel.send
    )

    paginator = EmbedPaginator(ctx, embeds)
    await paginator.start()

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
@client.tree.command(name="ask", description="Get AI powered responses")
@app_commands.describe(prompt="The prompt to send")
async def ask(interaction: discord.Interaction, prompt: str):

    # check if ChatGPT is available
    if not openai_available:
        await interaction.response.send_message("Im sorry, but the AI integration is currently unavailable. 😔")

    await interaction.response.defer()

    try:
        
        if openai_available == False:
            await interaction.follow.send("API key not found. Please ensure that your .env file has the necessary key, or that it's being imported correctly.")
            return

        # send the prompt to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant, but keep it casual like amongst friends. Do not use more than 2k characters. Instead of writing a list, structure your response in a paragraph like you're personally talking to someone."
            }, {
                "role": "user",
                "content": prompt
            }],
            max_tokens=1000)

        answer = response.choices[0].message["content"]

        await interaction.followup.send(f"You asked:{prompt}\n Here's my thoughts on it: {answer}")

        # now time for a disclaimer
        await asyncio.sleep(2)
        await interaction.channel.send("With that said, there is a non-zero possibility my intel is outdated or i got things wrong.So please, fact check whatever i tell you.", 
        reference=None,allowed_mentions=discord.AllowedMentions.none()
        )
    
    except Exception as e:
        await interaction.followup.send(f"Sorry, i got an error: {str(e)}")

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

# ==== EVENTS =====
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")

    except Exception as e:
        print(e)

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