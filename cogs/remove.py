import discord
import random
from discord.ext import commands
from bearlib.corelib import *

yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

class Remove(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def rolestop(self, ctx):
        settings = Libsettings(self.client)
        await settings.del_setting(ctx.message.guild, "autorole")
        await ctx.message.channel.send(f"Auto Roles for {ctx.message.guild} has been stopped")        

    @commands.command()
    async def levelstop(self, ctx):
        settings = Libsettings(self.client)
        await settings.del_setting(ctx.message.guild, "lvlchannel")        
        await ctx.message.channel.send(f"Leveling channel for {ctx.message.guild} has been stopped")

    @commands.command()
    async def coronastop(self, ctx):
        settings = Libsettings(self.client)
        await settings.del_setting(ctx.message.guild, "coronachannel")
        await ctx.message.channel.send(f"Corona updates for {ctx.message.guild} has been stopped")

    @commands.command()
    async def welcomestop(self, ctx):
        settings = Libsettings(self.client)
        await settings.del_setting(ctx.message.guild, "welcomechannel")
        await settings.del_setting(ctx.message.guild, "welcomemsg")
        
        await ctx.message.channel.send(f"Welcome messages for {ctx.message.guild} has been stopped")

def setup(client):
    client.add_cog(Remove(client))
    print("Remove is loaded")
