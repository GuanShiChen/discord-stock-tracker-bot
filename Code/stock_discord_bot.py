from discord.ext import commands
import discord
import requests
from datetime import datetime
import time
import random
import asyncio
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

# --- Configuration Variables ---
# Headers to use for HTTP requests to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# Discord Bot Token
# CHANGE THIS to your Bot's Token
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

# --- Bot Initialization ---
# Initialize the Discord bot with a command prefix and all intents
# Intents define which events your bot wants to receive from Discord.
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# --- Global State Variables for the Bot Loop ---
# Minimum and maximum allowed intervals for stock checking (in seconds)
# These are the constraints for the !start command.
MIN_INTERVAL_SECONDS = 300  # 5 minutes
MAX_INTERVAL_SECONDS = 7200 # 2 hours

# Current bounds for the random interval between stock checks
low_bound_seconds = MIN_INTERVAL_SECONDS
high_bound_seconds = MAX_INTERVAL_SECONDS

# The Discord channel where stock updates will be sent
target_channel = None

# Flag to control the running state of the stock checking loop
running = False

# The user ID to mention in stock update messages
current_user_mention = ""

# Default URL to monitor for stock
check_url = ""


# --- Helper Functions ---

def is_valid_url(url_string):
    """
    Checks if a given string is a valid URL.
    Args:
        url_string (str): The URL string to validate
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url_string)
        # Check if both scheme (http/https) and domain are present
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def request_stock_status():
    """
    Fetches the HTML content from the check_url, parses it to find stock information,
    and returns a formatted message.
    Returns:
        str: A message indicating the stock status and count
    """
    global check_url, current_user_mention
    msg = ""
    html_content = ""

    try:
        # Using requests session for better performance with multiple requests
        with requests.Session() as session:
            response = session.get(check_url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                html_content = response.text
            else:
                return (f"{current_user_mention} **Error:** Failed to retrieve HTML content from "
                        f"`{check_url}`. Status code: `{response.status_code}`.")
    except requests.exceptions.Timeout:
        return f"{current_user_mention} **Error:** Request to `{check_url}` timed out."
    except requests.RequestException as e:
        return f"{current_user_mention} **Error fetching URL:** `{e}`"

    # Find 'inStock' value using regex
    # Looks for 'inStock':'True' or 'inStock':'False'
    match_in_stock = re.search(r"'inStock':'(True|False)'", html_content)

    inventory_count = "N/A"
    current_time_str = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    # Use BeautifulSoup to parse the HTML for the inventory count
    soup = BeautifulSoup(html_content, 'html.parser')
    inventory_span = soup.find('span', class_='inventoryCnt')

    if inventory_span:
        inventory_count_full_text = inventory_span.get_text(strip=True)
        # Extract numbers from the inventory text
        numbers = re.findall(r'\d+', inventory_count_full_text)
        if numbers:
            inventory_count = numbers[0]  # Take the first number found
        else:
            inventory_count = "Not Found" # No number found in the inventory text
    else:
        inventory_count = "Span Not Found" # The inventoryCnt span was not found

    if match_in_stock:
        in_stock_value = match_in_stock.group(1)
        if in_stock_value == 'True':
            msg = (f"{current_user_mention} **{current_time_str}** -> "
                   f"**IN STOCK!** Inventory Count: **{inventory_count}**\n"
                   f"Link: <{check_url}>")
        else:
            msg = (f"{current_user_mention} **{current_time_str}** -> "
                   f"**Out Of Stock.** Inventory Count: {inventory_count}")
    else:
        msg = (f"{current_user_mention} **{current_time_str}** -> "
               f"Could not determine stock status. Inventory Count: {inventory_count}\n"
               f"Check page manually: <{check_url}>")
            
    return msg

async def message_loop():
    """
    The main asynchronous loop that periodically checks stock and sends messages
    to the target Discord channel.
    """
    global running, low_bound_seconds, high_bound_seconds, target_channel

    # Set the time for the first check
    next_check_time = time.time() + random.randint(low_bound_seconds, high_bound_seconds)

    while running and target_channel:
        current_system_time = time.time()

        if current_system_time >= next_check_time:
            # Perform the stock request to get the message
            status_message = await request_stock_status()
            await target_channel.send(status_message)
            
            # Calculate the time for the next check
            next_check_time = current_system_time + random.randint(low_bound_seconds, high_bound_seconds)
            
        await asyncio.sleep(1) # Check every second if it's time for the next message

# --- Discord Bot Commands ---

@bot.command(name='link')
async def set_link(ctx, input_url: str):
    """
    Sets the URL that the bot will monitor for stock.
    Usage: !link <URL>
    """
    global check_url
    if is_valid_url(input_url):
        check_url = input_url
        await ctx.send(f"{ctx.author.mention} **Success!** Monitoring URL updated to: <{check_url}>")
    else:
        await ctx.send(f"{ctx.author.mention} **Error:** Invalid Link. Please enter a valid URL (e.g., `https://example.com/product`).")

@bot.command(name='clearlink')
async def set_link(ctx):
    """
    Clears the URL the bot will monitor for stock.
    """
    global check_url
    check_url = ''
    await ctx.send(f"{ctx.author.mention} **Success!** Monitoring URL cleared.")

@bot.command(name='start')
async def start_monitoring(ctx, low: int, high: int):
    """
    Starts sending stock update messages at random intervals.
    Intervals are between 'low' and 'high' seconds.
    Usage: !start <low_seconds> <high_seconds>
    Example: !start 300 1800 (checks every 5 to 30 minutes)
    """
    global low_bound_seconds, high_bound_seconds, target_channel, running, current_user_mention

    # Set the user as the one who started the bot
    current_user_mention = ctx.author.mention
    
    # Validate the input intervals against the defined min/max allowed
    if low < MIN_INTERVAL_SECONDS or high > MAX_INTERVAL_SECONDS or low > high:
        await ctx.send(
            f"{ctx.author.mention} **Error:** Please provide valid numbers for the intervals:\n"
            f"- `low` must be at least `{MIN_INTERVAL_SECONDS}` seconds ({MIN_INTERVAL_SECONDS/60} minutes).\n"
            f"- `high` must be at most `{MAX_INTERVAL_SECONDS}` seconds ({MAX_INTERVAL_SECONDS/3600} hours).\n"
            f"- `low` must be less than or equal to `high`."
        )
        return

    if not is_valid_url(check_url):
        await ctx.send(
            f"{ctx.author.mention} **Error:** Please provide an item link using the `!link` command."
        )
        return

    low_bound_seconds = low
    high_bound_seconds = high
    target_channel = ctx.channel # Set the channel where the command was issued as the target

    if not running:
        running = True
        await ctx.send(
            f"{ctx.author.mention} **Starting stock monitoring!**\n"
            f"Updates will be sent to this channel every **{low_bound_seconds}** to **{high_bound_seconds}** seconds.\n"
            f"Monitoring URL: <{check_url}>"
        )
        # Create and start the background task for the message loop
        bot.loop.create_task(message_loop())
    else:
        await ctx.send(f"{ctx.author.mention} **Alert:** Monitoring is already running! Use `!stop` to stop the loop first, then `!start` again.")

@bot.command(name='stop')
async def stop_monitoring(ctx):
    """
    Stops the bot from sending stock update messages.
    Usage: !stop
    """
    global running
    if running:
        running = False
        await ctx.send(f"{ctx.author.mention} **Stopped** sending stock updates.")
    else:
        await ctx.send(f"{ctx.author.mention} **Info:** The bot is not currently running.")

@bot.command(name='settings')
async def show_settings(ctx):
    """
    Displays the current monitoring settings (URL and interval).
    Usage: !settings
    """
    global check_url, low_bound_seconds, high_bound_seconds
    status_message = "Currently **running**." if running else "Currently **stopped**."
    
    await ctx.send(
        f"{ctx.author.mention} **Current Monitoring Settings:**\n"
        f"- **Status:** {status_message}\n"
        f"- **Monitoring URL:** <{check_url}>\n"
        f"- **Check Interval:** Every `{low_bound_seconds}` to `{high_bound_seconds}` seconds."
    )

# --- Bot Event Handlers ---

@bot.event
async def on_ready():
    """
    Event listener that fires when the bot successfully connects to Discord.
    """
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready!')

# --- Run the Bot ---
bot.run(BOT_TOKEN)
