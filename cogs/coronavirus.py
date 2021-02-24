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
class CoronaTracker(commands.Cog):
    def __init__(self, client):
        self.client = client
    try:
        if(msg):
            pass
    except:
        msg = False

    @commands.command()
    async def coronahelp(self, ctx):
        await ctx.message.channel.send(f"**All Coronavirus Data is provided by thevirustracker.com**\n**{ctx.prefix}setcoronachannel:** Set the channel for the tracker\n\nUnfortunately, due to rate limiting, we cannot allow individual coronatrack requests")

    @commands.command()
    async def setcoronachannel(self, ctx, channel: discord.TextChannel):
        settings = Libsettings(self.client)
        await settings.set_setting(ctx.message.guild, "coronachannel", channel.id)
        await ctx.message.channel.send(f"**Successfully set coronavirus channel for {ctx.message.guild}.**")

def setup(client):
    client.add_cog(CoronaTracker(client))
    print("CoronaTracker is loaded")

