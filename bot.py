import os
import discord
from discord import Client
from datetime import datetime
from collections.abc import Sequence
import time
from dotenv import load_dotenv
from discord.ext import commands

__author__ = "Pablo Schmeiser (pablau#2861)"
__copyright__ = "Copyright (C) 2022 Pablo Schmeiser"
__license__ = "GNU General Public License v3.0"
__version__ = "1.0.0"

# Stop reaction representative.
x = ":x:"

# Loading the bots token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Setting standard values and defining the bot with its command prefix
bot = commands.Bot(command_prefix="$")
# Setting client.
client = Client()

dateDict = {}

# Creates a Sequence
def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)

# Checks a message for a certain reaction.
def reaction_check(message=None, emoji=None, author=None, ignore_bot=True):
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)
    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check


# Starts clock on user given as String
@bot.command(pass_context=True)
async def start(ctx, user: discord.Member, arg):
    if (arg == "-m"):
        waitTime = 60
    elif (arg == "-h"):
        waitTime = 60 * 60
    elif (arg == "-d"):
        waitTime = 60 * 60 * 24
    elif (arg == "-w"):
        waitTime = 60 * 60 * 24 * 7
    
    await background_loop(ctx, waitTime, user)

# Loop running in the background.
async def background_loop(ctx, sec, user):
    await client.wait_until_ready()
    msg = await ctx.send("Bot started!")
    await msg.add_reaction(x)
    start = time.time()
    while not client.is_closed:
        res = await client.wait_for('reaction_add', check=reaction_check(message=msg, emoji=x))
        if res:  # not None
            await msg.edit(content="Bot stopped!")
            break
        else:
            if (time.time() >= start + sec):
                # Requests Datetime and converts to String
                date = datetime.now().strftime("%B/%d/%Y %H:%M")

                if (sec >= 60 * 60 * 24):
                    date = date.split(" ")[0]

                # Checks for months different in german and changes them to german. Also replaces event dates with events.
                if date.split(" ")[0] in dateDict:
                    date = dateDict[date.split(" ")[0]]
                elif "July" in date:
                    date = date.replace("July", "Juli")
                elif "January" in date:
                    date = date.replace("January", "Januar")
                elif "March" in date:
                    date = date.replace("March", "März")
                elif "May" in date:
                    date = date.replace("May", "Mai")
                elif "June" in date:
                    date = date.replace("June", "Juni")
                elif "December" in date:
                    date = date.replace("December", "Dezember")

                # Updates user asynchronously.
                await user.edit(nick = date)


# Adds an Event-Date Combination to the list of Events.
@bot.command(pass_context=True)
async def addEvent(ctx, date, event):
    try:
        date = datetime.strptime(date, "%d.%m.%Y").strftime("%B/%d/%Y")
        dateDict[date] = event
        await ctx.send("Event " + dateDict[date] + " successfully on Date: " + date)
    except:
        await ctx.send("Event has wrong format or could not be converted!")


# Prints all Event-Date Combinations.
@bot.command(pass_context=True)
async def showEvents(ctx):
    msg = await ctx.send("Events:")
    for key, value in dateDict.items():
        await msg.edit(content = content + "\n" + value + ", " + key)


# Shuts down the entire Bot Script.
@bot.command(pass_context=True)
@commands.is_owner()
async def shutdown(ctx):
    exit()


bot.run(TOKEN)
client.run(TOKEN)
