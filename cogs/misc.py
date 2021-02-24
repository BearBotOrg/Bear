import discord
from discord.ext import commands
import asyncio
import datetime
import requests
from bearlib.corelib import Libsettings
from captcha.image import ImageCaptcha
import secrets
import string
yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.memcache = {}
        self.settings = Libsettings(self.client)

    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.guild):
            verifychannel = await self.settings.get_setting(message.guild, "verify_channel", table="guild_config")
            if verifychannel is not None:
                vc = client.get_channel(vc)
                await vc.purge(limit=3)

    @commands.command(pass_context=True)
    async def bitcoin(self, ctx):
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        response = requests.get(url)
        value = response.json()['bpi']['USD']['rate']
        await ctx.send(embed= discord.Embed(description= "Bitcoin price is: $" + value, colour= teal))


    @commands.command()
    async def time(self, ctx):
        now = datetime.now()

        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        await ctx.send(f"{date_time}")

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def captchamode(self, ctx, val):
        error = 0
        try:
            val = int(val)
        except:
            val = 2
            error = 1
        if(val not in [0, 1]):
            error = 1
        if(error):
            await ctx.message.channel.send("Error, invalid value for captcha verification\nPlease use 0 or 1")
        await self.settings.set_setting(ctx.guild, "captchaverify", val)
        await ctx.message.channel.send("Successfully changed mode of verification")


    @commands.command()
    async def verify(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.message.channel.send("I need Manage Roles in order to run this command")
            return
        member = ctx.message.author
        guild = ctx.message.guild
        if not guild:
            await ctx.author.send("Verify can only be used in a guild.")
        prefix = ctx.prefix
        role_id = await self.settings.get_setting(guild, "verifyrole")
        captchaverify = await self.settings.get_setting(guild, "captchaverify")
        if(role_id == None): 
            await ctx.message.channel.send(f"**Error**\nNo verified role has been setup. Please use {prefix}verifyrole <your verified role> to setup a verified role")
            return
        role = member.guild.get_role(int(role_id))
        if discord.utils.get(ctx.author.roles, name=str(role)):
            await ctx.send(f"{member.mention}, you are already verified.")
        else:
            # CAPTCHA Verification
            if(captchaverify == 1):
                token = ''.join((secrets.choice(string.ascii_lowercase + "0123456789") for i in range(6)))
                print(token)
                image = ImageCaptcha()
                data = image.generate(token)
                self.memcache[str(member.id)] = member.id, token
                await ctx.author.send(file=discord.File(data, f'captcha-{str(member.id)}.png'))
                await ctx.message.channel.send("I have attempted to send you a captcha. Make sure your DMs are open")
                msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == self.memcache[str(member.id)][0] and str(msg.channel.type) == "private")
                if(msg.content.lower() == self.memcache[str(member.id)][1]):
                    await ctx.author.add_roles(role)
                    await member.send(f'Thank you for verifying {member.mention}.')
                    self.memcache[str(member.id)] = None
                    return
                else:
                    await ctx.author.send(f"Invalid CAPTCHA. Please try again by reverifying using {ctx.prefix}verify again.")
                    return
            await ctx.author.add_roles(role)
            await ctx.send(f'Thank you for verifying {member.mention}.')

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def verifyrole(self, ctx, role: discord.Role):
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.message.channel.send("I need Manage Roles in order to run this command")
            return
        guild = ctx.message.guild
        print(guild)
        if(guild):
            gid = guild.id
        else:
            await ctx.message.channel.send("You can only set a verified role in a server.")
            return
        if(role == None):
            await ctx.message.channel.send(f"**Error**\nRole {role} was not found")
            return
        await self.settings.set_setting(guild, "verifyrole", role.id)
        await ctx.message.channel.send(f"**Successfully addded verified role for {guild}**\nNew Verified Role: {role}")

    @commands.command()
    async def userinfo(self, ctx, member : discord.Member):

        roles = [role for role in member.roles]

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.add_field(name="**User's status:**", value=f'User status is {member.status}')
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        embed.add_field(name="User's ID:", value=member.id)
        embed.add_field(name="User's name:", value=member.display_name)

        embed.add_field(name="Account Creation Date:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Join Date:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))
        embed.add_field(name="Top role:", value=member.top_role.mention)

        embed.add_field(name="Bot?", value=member.bot)

        await ctx.send(embed=embed)


    @commands.command()
    async def botsuggest(self, ctx, *, msg):
        user = ctx.author
        channel = self.client.get_channel(715284316271149076)
        embed = discord.Embed(
            colour = discord.Colour.orange()
        )
        embed.add_field(name="**Suggestion**", value="{}" .format(user) + " - " + " {}" .format(msg))
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.message.delete()
        await ctx.send("Your suggestion has been sent to the bot developer, F i j i. We always enjoy your suggestions!")
        message = await channel.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')



    @commands.command()
    async def stats(self, ctx):
        embed = discord.Embed(
            colour = discord.Colour.red()
        )

        embed.set_author(name='Some bot stats')
        embed.add_field(name='Amount of servers', value=f"I'm in " + str(len(self.client.guilds)) + " servers.", inline=False)
        embed.add_field(name='Amount of members', value=f"I'm helping {len([*self.client.get_all_members()])} members", inline=False)

        await ctx.send(embed=embed)



    @commands.command()
    async def vote(self, ctx):
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/690752908530155520/721216181406531694/fiji.png")
        embed.set_author(name='Vote for me!')
        embed.add_field(name='**Use this link to vote every 12 hours**', value='CURRENTLY UNAVALIABLE', inline=False)
        await ctx.send(embed=embed)



    async def __waterlinks__(dummy, self, ctx):
        embed = discord.Embed(
            colour = discord.Colour.blue()
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/690752908530155520/721216181406531694/fiji.png")
        embed.set_author(name='Helpful Links')
        embed.add_field(name='**Invite Me**', value='[Invite me to your server](https://discord.com/api/oauth2/authorize?client_id=710906959934783560&permissions=8&scope=bot)', inline=False)
        embed.add_field(name='**Join Our Support Server**', value='[Join our support server for support and exclusive benefits](https://discord.gg/KMAweuv)', inline=False)
        embed.add_field(name='**Add our bot now!**', value="Add our bot to your server now!", inline=False)

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        await self.__waterlinks__(self, ctx)
    @commands.command(pass_context=True)
    async def links(self, ctx):
        await self.__waterlinks__(self, ctx)

        
def setup(client):
    client.add_cog(Misc(client))
    print('Misc is loaded')

