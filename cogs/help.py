import discord
from discord.ext import commands
from libmeow.libmeow import Libprefix
from dpymenus import Page, PaginatedMenu
yellow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.p = Libprefix(self.client.pcur)

    @commands.command(pass_context=True)
    async def help(self, ctx):
        print("Got here")
        prefix = await self.p.get_prefix(ctx.message)
        # Economy Commands
        p1m = Page(title=f"Economy (Server Prefix: {prefix})", description='**Economy**')
        p2m = Page(title=f'Muting Users (Server Prefix: {prefix})', description='**Moderation**')
        p3m = Page(title=f"Warning Users (Server Prefix: {prefix})", description='**Moderation**')
        p4m = Page(title=f"Server Configuration (Server Prefix: {prefix})", description='**Moderation**')
        modval, mod1, mod2, eco = "", "", "", f'**{prefix}reward <type> -** Gives you your hourly/daily/weekly money! Have fun getting rich! Type is either hourly, daily or weekly\n**Example: {prefix}reward hourly**\n\n'
        # This person can mute others
        modval += f"**Basic Moderation Commands**\n\n"
        mod1 += f"**{prefix}tempmute <member> <mute time> <reason (optional)> -** Temporarily mutes a member with an optional reason for a specific amount of time\n**Example: {prefix}tempmute @Harry#0001 1h Spamming**\nNote: If the bot goes down for any reason, the person will stay muted until you unmute them\n\n"
        mod1 += f"**{prefix}mute <member> <reason (optional)> -** Mutes a member with an optional reason\n**Example: {prefix}mute @Harry#0001 'No Spamming'**\n\n"
        mod1 += f"**{prefix}unmute <member> <reason (optional)> -** Unmutes a member with an optional reason\n**Example: {prefix}unmute @Harry#0001 'He apologized'**\n\n"
        mod2 += f"**{prefix}warn <member> <reason> -** Warns a member\n**Example: {prefix}warn @Harry#0001 'No being toxic to other members'**\n\n"
        mod2 += f"**{prefix}delwarn <member> <case number> -** Deletes a warning for a member. Use {prefix}warnings to get the case number and then use this command to delete it\n**Example: {prefix}delwarn @Harry#0001 1**\n\n"
        mod2 += f"**{prefix}warnings <member> -** Returns a list of all warnings a member has\n**Example: {prefix}warnings @Harry#0001**\n\n"
        confval = ""
        confval += f"**muterole <role> -** Sets the role to give to muted users.\n**Example: {prefix}muterole @Muted**\n\n"
        confval += f"**autorole <role> -** Sets the role to give to users who just join your servers. Autorole with delay is coming soon....\n**Example: {prefix}autorole @MyRole**\n\n"
        confval += f"**captchamode <0/1> - **Enables or disables captcha-mode verification (in BETA).\n**Example: {prefix}captchamode 1**\n\n"


        p1m.add_field(name='**Page 1**', value=eco)
        p2m.add_field(name='**Page 2**', value=mod1)
        p3m.add_field(name='**Page 3**', value=mod2)
        p4m.add_field(name="**Page 4**", value=confval)
        menu = PaginatedMenu(ctx)
        menu.add_pages([p1m, p2m, p3m, p4m])
        menu.set_timeout(120)
        return await menu.open()

def setup(client):
    client.add_cog(Help(client))
    print('Help is loaded')

