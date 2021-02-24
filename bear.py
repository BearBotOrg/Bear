import asyncio
import uvloop
import discord
import random
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from discord.ext import commands
import os
import datetime
import requests
import secrets
import string
from config import ConfigBase, ConfigIntents
from config.ConfigBase import PG_USER as pg_user, PG_PWD as pg_pwd
from bearlib.corelib import Libprefix, setup_db, Libcommand, Libsettings
import uvicorn
import jishaku


purple = 0x161261
intents = discord.Intents.default() # Get all intents we can
intents.members = ConfigIntents.MEMBER_INTENT # Get member intent if we can
intents.presences = ConfigIntents.PRESENCE_INTENT
intents.members = True
client = commands.AutoShardedBot(command_prefix = "$", intents = intents, max_messages=10000) # Initial Client State

app = FastAPI()

@app.on_event("startup")
async def startup() -> None:
    global db, cache, lp, client
    db = await setup_db(pg_user, pg_pwd)
    lp = Libprefix(db)
    cache = {} # Empty cache initially
    client.command_prefix = lp.bot_get_prefix
    client.db = db
    client.prefix_cache = {} # The prefix is cached until bot reload
    client.remove_command('help')
    client.state_cache = {}
    client.state_cache_app = {}
    client.config = ConfigBase
    asyncio.create_task(client.start(client.config.BOT_TOKEN))
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("lib"):
            client.load_extension(f"cogs.{file[:-3]}")
    client.load_extension("jishaku")

def commaize(number: int) -> str:
    text = str(number)
    parts = text.split(".")
    ret = ""
    if len(parts) > 1:
        ret = "."
        ret += parts[1] # Apparently commas aren't used to the right of the decimal point. The -1 offsets to len() and 0 are because len() is 1 based but text[] is 0 based
    for i in range(len(parts[0]) - 1,-1,-1):
        # We can't just check (i % 3) because we're counting from right to left
        #  and i is counting from left to right. We can overcome this by checking
        #  len() - i, although it needs to be adjusted for the off-by-one with a -1
        # We also make sure we aren't at the far-right (len() - 1) so we don't end
        #  with a comma
        if (len(parts[0]) - i - 1) % 3 == 0 and i != len(parts[0]) - 1:
            ret = "," + ret
        ret = parts[0][i] + ret
    return ret

async def cpri(client, channel: discord.TextChannel, data_res: dict, time: str) -> None:
    if(data_res == "ERR_CONN_REFUSED"):
        embed = discord.Embed(description = f"__**Coronavirus Tracker for {time}**__\n**Error**\nCould not connect to the server", color = discord.Color.red())
        embed.set_footer(text = "All coroanvirus data is provided by TheVirusTracker.com")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/734701878767648788/745019513728139265/11296192.png")
    else:
        embed = discord.Embed(description = f"__**Coronavirus Tracker for {time}**__\n**Total Cases:**: {data_res['total_cases']}\n**Total Recovered:** {data_res['total_recovered']}\n**Total Unresolved**: {data_res['total_unresolved']}\n**Total Deaths:** {data_res['total_deaths']}\n**Total Affected Countries:** {data_res['total_affected_countries']}", color = discord.Color.red())
        embed.set_footer(text = "All coroanvirus data is provided by TheVirusTracker.com")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/734701878767648788/745019513728139265/11296192.png")

    await channel.send(embed=embed)

#@client.event
async def on_command_error(ctx, error):
    print(ctx, error)
    command = Libcommand(ctx.message, client.db)
    err = await command.error()
    try:
        if(err[0] == None or err[1] == None):
            return # No error, user isnt even running a valid command
    except:
        pass # Oops
    await ctx.message.channel.send(f"**{err[0]}**\n{err[1]}")

covid_up = False # COVID API is down

@client.event
async def on_ready(pass_context=True):
    print(client.user.name)
    print(client.user.id)
    print('------------------')
    while(covid_up == True):
        try:
            re = requests.get("https://thevirustracker.com/free-api?global=stats",timeout=5)
            data = re.json()
            data_res = data['results'][0]
            for key in data_res:
                element = data_res[key]
                if(type(element) == dict):
                    continue
                try:
                    element = commaize(int(element))
                except:
                    continue
            data_res[key] = element
        except:
            data_res = "ERR_CONN_REFUSED"
            await asyncio.sleep(5)
            continue # Force a wait of one hour to make sure server is up
        now = datetime.datetime.now()
        t = now.strftime("%m/%d/%Y, %H:%M:%S")
        try:
            for guild in client.guilds:
                s = Libsettings(client)
                cchannel = await s.get_setting(guild, "coronachannel") 
                try:
                    cchannel = int(cchannel)
                    do_event = True
                except:
                    do_event = False
                if(do_event):
                    for channel in guild.text_channels:
                        if(channel.name == f"{cchannel}" or str(channel.id) == f"{cchannel}"):
                            await cpri(client, channel, data_res, t)
            await asyncio.sleep(86400) # Use one hour to prevent ratelimits
        except:
            print("client error [corona]. Retrying in one hour")
            await asyncio.sleep(86400)

