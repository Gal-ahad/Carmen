import discord, json, os, re, asyncio, datetime
from discord import app_commands
from discord.ext import commands

# Directories
MEDIA_FILTER_DIR = 'server_settings/media_filters'
FILTER_DIR = 'server_settings/filter_lists'
SERVER_CONFIG_DIR = 'server_settings/configs'

# Ensure all directories exist
for directory in [MEDIA_FILTER_DIR, FILTER_DIR, SERVER_CONFIG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Media types that can be filtered
MEDIA_TYPES = ['images', 'videos', 'links', 'files', 'embeds']

# Dictionary to store filter lists for each server
guild_filter_lists = {}

# Dictionary to store media filter settings for each server
guild_media_filters = {}

# Get the path for a specific server's media filter settings
def get_media_filter_path(guild_id):
    return os.path.join(MEDIA_FILTER_DIR, f'media_filter_{guild_id}.json')

# Get the path for a specific server's filter list
def get_filter_path(guild_id):
    return os.path.join(FILTER_DIR, f'filter_list_{guild_id}.json')

# Get the path for a specific server's config file
def get_server_config_path(guild_id):
    return os.path.join(SERVER_CONFIG_DIR, f'server_settings_{guild_id}.json')

# Load or create the media filter settings for a specific server
def load_media_filters(guild_id):
    file_path = get_media_filter_path(guild_id)
    
    try:
        with open(file_path, 'r') as f:
            media_filters = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default structure: {channel_id: {media_type: is_filtered}}
        media_filters = {}
        with open(file_path, 'w') as f:
            json.dump(media_filters, f, indent=2)
    return media_filters

# Load or create the filter list for a specific server
def load_filter_list(guild_id):
    file_path = get_filter_path(guild_id)
    
    try:
        with open(file_path, 'r') as f:
            filter_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        filter_list = []
        with open(file_path, 'w') as f:
            json.dump(filter_list, f, indent=2)
    return filter_list

async def initialize_server_filter(guild_id: int, guild_name: str = None) -> dict:
    config_file = get_server_config_path(guild_id)
    
    if os.path.exists(config_file):
        return {"created": False, "message": "Filter configuration already exists"}
    
    default_config = {
        "server_name": guild_name or f"Server_{guild_id}",
        "server_id": guild_id,
        "filters": {
            "links": False, "invites": False, "profanity": False,
            "spam": False, "caps": False, "mentions": False
        },
        "settings": {
            "log_channel": None, "ignore_admins": True, "ignore_mods": True
        },
        "created_at": str(datetime.datetime.now()),
        "last_updated": str(datetime.datetime.now())
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return {"created": True, "message": "Filter configuration created successfully"}
    except Exception as e:
        raise Exception(f"Failed to create filter configuration: {str(e)}")

# Command functions that will be added to the main bot
def setup_filter_commands(bot):

    # Add all filter commands to the bot
    
    @bot.tree.command(name="media_filter", description="Toggle filtering of specific media types in this channel.")
    @app_commands.describe(
        media_type="The type of media to filter (images, videos, links, files, embeds)",
        action="Turn the filter on or off"
    )
    @app_commands.choices(
        media_type=[
            app_commands.Choice(name="Images", value="images"),
            app_commands.Choice(name="Videos", value="videos"),
            app_commands.Choice(name="Links", value="links"),
            app_commands.Choice(name="Files", value="files"),
            app_commands.Choice(name="Embeds", value="embeds")
        ],
        action=[
            app_commands.Choice(name="On", value="on"),
            app_commands.Choice(name="Off", value="off")
        ]
    )
    async def filter_media(interaction: discord.Interaction, media_type: str, action: str):

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        if media_type not in MEDIA_TYPES:
            await interaction.response.send_message(f"Invalid media type. Choose from: {', '.join(MEDIA_TYPES)}", ephemeral=True)
            return

        guild_id = interaction.guild.id
        if guild_id not in guild_media_filters:
            guild_media_filters[guild_id] = load_media_filters(guild_id)
        
        media_filters = guild_media_filters[guild_id]
        channel_id = str(interaction.channel.id)
        
        if channel_id not in media_filters:
            media_filters[channel_id] = {}
        
        is_filtered = action.lower() == "on"
        media_filters[channel_id][media_type] = is_filtered
        
        with open(get_media_filter_path(guild_id), 'w') as f:
            json.dump(media_filters, f, indent=2)
        
        status = "enabled" if is_filtered else "disabled"
        await interaction.response.send_message(f"{media_type.capitalize()} filtering has been {status} in this channel.", ephemeral=False)

    @bot.tree.command(name="media_filter_status", description="Show the current media filter settings for this channel.")
    async def filter_media_status(interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        if not interaction.user.guild_permissions.administrator or interaction.user.guild.owner:
            await interaction.followup.send("❌ This command is not available to you", ephemeral=True)
            return

        guild_id = interaction.guild.id

        if guild_id not in guild_media_filters:
            guild_media_filters[guild_id] = load_media_filters(guild_id)
        
        media_filters = guild_media_filters[guild_id]
        channel_id = str(interaction.channel.id)
        
        embed = discord.Embed(
            title=f"Media Filter Status for #{interaction.channel.name}",
            description="Current media filter settings for this channel:",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        if channel_id not in media_filters:
            status_text = "No media filters are active in this channel."

        else:
            status_lines = []

            for media_type in MEDIA_TYPES:

                is_filtered = media_filters[channel_id].get(media_type, False)
                status = "🟢 Allowed" if not is_filtered else "🔴 Filtered"
                status_lines.append(f"**{media_type.capitalize()}**: {status}")

            status_text = "\n".join(status_lines)
        
        embed.add_field(name="Settings", value=status_text, inline=False)
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="filter_add", description="Add a word to the list of filtered words.")
    @app_commands.describe(word="The word to add to the filter list")
    async def add_to_filter(interaction: discord.Interaction, word: str):

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        if guild_id not in guild_filter_lists:
            guild_filter_lists[guild_id] = load_filter_list(guild_id)
        
        current_filter_list = guild_filter_lists[guild_id]
        
        if word.lower() in [w.lower() for w in current_filter_list]:
            await interaction.response.send_message("Word already in list.", ephemeral=True)
            return
        
        current_filter_list.append(word.lower())

        with open(get_filter_path(guild_id), 'w') as f:
            json.dump(current_filter_list, f, indent=2)
        
        await interaction.response.send_message(f"Added '{word}' to the filter list.", ephemeral=True)

    @bot.tree.command(name="filter_remove", description="Remove a word from the list of filtered words.")
    @app_commands.describe(word="The word to remove from the filter list")
    async def remove_from_filter(interaction: discord.Interaction, word: str):

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        if guild_id not in guild_filter_lists:
            guild_filter_lists[guild_id] = load_filter_list(guild_id)
        
        current_filter_list = guild_filter_lists[guild_id]
        word_lower = word.lower()
        matching_words = [w for w in current_filter_list if w.lower() == word_lower]
        
        if not matching_words:
            await interaction.response.send_message("Word not found in list.", ephemeral=True)
            return

        for match in matching_words:
            current_filter_list.remove(match)
        
        with open(get_filter_path(guild_id), 'w') as f:
            json.dump(current_filter_list, f, indent=2)
        
        await interaction.response.send_message(f"Removed '{word}' from the filter list.", ephemeral=True)

    @bot.tree.command(name="filter_list", description="Show the current list of filtered words.")
    async def show_filter(interaction: discord.Interaction):

        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to view the filter list.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        if guild_id not in guild_filter_lists:
            guild_filter_lists[guild_id] = load_filter_list(guild_id)
        
        current_filter_list = guild_filter_lists[guild_id]

        embed = discord.Embed(
            title="Filtered Words",
            description=f"These words are currently filtered from this server.",
            color=discord.Color.default(),
            timestamp=discord.utils.utcnow()
        )
        
        words_text = "\n".join(current_filter_list) if current_filter_list else "No filtered words"
        embed.add_field(name="Words", value=words_text, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Event listener to filter media based on settings
async def on_message_filter(message, client):
    if message.author == client.user:
        return
    
    if not message.guild:
        return

    guild_id = message.guild.id
    if guild_id not in guild_media_filters:
        guild_media_filters[guild_id] = load_media_filters(guild_id)
    
    media_filters = guild_media_filters[guild_id]
    channel_id = str(message.channel.id)

    if channel_id not in media_filters:
        await handle_word_filtering(message)
        return
    
    channel_settings = media_filters[channel_id]
    should_delete = False
    filtered_types = []
    
    # Check for images
    if channel_settings.get('images', False) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                should_delete = True
                filtered_types.append('images')
                break
    
    # Check for videos
    if channel_settings.get('videos', False) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('video/'):
                should_delete = True
                filtered_types.append('videos')
                break
    
    # Check for links
    def has_links(text):
        text_lower = text.lower()
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[a-zA-Z0-9.-]+\.[a-z]{2,}',
            r'[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|io|co|uk|de|fr|ru|jp|br|in|au|ca|nl|it|es|pl|ch|se|no|dk|fi|be|at|cz|hu|gr|pt|ie|ro|bg|hr|si|sk|lt|lv|ee|lu|mt|cy)\b',
        ]
        
        obfuscated_text = text_lower.replace('(dot)', '.').replace('[dot]', '.').replace(' dot ', '.')
        
        for pattern in url_patterns:
            if re.search(pattern, text_lower) or re.search(pattern, obfuscated_text):
                return True
        return False

    if channel_settings.get('links', False) and has_links(message.content):
        should_delete = True
        filtered_types.append('links')
    
    # Check for files
    if channel_settings.get('files', False) and message.attachments:
        for attachment in message.attachments:
            if not (attachment.content_type and (attachment.content_type.startswith('image/') or attachment.content_type.startswith('video/'))):
                should_delete = True
                filtered_types.append('files')
                break
    
    # Check for embeds
    if channel_settings.get('embeds', False) and message.embeds:
        should_delete = True
        filtered_types.append('embeds')
    
    if should_delete:
        try:
            await message.delete()
            types_str = ', '.join(filtered_types)
            await message.channel.send(
                f"{message.author.mention}, your message was deleted because {types_str} are not allowed in this channel.", 
                delete_after=10
            )
        except Exception as error:
            print(f"Failed to delete message or send notification: {error}")
    else:
        await handle_word_filtering(message)

# Separate function to handle word filtering
async def handle_word_filtering(message):
    guild_id = message.guild.id
    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]
    banned_words = [word for word in current_filter_list if word.lower() in message.content.lower()]
    
    if banned_words:
        try:
            await message.delete()
            print(f"Server {guild_id}: Deleted message containing banned words: {', '.join(banned_words)}")
        except Exception as error:
            print(f"Failed to delete message: {error}")

        try:
            await message.channel.send(
                f"{message.author.mention}, your message was deleted for containing prohibited material", 
                delete_after=10
            )
        except Exception as error:
            print(f"Failed to send reply to offending user: {error}")