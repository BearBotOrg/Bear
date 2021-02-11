import discord
from discord.ext import commands
from libmeow.libmeow import Libsettings
yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member, pass_context=True):
        settings = Libsettings(self.client)
        try:
            wchannel = int(await settings.get_setting(member.guild, "welcomechannel"))
        except:
            return
        wmsg = await settings.get_setting(member.guild, "welcomemsg")
        channel = member.guild.get_channel(wchannel)
        if(channel == None):
            return
        await channel.send(f"**{member.mention}** has just joined the server!\n{wmsg}")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcome(self, ctx, wmsg):
        settings = Libsettings(self.client)
        await settings.set_setting(ctx.message.guild, "welcomemsg", wmsg)
        await ctx.message.channel.send(f"**Successfully set welcome message for {ctx.message.guild}.**")
        print(f"Welcome message changed on server {ctx.message.guild} to {wmsg}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel):
        settings = Libsettings(self.client)
        await settings.set_setting(ctx.message.guild, "welcomechannel", channel.id)
        await ctx.message.channel.send(f"**Successfully set welcome channel for {ctx.message.guild}.**")
        print(f"Welcome channel changed on server {ctx.message.guild} to {channel}.")


def setup(client):
    client.add_cog(Welcome(client))
    print("Welcome is loaded")

