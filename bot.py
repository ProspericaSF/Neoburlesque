import discord
from discord.ext import commands, tasks
import asyncio
import pytz
from datetime import datetime, timedelta
import aiohttp

intents = discord.Intents.default()
intents.messages = True  # Enable message-related events

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    timezone = pytz.timezone('Australia/Sydney')
    # Calculate the delay until the next daily reset (rounded to the next nearest 10 minutes)
    now = datetime.now(timezone)
    remaining_seconds = (now.minute * 60 + now.second) % 600
    delay = 600 - remaining_seconds  # Calculate seconds until the next 10-minute mark

    await asyncio.sleep(delay)

    send_message.start()  # Start the task when the bot is ready

@tasks.loop(minutes=10)
async def send_message():
    channel_id = 1175962582780215296
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send("This is a message sent every 10 minutes!")
        await log_api_limit("Interval Check")

async def log_api_limit(message):
    channel_id = 1175962582780215296
    channel = bot.get_channel(channel_id)
    message_passed = message
    try:
        # Make a request to a rate-limited endpoint to get rate limit information
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/v10/channels/{channel_id}/messages', headers={'Authorization': f'Bot {bot.http.token}'}) as resp:
                # Extract rate limit information from headers
                retry_after = int(resp.headers.get('Retry-After', 0))
                limit = int(resp.headers.get('X-RateLimit-Limit', 0))
                remaining = int(resp.headers.get('X-RateLimit-Remaining', 0))

                reset_timestamp = resp.headers.get('X-RateLimit-Reset', 0)
                reset_timestamp = float(reset_timestamp)

                sydney_timezone = pytz.timezone('Australia/Sydney')
                reset_datetime = datetime.utcfromtimestamp(reset_timestamp).replace(tzinfo=pytz.utc).astimezone(sydney_timezone)
                reset_time_str = reset_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')

                # Calculate time remaining until reset
                current_time = datetime.now(sydney_timezone)
                time_until_reset = reset_datetime - current_time


                await channel.send(f"After: {message_passed}, Rate Limit Information - Limit: {limit}, Remaining: {remaining}, Retry After: {retry_after}, Reset Time: {reset_time_str}, Time Until Reset: {time_until_reset}")

    except discord.errors.HTTPException as e:
        # Handle other HTTP exceptions if needed
        await channel.send(f"HTTP Exception: {e}")

@bot.tree.command(name="commands")
async def commands_command(interaction: discord.Interaction):
    # Your code for the /tree commands goes here
    await interaction.response.send_message("List of commands goes here")

bot.run("MTEwMTExNzg0NDM2MTU4MDU4Ng.GGqBvZ.qVX7MZUwFaVaKqwzyZNgiZtMB_pMhlkCcZbnBU")