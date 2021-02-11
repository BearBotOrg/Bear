import discord
from discord.ext import commands
import asyncio
from libmeow.libmeow import Libsettings

class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.settings = Libsettings(self.client)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def joinlog(self, ctx, channel: discord.TextChannel):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.set_setting(ctx.message.guild, "joinlog", channel.id)
        await ctx.message.channel.send(f"**Successfully set join logs channel for {ctx.message.guild}.**")
        print(f"Join log channel changed on server {ctx.message.guild} to {channel}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remjoinlog(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.del_setting(ctx.guild, "joinlog")
        await ctx.message.channel.send("**Join logs has been disabled**")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def userlog(self, ctx, channel: discord.TextChannel):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.set_setting(ctx.message.guild, "userlog", channel.id)
        await ctx.message.channel.send(f"**Successfully set user logs channel for {ctx.message.guild}.**")
        print(f"User log channel changed on server {ctx.message.guild} to {channel}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remuserlog(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.del_setting(ctx.guild, "userlog")
        await ctx.message.channel.send("**User logs has been disabled**")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def rolelog(self, ctx, channel: discord.TextChannel):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.set_setting(ctx.message.guild, "rolelog", channel.id)
        await ctx.message.channel.send(f"**Successfully set role logs channel for {ctx.message.guild}.**")
        print(f"Mod log channel changed on server {ctx.message.guild} to {channel}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remrolelog(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.del_setting(ctx.guild, "rolelog")
        await ctx.message.channel.send("**Role logs has been disabled**")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def modlog(self, ctx, channel: discord.TextChannel):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return
        await self.settings.set_setting(ctx.message.guild, "modlog", channel.id)
        await ctx.message.channel.send(f"**Successfully set mod logs channel for {ctx.message.guild}.**")
        print(f"Mod log channel changed on server {ctx.message.guild} to {channel}.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remmodlog(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_guild:
            await ctx.message.channel.send("I need Manage Server in order to run this command")
            return

        await self.settings.del_setting(ctx.guild, "modlog")
        await ctx.message.channel.send("**Mod logs has been disabled**")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = await self.settings.get_setting(member.guild, "joinlog")
        channel = member.guild.get_channel(channel)
        if(channel == None):
            return
        embed = discord.Embed(title="Member Joined", description=f"{str(member)} has just joined the server.")
        embed.set_thumbnail(url=str(member.avatar_url))
        await channel.send(embed=embed)

    @commands.Cog.listener()    
    async def on_member_update(self, before, after):
        if(len(before.roles) < len(after.roles)):
            mchannel = await self.settings.get_setting(after.guild, "modlog")
            mchannel = after.guild.get_channel(mchannel)
            muterole = await self.settings.get_setting(after.guild, "muterole")
            try:
                muterole = after.guild.get_role(int(muterole))
            except:
                muterole = None
            if(mchannel == None):
                return
            # Role has been added
            act = "Role Added", "r"
            diff0 = list(set(after.roles) - set(before.roles))
            diff = []
            # Make sure all role instances are str
            for el in diff0:
                if(muterole == None or mchannel == None):
                    print(muterole, mchannel)
                    pass
                elif(el.name == muterole.name):
                    print("Got here")
                    # User got muted action as well
                    embed = discord.Embed(title="User Muted", description=f"**Member: ** {str(after)}\n**Action: **User Muted")
                    embed.set_thumbnail(url=str(after.avatar_url))
                    await mchannel.send(embed=embed)
                diff.append(el.name)
            rl = ', '.join(diff)
            embed = discord.Embed(title="Roles Update", description=f"**Member: ** {str(after)}\n**Action: **{act[0]}\n**Roles: ** {rl}")
            embed.set_thumbnail(url=str(after.avatar_url))
            await mchannel.send(embed=embed)
        if(len(before.roles) > len(after.roles)):
            channel = await self.settings.get_setting(after.guild, "rolelog")
            channel = after.guild.get_channel(channel)
            mchannel = await self.settings.get_setting(after.guild, "modlog")
            mchannel = after.guild.get_channel(mchannel)
            muterole = await self.settings.get_setting(after.guild, "muterole")
            try:
                muterole = after.guild.get_role(int(muterole))
            except:
                muterole = None
            if(channel == None):
                return
            # Role has been removed
            act = "Role Removed", "r"
            diff0 = list(set(before.roles) - set(after.roles))
            diff = []
            # Make sure all role instances are str
            for el in diff0:
                if(muterole == None or mchannel == None):
                    pass
                elif(el.name == muterole.name):
                    # User got unmuted action as well
                    embed = discord.Embed(title="User Unmuted", description=f"**Member: ** {str(after)}\n**Action: **User Unmuted")
                    embed.set_thumbnail(url=str(after.avatar_url))
                    await mchannel.send(embed=embed)
                diff.append(el.name)
            rl = ', '.join(diff)
            embed = discord.Embed(title="Roles Update", description=f"**Member: ** {str(after)}\n**Action: **{act[0]}\n**Roles: ** {rl}")
            embed.set_thumbnail(url=str(after.avatar_url))
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        mchannel = await self.settings.get_setting(guild, "modlog")
        mchannel = guild.get_channel(mchannel)
        if(mchannel == None):
            return
        if(isinstance(user, discord.Member)):
            r = []
            for role in user.roles:
                r.append(role.name)
            r = ", ".join(r)
        else:
            r = "No Role Information Is Present"
        embed = discord.Embed(title="Member Banned", description=f"**Member: ** {str(user)}\n**Roles: ** {r}")
        embed.set_thumbnail(url=str(user.avatar_url))
        await mchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        mchannel = await self.settings.get_setting(guild, "modlog")
        mchannel = guild.get_channel(mchannel)
        if(mchannel == None):
            return
        embed = discord.Embed(title="Member Unbanned", description=f"**Member: ** {str(user)}")
        embed.set_thumbnail(url=str(user.avatar_url))
        await mchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(0.5) # Wait for a while so discord.py updates guild stuff first
        # Before updating db, check if its actually a user leave
        if(member.guild.get_member(member.id)):
            return # This is a user join, ignore it
        channel = await self.settings.get_setting(member.guild, "joinlog")
        channel = member.guild.get_channel(channel)
        if(channel == None):
            return
        embed = discord.Embed(title="Member Left", description=f"**Member: ** {str(member)}")
        embed.set_thumbnail(url=str(member.avatar_url))
        await channel.send(embed=embed)
        

def setup(client):
    client.add_cog(Logs(client))
    print('Rootspring Logs has loaded successfully!')
        