async def game_presence():
    while(True):
        try:
            await client.wait_until_ready()
            games = [">help", "Default prefix is >", "Playing Video Games"]
            while not client.is_closed():
                status = random.choice(games)
                await client.change_presence(activity=discord.Game(status))
                await asyncio.sleep(60*60*2) # Prevent rate limits
        except:
            print("client error [game_presence]. Retrying")
            await asyncio.sleep(60*60*2) # Prevent rate limits

client.loop.create_task(game_presence())
@client.command()
async def new(ctx):
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )

    embed.set_author(name='Aqua 1.0')
    embed.add_field(name='**coronastop, levelstop, welcomestop**', value='Stops level messages, welcome messages, and corona updates after you have enabled them', inline=False)
    embed.add_field(name='**setlevelchannel**', value="set a level channel for level up messages to be sent, not setting this up means it will not send level messages anywhere", inline=False)

    await ctx.send(embed=embed)


# FastAPI code

def get_token(length: str) -> str:
    secure_str = "".join(
        (secrets.choice(string.ascii_letters + string.digits) for i in range(length))
    )
    return secure_str

def error(*, code: str = None, html: str = None, support: bool = False, **kwargs: str) -> dict:
    eMsg = {"error_code": code, "context": kwargs}
    if html != None:
        eMsg["error_html"] = f"<p style='text-align: center; color: red'>{html}"
        if support is True:
            eMsg["error_html"] += "<br/>Contact Aqua Support for more information and support."
        eMsg["error_html"] += "</p>"
    return eMsg

async def user_from_token(token: str) -> Optional[str]:
  t = await client.db.fetchrow("SELECT uid from webtokens WHERE token = $1", str(token))
  if t == None:
    return None
  return str(t['uid'])



class TokenModel(BaseModel):
    token: str # Token for authentication/website authentication token

class AdminPrefixSet(TokenModel):
    gid: str # Workaround swagger issue with ints
    prefix: str # New Prefix

@app.get("/", tags = ["Documentation"])
async def root():
    return {
        "docs_swagger": "https://Aqua.cheesycod.repl.co/docs",
        "docs_redoc": "https://Aqua.cheesycod.repl.co/redocs",
        "endpoints": ["GET", "POST"],
        "/auth/token": {
            "desc": "Gets (or creates) a token",
            "users": "staff|website",
            "token_needed": 0,
            "methods": "GET"
        },
        "/auth/token/regenerate": {
            "desc": "Regenerates the token",
            "users": "everyone",
            "token_needed": 0,
            "methods": "GET"
        }, # DONE
        "/admin/prefix/set": {
            "desc": "Set the prefix",
            "users": "everyone",
            "token_needed": 1,
            "methods": "POST"
        }
    }


@app.get("/auth/token", tags = ["Authentication"])
async def auth_token(uid: int, webtoken: str) -> dict:
    uid = int(uid)
    if config.WEB_TOKEN != webtoken:
        return error(code = "INVALID_WEB_TOKEN", html = "Not Authorized.<br/>Please try logging in and out again")

    # Get a new token
    token = await client.db.fetchrow("SELECT token from webtokens WHERE uid = $1", str(uid))
    if token == None:
        flag = True
        while flag:
            token = get_token(128)
            token_check = await client.db.fetchrow("SELECT token from webtokens WHERE token = $1", token)
            if token_check == None:
                flag = False
        await client.db.execute("INSERT INTO webtokens (uid, token, perms) VALUES ($1, $2, $3)", str(uid), token, 0)
    else:
        token = token["token"]
    return error(code = None, token = token)

@app.get("/auth/token/regenerate", tags = ["Authentication"])
async def auth_token_regenerate(token: str, uid: int) -> dict:
    expected_uid = await user_from_token(token)
    if(str(uid) == str(expected_uid)):
        # Do it
        await client.db.execute("DELETE FROM webtokens WHERE token = $1", token)
        return error(code = None)
    return error(code = "UNEXPECTED_UID", html = "Unexpected User.<br/>Please try logging in and out again")

@app.post("/admin/prefix/set", tags = ["Admin"])
async def server_prefix_set(request: AdminPrefixSet):
        try:
            gid = int(request.gid)
        except:
            return error(code = "INVALID_GUILD", html = "This guild does not exist")
        uid = await user_from_token(request.token)
        if uid == None:
            return error(code = "INVALID_USER", html = "User could not be found. Please try logging in and logging out and then try again.")
        try:
            user = await client.fetch_user(uid)
        except:
            user = None
        if user == None:
            return error(code = "INVALID_USER", html = "User could not be found. Please try logging in and logging out and then try again.")
        guild = client.get_guild(gid)
        if guild == None:
            return error(code = "INVALID_GUILD", html = "This guild does not exist")
        member = guild.get_member(uid)
        if member != None and (member.guild_permissions.manage_guild or member.guild_permissions.administrator):
            return error(code = "FORBIDDEN", html = "You are not allowed to do this action")
        lprefix = Libprefix(client.db) # Create a Libprefix object
        await lprefix.set_prefix(guild, request.prefix)
        return error(code = None)
