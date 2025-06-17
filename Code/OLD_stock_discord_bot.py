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

userid = ""
html_content = ""
in_stock = False
url = ''
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


BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"

bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())


def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def requestStock():
    msg = ""
    try:
        with requests.Session() as session:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                msg += "Status Code: " + str(response.status_code)
                html_content = response.text
                # print(html_content)
                
                with open("website.html", "a") as file:
                    file.write(html_content)
            else:
                msg += f"{userid} Failed to retrieve HTML content. Status code: {response.status_code}"
    except requests.RequestException as e:
        msg += f"Error fetching URL: {e}"
        
        
    match = re.search(r"'inStock':'(True|False)'", html_content)

    if match:
        in_stock_value = match.group(1)
        
        # Get inventoryCnt
        soup = BeautifulSoup(html_content, 'html.parser')
        inventory_span = soup.find('span', class_='inventoryCnt')

        
        if inventory_span:
            inventory_count_full_text = inventory_span.get_text(strip=True)
            
            # Use a regular expression to find all digits
            numbers = re.findall(r'\d+', inventory_count_full_text)
            
            if numbers:
                inventory_count = numbers[0] # Take the first number found
            else:
                inventory_count = "N/A" # Or handle cases where no number is found
                
            msg += userid + " " + datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> Inventory Count: " + inventory_count
        else:
            msg += userid + " " + datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> Inventory Count not found."
        
        # print(f"The value of 'inStock' is: {inventory_count}")
        
    else:
        msg += datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + " --> Out Of Stock"
        
    return msg

min = 300
max = 7200
low_bound = min
high_bound = max
target_channel = None
running = False


async def message_loop():
    global running
    next_time = time.time() + random.randint(low_bound, high_bound)

    while running and target_channel:
        current_time = time.time()

        if current_time >= next_time:
            msg = requestStock()
            await target_channel.send(f"{msg}")
            next_time = current_time + random.randint(low_bound, high_bound)

        await asyncio.sleep(0.5)

@bot.command()
async def link(ctx, inputURL: str):
    global url
    if (is_valid_url(inputURL)):
        url = inputURL
        await ctx.send(userid + " URL set!")
    else:
        await ctx.send("Invalid Link. Please enter a valid link!")


@bot.command()
async def start(ctx, low: int, high: int):
    user = ctx.author
    
    userid = f"<@{user.id}>"
    await ctx.send("User id: " + userid)
    
    
    """Starts sending messages at random intervals between low and high (in seconds)."""
    global low_bound, high_bound, target_channel, running

    if low < min or high > max or low > high:
        await ctx.send("Please provide valid numbers: low < high, low > 1800, high < 7200.")
        return

    low_bound = low
    high_bound = high
    target_channel = ctx.channel

    if not running:
        running = True
        await ctx.send(f"Starting messages between {low}s and {high}s intervals.")
        bot.loop.create_task(message_loop())
    else:
        await ctx.send("Already running! Use `!stop` to stop the loop first.")

@bot.command()
async def stop(ctx):
    """Stops sending messages."""
    global running
    if running:
        running = False
        await ctx.send("Stopped sending updates.")
    else:
        await ctx.send("Bot is not currently running.")




bot.run(BOT_TOKEN)




