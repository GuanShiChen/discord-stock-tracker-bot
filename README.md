# Discord Stock Tracker Bot

A Discord bot written in Python that monitors the stock of a specified item on a given webpage and notifies users in a Discord channel when the stock status changes or at set intervals.

---

## Table of Contents

-   [About the Bot](#about-the-bot)
-   [Features](#features)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Running the Bot](#running-the-bot)
-   [Bot Commands](#bot-commands)
-   [Configuration](#configuration)
-   [How it Works](#how-it-works)

---

## About the Bot

This Discord bot provides a convenient way to keep track of item availability on e-commerce websites. By simply providing a product URL, the bot will periodically check the page for stock information and send updates directly to your Discord channel. It's particularly useful for highly sought-after items that frequently go in and out of stock.

---

## Features

* **Real-time Stock Monitoring**: Continuously checks a specified URL for stock status.
* **Customizable Intervals**: Set random check intervals within a defined range to avoid detection.
* **Discord Notifications**: Sends messages directly to your chosen Discord channel.
* **Stock Count Extraction**: Attempts to extract and display the exact inventory count.
* **Easy-to-Use Commands**: Simple Discord commands to manage monitoring.

---

## Getting Started

Follow these instructions to get your Discord Stock Tracker Bot up and running.

### Prerequisites

Before you begin, ensure you have the following:

* **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
* **Discord Account**: You'll need a Discord account and a server where you have administrative privileges to add the bot.
* **Discord Bot Token**: You must create a new application on the [Discord Developer Portal](https://discord.com/developers/applications) and obtain a bot token.
    * **Enable Intents**: In your bot's settings on the Discord Developer Portal, under the "Bot" tab, make sure to enable the **"MESSAGE CONTENT INTENT"**, **"PRESENCE INTENT"**, and **"SERVER MEMBERS INTENT"** toggles. Without these, the bot may not function correctly.
* **Necessary Permissions**: Ensure the bot has permissions to send messages in the desired channels on your Discord server.

### Installation

1.  **Clone the repository**:

    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Install dependencies**:

    It's recommended to use a virtual environment.

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

    Then install the required Python libraries:

    ```bash
    pip install discord.py requests beautifulsoup4
    ```

### Running the Bot

1.  **Insert your Bot Token**:
    Open the `main.py` file (or whatever you named the script) and replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your actual Discord Bot Token:

    ```python
    # ...
    # Discord Bot Token
    # CHANGE THIS to your Bot's Token
    BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
    # ...
    ```

2.  **Run the script**:

    ```bash
    python3 stock_discord_bot.py
    ```

    Once the bot starts successfully, you'll see a message in your console similar to:

    ```
    Logged in as YourBotName (YourBotID)
    Bot is ready!
    ```

3.  **Invite the bot to your Discord server**:
    Go to the [Discord Developer Portal](https://discord.com/developers/applications), select your bot application, navigate to "OAuth2" -> "URL Generator". Select "bot" under "SCOPES" and then select the necessary permissions (e.g., "Send Messages", "Read Message History"). Copy the generated URL and paste it into your browser to invite the bot to your server.

---

## Bot Commands

Here's a list of commands you can use with the bot:

* `!link <URL>`: Sets the URL that the bot will monitor for stock.
    * **Example**: `!link https://www.bestbuy.com/product/example-item/12345.p`

* `!clearlink`: Clears the currently monitored URL.

* `!start <low_seconds> <high_seconds>`: Starts the stock monitoring. The bot will check for stock at random intervals between `low_seconds` and `high_seconds`.
    * `low_seconds`: Minimum interval in seconds (minimum 300 seconds or 5 minutes).
    * `high_seconds`: Maximum interval in seconds (maximum 7200 seconds or 2 hours).
    * **Example**: `!start 600 3600` (checks every 10 minutes to 1 hour)

* `!stop`: Stops the bot from sending stock update messages.

* `!settings`: Displays the current monitoring settings, including the URL, current status (running/stopped), and check interval.

---

## Configuration

You can adjust the following variables at the top of the `main.py` file:

* **`BOT_TOKEN`**: Your Discord bot's authentication token. **(Required)**
* **`HEADERS`**: HTTP headers used for web requests. These are set to mimic a standard browser to help avoid blocking. You generally won't need to change these unless specific websites require different headers.
* **`MIN_INTERVAL_SECONDS`**: The absolute minimum interval (in seconds) allowed for stock checks (default: 300 seconds / 5 minutes).
* **`MAX_INTERVAL_SECONDS`**: The absolute maximum interval (in seconds) allowed for stock checks (default: 7200 seconds / 2 hours).

---

## How it Works

The bot operates by:

1.  **Receiving Commands**: It listens for specific commands prefixed with `!`.
2.  **Setting URL**: When `!link` is used, it stores the provided URL.
3.  **Starting Loop**: When `!start` is issued with valid time bounds, it initiates an asynchronous loop.
4.  **Fetching Data**: Periodically, within the specified random interval, the bot sends an HTTP GET request to the monitored URL. It uses `requests` and custom headers to behave like a web browser.
5.  **Parsing HTML**: `BeautifulSoup` is used to parse the received HTML content. It specifically looks for:
    * A regular expression `'inStock':'True'` or `'inStock':'False'` to determine the stock status.
    * A `<span>` tag with the class `inventoryCnt` to extract the numerical inventory count.
6.  **Sending Notifications**: Based on the parsing results, the bot crafts a message and sends it to the Discord channel where the `!start` command was issued.
7.  **Loop Control**: The `!stop` command halts the monitoring loop.

---

## Picture

<img src="/Pictures/botMessages.png" alt="Bot Message"><br>
