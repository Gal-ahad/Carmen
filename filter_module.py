import discord, json, os, re, asyncio, datetime
from discord import app_commands

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
    # Initialize filter configuration for a server if it doesn't exist.
    # Returns dict with 'created' boolean and any relevant info.
    
    config_file = get_server_config_path(guild_id)
    
    # Check if file already exists
    if os.path.exists(config_file):
        return {
            "created": False,
            "message": "Filter configuration already exists"
        }
    
    # Create default filter configuration
    default_config = {
        "server_name": guild_name or f"Server_{guild_id}",
        "server_id": guild_id,
        "filters": {
            "links": False,
            "invites": False,
            "profanity": False,
            "spam": False,
            "caps": False,
            "mentions": False
        },
        "settings": {
            "log_channel": None,
            "ignore_admins": True,
            "ignore_mods": True
        },
        "created_at": str(datetime.datetime.now()),
        "last_updated": str(datetime.datetime.now())
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        return {
            "created": True,
            "message": "Filter configuration created successfully"
        }
    
    except Exception as e:
        raise Exception(f"Failed to create filter configuration: {str(e)}")

async def get_server_filter_info(guild_id: int) -> dict:
    # Get information about a server's filter configuration.
    # Returns dict with 'exists' boolean and settings if available.
    config_file = get_server_config_path(guild_id)
    
    if not os.path.exists(config_file):
        return {
            "exists": False,
            "settings": {}
        }
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        return {
            "exists": True,
            "settings": config.get("filters", {}),
            "server_settings": config.get("settings", {}),
            "created_at": config.get("created_at"),
            "last_updated": config.get("last_updated")
        }
    
    except Exception as e:
        raise Exception(f"Failed to read filter configuration: {str(e)}")

def ensure_server_config_exists(guild_id: int, guild_name: str = None):
    """
    Synchronous version to ensure config exists (for use in existing code).
    Creates config file if it doesn't exist.
    """
    config_file = get_server_config_path(guild_id)
    
    if os.path.exists(config_file):
        return False  # Already exists
    
    default_config = {
        "server_name": guild_name or f"Server_{guild_id}",
        "server_id": guild_id,
        "filters": {
            "links": False,
            "invites": False,
            "profanity": False,
            "spam": False,
            "caps": False,
            "mentions": False
        },
        "settings": {
            "log_channel": None,
            "ignore_admins": True,
            "ignore_mods": True
        },
        "created_at": str(datetime.datetime.now()),
        "last_updated": str(datetime.datetime.now())
    }
    
    try:

        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return True  # Created new config

    except Exception as e:
        return False

# Set up moderation commands
def setup_moderation_commands(moderation_group, client):
    
    # Command to toggle media filters for a channel
    @client.tree.command(name="media_filter", description="Toggle filtering of specific media types in this channel.")
    @app_commands.describe(media_type="The type of media to filter (images, videos, links, files, embeds)",action="Turn the filter on or off")
    @app_commands.choices(media_type=[
            app_commands.Choice(name="Images", value="images"),
            app_commands.Choice(name="Videos", value="videos"),
            app_commands.Choice(name="Links", value="links"),
            app_commands.Choice(name="Files", value="files"),
            app_commands.Choice(name="Embeds", value="embeds")
        ],action=[app_commands.Choice(name="On", value="on"),app_commands.Choice(name="Off", value="off")])

        
    async def filter_media(interaction: discord.Interaction, media_type: str, action: str):

        # Check if the user has the admin role or is the server owner
        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        # Validate media type
        if media_type not in MEDIA_TYPES:
            await interaction.response.send_message(f"Invalid media type. Choose from: {', '.join(MEDIA_TYPES)}", ephemeral=True)
            return

        # Get or load media filter settings for this server
        guild_id = interaction.guild.id

        if guild_id not in guild_media_filters:
            guild_media_filters[guild_id] = load_media_filters(guild_id)
        
        media_filters = guild_media_filters[guild_id]
        
        # Convert channel ID to string for JSON compatibility
        channel_id = str(interaction.channel.id)
        
        # Initialize channel settings if needed
        if channel_id not in media_filters:
            media_filters[channel_id] = {}
        
        # Set the filter status
        is_filtered = action.lower() == "on"
        media_filters[channel_id][media_type] = is_filtered
        
        # Save the settings
        with open(get_media_filter_path(guild_id), 'w') as f:
            json.dump(media_filters, f, indent=2)
        
        status = "enabled" if is_filtered else "disabled"
        await interaction.response.send_message(f"{media_type.capitalize()} filtering has been {status} in this channel.", ephemeral=False)

    # Command to view current media filter settings for a channel
    @client.tree.command(name="media_filter_status", description="Show the current media filter settings for this channel.")
    async def filter_media_status(interaction: discord.Interaction):

        # Get or load media filter settings for this server
        guild_id = interaction.guild.id

        if guild_id not in guild_media_filters:
            guild_media_filters[guild_id] = load_media_filters(guild_id)
        
        media_filters = guild_media_filters[guild_id]
        
        # Convert channel ID to string for JSON compatibility
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

    # add to filter
    @client.tree.command(name="filter_add", description="Add a word to the list of filtered words.")
    @app_commands.describe(word="The word to add to the filter list")
    async def add_to_filter(interaction: discord.Interaction, word: str):

        # Check if the user has the admin role or is the server owner
        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        # Get or load the filter list for this server
        guild_id = interaction.guild.id
        if guild_id not in guild_filter_lists:
            guild_filter_lists[guild_id] = load_filter_list(guild_id)
        
        current_filter_list = guild_filter_lists[guild_id]
        
        # Add the word
        if word.lower() in [w.lower() for w in current_filter_list]:
            await interaction.response.send_message("Word already in list.", ephemeral=True)
            return
        
        current_filter_list.append(word.lower())
        with open(get_filter_path(guild_id), 'w') as f:
            json.dump(current_filter_list, f, indent=2)
        
        await interaction.response.send_message(f"Added '{word}' to the filter list.", ephemeral=True)

    @client.tree.command(name="filter_remove", description="Remove a word from the list of filtered words.")
    @app_commands.describe(word="The word to remove from the filter list")
    async def remove_from_filter(interaction: discord.Interaction, word: str):

        # Check if the user has the admin role or is the server owner
        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
            return

        # Get or load the filter list for this server
        guild_id = interaction.guild.id
        if guild_id not in guild_filter_lists:
            guild_filter_lists[guild_id] = load_filter_list(guild_id)
        
        current_filter_list = guild_filter_lists[guild_id]
        
        # Find the word (case-insensitive)
        word_lower = word.lower()
        matching_words = [w for w in current_filter_list if w.lower() == word_lower]
        
        if not matching_words:
            await interaction.response.send_message("Word not found in list.", ephemeral=True)
            return

        # Remove the word
        for match in matching_words:
            current_filter_list.remove(match)
        
        with open(get_filter_path(guild_id), 'w') as f:
            json.dump(current_filter_list, f, indent=2)
        
        await interaction.response.send_message(f"Removed '{word}' from the filter list.", ephemeral=True)

    @client.tree.command(name="filter_list", description="Show the current list of filtered words.")
    async def show_filter(interaction: discord.Interaction):

        # Check if the user has the admin role or is the server owner
        admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
        is_admin = (admin_role and admin_role in interaction.user.roles)
        is_owner = (interaction.user.id == interaction.guild.owner_id)
        
        if not (is_admin or is_owner):
            await interaction.response.send_message("You need to be the server owner or have the Admin role to view the filter list.", ephemeral=True)
            return

        # Get or load the filter list for this server
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

    # Register the commands with the client
    client.tree.add_command(moderation_group)
    
    return moderation_group

# Event listener to filter media based on settings
async def on_message_filter(message, client):

    # Skip messages from the bot itself
    if message.author == client.user:
        return
    
    # Skip if not in a guild
    if not message.guild:
        return

    # Load media filter settings for this server if needed
    guild_id = message.guild.id

    if guild_id not in guild_media_filters:
        guild_media_filters[guild_id] = load_media_filters(guild_id)
    
    media_filters = guild_media_filters[guild_id]
    
    # Skip if no filter settings for this channel
    channel_id = str(message.channel.id)

    if channel_id not in media_filters:
        # Continue with word filtering
        await handle_word_filtering(message)
        return
    
    channel_settings = media_filters[channel_id]
    
    # Check for various media types
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

        # Convert to lowercase for easier matching
        text_lower = text.lower()
        
        # Direct URL patterns
        url_patterns = [
            r'https?://[^\s]+',                    # Standard URLs
            r'www\.[a-zA-Z0-9.-]+\.[a-z]{2,}',    # www.domain.com
            r'[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|io|co|uk|de|fr|ru|jp|br|in|au|ca|nl|it|es|pl|ch|se|no|dk|fi|be|at|cz|hu|gr|pt|ie|ro|bg|hr|si|sk|lt|lv|ee|lu|mt|cy)\b',  # Common TLDs
        ]
        
        # Check for obfuscated dots
        obfuscated_text = text_lower.replace('(dot)', '.').replace('[dot]', '.').replace(' dot ', '.')
        
        # Check all patterns on both original and obfuscated text
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
    
    # Delete the message if it contains filtered media
    if should_delete:

        try:
            await message.delete()
            
            # Notify the user
            types_str = ', '.join(filtered_types)
            await message.channel.send(
                f"{message.author.mention}, your message was deleted because {types_str} are not allowed in this channel.", 
                delete_after=10
            )

        except Exception as error:
            print(f"Failed to delete message or send notification: {error}")

    else:
        # Continue with word filtering if media filtering didn't trigger
        await handle_word_filtering(message)

# Separate function to handle word filtering
async def handle_word_filtering(message):
    
    # Get or load the filter list for this server
    guild_id = message.guild.id

    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]
    
    # Check for banned words
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