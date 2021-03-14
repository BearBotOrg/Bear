import discord
from discord.ext import commands
from bearlib.corelib import Libsettings
yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

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


class CoronaTracker(commands.Cog):
    def __init__(self, client):
        self.client = client
    try:
        if(msg):
            pass
    except:
        msg = False

    @commands.Cog.listener()
    async def on_ready(self):
        covid_up = False # Until we get a better API
        while covid_up:
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
                await asyncio.sleep(10)
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
                    if do_event:
                        channel = guild.get_channel(cchannel)
                        if channel:
                            await cpri(client, channel, data_res, t)
                await asyncio.sleep(86400) # Use one hour to prevent ratelimits
            except:
                print("client error [corona]. Retrying in one hour")
                await asyncio.sleep(86400)


    #@commands.command()
    async def coronahelp(self, ctx):
        await ctx.message.channel.send(f"**All Coronavirus Data is provided by thevirustracker.com**\n**{ctx.prefix}setcoronachannel:** Set the channel for the tracker\n\nUnfortunately, due to rate limiting, we cannot allow individual coronatrack requests")

    #@commands.command()
    async def setcoronachannel(self, ctx, channel: discord.TextChannel):
        settings = Libsettings(self.client)
        await settings.set_setting(ctx.message.guild, "coronachannel", channel.id)
        await ctx.message.channel.send(f"**Successfully set coronavirus channel for {ctx.message.guild}.**")

def setup(client):
    client.add_cog(CoronaTracker(client))
    print("CoronaTracker is loaded")
