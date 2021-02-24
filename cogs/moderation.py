import discord
from discord.ext import commands
import asyncio
from bearlib.corelib import Libsettings, Libwarn
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2


class Moderation(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.settings = Libsettings(self.client)

	@commands.command()
	@commands.has_guild_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.message.guild.me.guild_permissions.kick_members:
			await ctx.message.channel.send("I need Kick Members in order to run this command")
			return
		if (member.top_role >= ctx.author.top_role):
			await ctx.message.channel.send("You can only kick people below you")
			return
		try:
			if (reason == None):
				await member.send(
				    f"You have been kicked from server {member.guild}.\n There was no specified reason")
			else:
				await member.send(
				    f"You have been kicked from server {member.guild} for reason {reason}")
		except:
			await ctx.message.channel.send(
			    "{member} has his DM's turned off, but the specified action was still performed")
		await member.kick(reason=reason)
		if (reason == None):
			await ctx.send(
			    embed=discord.Embed(
			        description=
			        f'{member} has been kicked by {ctx.author}. There was no specified reason.',
			        color=teal))
			return
		await ctx.send(
		    embed=discord.Embed(
		        description=
		        f'User {member} has been kicked by {ctx.author} for {reason}!',
		        color=orange))

	@commands.command()
	@commands.has_guild_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.message.guild.me.guild_permissions.ban_members:
			await ctx.message.channel.send("I need Ban Members in order to run this command")
			return
		if (member.top_role >= ctx.author.top_role):
			await ctx.message.channel.send("You can only ban people below you")
			return
		try:
			if (reason == None):
				await member.send(
				    f"You have been banned from server {member.guild}.\n There was no specified reason"
				)
			else:
				await member.send(
				    f"You have been banned from server {member.guild} for reason {reason}"
				)
		except:
			await ctx.message.channel.send(
			    "{member} has his DM's turned off, but the specified action was still performed"
			)
		await member.ban(reason=reason)
		if (reason == None):
			await ctx.send(
			    embed=discord.Embed(
			        description=
			        f'{member} has been banned by {ctx.author}. There was no specified reason.',
			        color=teal))
			return
		await ctx.send(
		    embed=discord.Embed(
		        description=
		        f'User {member} has been banned by {ctx.author} for {reason}!',
		        color=red))

	@commands.command()
	@commands.has_guild_permissions(ban_members=True)
	async def unban(self, ctx, user_id):
		if not ctx.message.guild.me.guild_permissions.ban_members:
			await ctx.message.channel.send("I need Ban Members in order to run this command")
			return
		user = await self.client.fetch_user(int(user_id))
		await ctx.guild.unban(user)
		await ctx.message.channel.send(
		    embed=discord.Embed(
		        description=f'User with user id {user_id} has been unbanned!',
		        color=red))

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def mute(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		if (member.top_role >= ctx.author.top_role):
			await ctx.message.channel.send("You can only mute people below you") 
			return
		try:
			if (reason == None):
				await member.send(
				    f"You have been muted from server {member.guild}.\n There was no specified reason"
				)
			else:
				await member.send(
				    f"You have been muted from server {member.guild} for reason {reason}"
				)
		except:
			await ctx.message.channel.send(
			    f"{member} has his DM's turned off, but the specified action was still performed"
			)
		role_id = await self.settings.get_setting(ctx.message.guild, "muterole")
		if (role_id == None):
			await ctx.message.channel.send("**No muted role**\nPlease set a mute role using the muterole command")
			return
		try:
			role = member.guild.get_role(int(role_id))
		except:
			role = None
		if (role == None):
			await ctx.message.channel.send("**No muted role**\nPlease set a muted role using the muterole command")
			return
		if not member:
			await ctx.send(
			    embed=discord.Embed(
			        description="Please specify a member.", color=teal))
			return
		await member.add_roles(role)
		if (reason == None):
			await ctx.send(
			    embed=discord.Embed(
			        description=
			        f'{member} has been muted by {ctx.author}. There was no specified reason.',
			        color=teal))
			return
		await ctx.send(
		    embed=discord.Embed(
		        description=
		        f'{member} has been muted by {ctx.author} for {reason}.',
		        color=teal))

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def unmute(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		if (member.top_role >= ctx.author.top_role):
			await ctx.message.channel.send(
			    "You can only unmute people below you")
			return
		try:
			if (reason == None):
				await member.send(
				    f"You have been unmuted from server {member.guild}.\n There was no specified reason"
				)
			else:
				await member.send(
				    f"You have been unmuted from server {member.guild} for reason {reason}"
				)
		except:
			await ctx.message.channel.send(
			    f"{member} has his DM's turned off, but the specified action was still performed"
			)
		role_id = await self.settings.get_setting(ctx.message.guild,
		                                          "muterole")
		if (role_id == None):
			await ctx.message.channel.send(
			    "**No muted role**\nPlease set a muted role using the muterole command"
			)
			return
		role = member.guild.get_role(int(role_id))
		if (role == None):
			await ctx.message.channel.send(
			    "**No muted role**\nPlease set a muted role using the muterole command"
			)
			return
		if not member:
			await ctx.send(
			    embed=discord.Embed(
			        description="Please specify a member.", color=teal))
			return
		await member.remove_roles(role)
		await ctx.send(
		    embed=discord.Embed(
		        description=f'{member} has been unmuted by {ctx.author}',
		        color=teal))

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def tempmute(self, ctx, member: discord.Member, *,
	                   mute_time_and_reason):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		if (member.top_role >= ctx.author.top_role):
			await ctx.message.channel.send(
			    "You can only temporarily mute people below you")
			return
		mute_time_and_reason = mute_time_and_reason.split()
		mute_time = mute_time_and_reason[0]
		try:
			reason = mute_time_and_reason[1]
		except:
			reason = None
		mute_time = str(mute_time)
		if (mute_time[-1] == 's'):
			m = 1
			fn = "seconds"
		elif (mute_time[-1] == 'm'):
			m = 60
			fn = "minutes"
		elif (mute_time[-1] == 'h'):
			m = 60 * 60
			fn = "hours"
		elif (mute_time[-1] == 'd'):
			m = 60 * 60 * 24
			fn = "days"
		elif (mute_time[-1] == 'w'):
			m = 60 * 60 * 24 * 7
			fn = "weeks"
		else:
			await ctx.message.channel.send(
			    "**Error**\nInvalid mute time. Mute time must be a number followed by either s for second, m for minute, h for hour, d for day or w for week> You cannot use any unit of time greater than a week in a temporary mute\n**Usage**: tempmute <member> <mute time> <reason (optional)>"
			)
			return
		mute_time = mute_time[:-1]
		role_id = await self.settings.get_setting(ctx.message.guild,
		                                          "muterole")
		if (role_id == None):
			await ctx.message.channel.send(
			    "**No muted role**\nPlease set a muted role using the muterole command"
			)
			return
		try:
			if (reason == None):
				await member.send(
				    f"You have been temporarily muted from server {member.guild}.\n There was no specified reason"
				)
			else:
				await member.send(
				    f"You have been temporarily muted from server {member.guild} for reason {reason}"
				)
		except:
			await ctx.message.channel.send(
			    f"{member} has his DM's turned off, but the specified action was still performed"
			)
		role = member.guild.get_role(int(role_id))
		if (role == None):
			await ctx.message.channel.send(
			    "**No muted role**\nPlease set a muted role using the muterole command"
			)
			return
		if not member:
			await ctx.send(
			    embed=discord.Embed(
			        description="Please specify a member.", color=pink))
			return
		else:
			await member.add_roles(role)
			if (reason == None):
				await ctx.send(
				    embed=discord.Embed(
				        description=
				        f'{member} has been temporarily muted by {ctx.author} for {mute_time} {fn}. There was no specified reason.',
				        color=teal))
			else:
				await ctx.send(
				    f'{member} has been temporarily muted for {mute_time} {fn} by {ctx.author} for {reason}.'
				)
			await asyncio.sleep(int(mute_time) * m)
			await member.remove_roles(role)
			if (int(mute_time) == 1):
				fn = fn[:-1]
			await ctx.send(
			    embed=discord.Embed(
			        description=
			        f'User {member} has finished their temp mute punishment of {mute_time} {fn}.',
			        color=teal))

	@commands.has_permissions(manage_roles=True)
	@commands.command()
	async def muterole(self, ctx, role: discord.Role):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		guild = ctx.message.guild
		if (guild):
			pass
		else:
			await ctx.message.channel.send(
			    "You can only set a mute role in a server.")
			return
		drole = role
		if (drole == None):
			await ctx.message.channel.send(
			    f"**Error**\nRole {role} was not found")
			return
		await self.settings.set_setting(guild, "muterole", drole.id)
		await ctx.message.channel.send(
		    f"**Successfully addded mute role for {guild}**\nNew Mute Role: {role}"
		)

	@commands.command()
	@commands.has_guild_permissions(manage_messages=True)
	async def purge(self, ctx, amount=10):
		if not ctx.message.guild.me.guild_permissions.manage_messages:
			await ctx.message.channel.send("I need Manage Messages in order to run this command")
			return
		await ctx.message.channel.purge(limit=amount + 1)

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def warn(self, ctx, member: discord.Member, *, reason=None):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		warner = Libwarn(self.client, member, ctx.message.guild)
		if(reason == None):
			await ctx.message.channel.send("You need to provide a reason to warn someone")
			return
		await warner.add_warn(reason)
		await ctx.send(f"**Member Warned**\n{member.name} has been warned for {reason}.")
		await member.send(f"You have been warned in {str(member.guild)} for {reason}.")
		mchannel = await self.settings.get_setting(member.guild, "modlog")
		mchannel = member.guild.get_channel(mchannel)
		if(mchannel == None):
			# User doesn't want modlogs, dont do anything
			return
		embed = discord.Embed(title="User Warned", description=f"**Member: ** {str(member)}\n**Reason: **{reason}")
		embed.set_thumbnail(url=str(member.avatar_url))
		await mchannel.send(embed=embed)

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def delwarn(self, ctx, member: discord.Member, num):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		try:
			num = int(num)
		except:
			await ctx.send(f"Invalid case number")
		warner = Libwarn(self.client, member, ctx.message.guild)
		await warner.del_warn(ctx, num)
		await ctx.send(f"Successfully removed warning {str(num)}")
		mchannel = await self.settings.get_setting(member.guild, "modlog")
		mchannel = member.guild.get_channel(mchannel)
		if(mchannel == None):
			# User doesn't want modlogs, dont do anything
			return
		embed = discord.Embed(title="User Unwarned", description=f"**Member: ** {str(member)}\n**Warning: **{str(num)}")
		embed.set_thumbnail(url=str(member.avatar_url))
		await mchannel.send(embed=embed)

	@commands.command()
	@commands.has_guild_permissions(manage_guild=True)
	async def clearwarn(self, ctx, member: discord.Member):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		warner = Libwarn(self.client, member, ctx.message.guild)
		await warner.clear_warn()
		await ctx.send(f"Successfully cleared all warnings for {str(member)}")
		mchannel = await self.settings.get_setting(member.guild, "modlog")
		mchannel = member.guild.get_channel(mchannel)
		if(mchannel == None):
			# User doesn't want modlogs, dont do anything
			return
		embed = discord.Embed(title="User Warnings Cleared", description=f"**Member: **{str(member)}\n")
		embed.set_thumbnail(url=str(member.avatar_url))
		await mchannel.send(embed=embed)

	@commands.command()
	@commands.has_guild_permissions(mute_members=True)
	async def warnings(self, ctx, member: discord.Member):
		if not ctx.message.guild.me.guild_permissions.manage_roles:
			await ctx.message.channel.send("I need Manage Roles in order to run this command")
			return
		warner = Libwarn(self.client, member, ctx.message.guild)
		warns = await warner.list_warns()
		c = 1
		for i in warns:
			try:
				Rext = await warner.decomp_warn(i)
				await ctx.send(
				    f"**Warning {c}.**\n**Reason: ** {Rext[1]}\n**Time: ** {Rext[0]}"
				)
				c += 1
			except:
				await ctx.send(f"**{member.name} has no infractions**")

def setup(client):
	client.add_cog(Moderation(client))
	print('Moderation is loaded')
