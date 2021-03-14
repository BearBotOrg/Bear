import discord 
from discord.ext import commands 
from bearlib.corelib import Libsettings
from typing import List
class Autorole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member, pass_context=True):
        settings  = Libsettings(self.client)
        role_id = await settings.get_setting(member.guild, "autorole")
        try:
            role = member.guild.get_role(int(role_id))
            await member.add_roles(role)
        except:
            pass # Dont error here if there was an issue adding the role

    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def autorole(self, message, *args):
        """
            Sets up autorole AKA gives role to user when they join your server. Needs Manage Roles on the bot and Manage Server by the user trying to use the command. Allows a max of three roles
        """
        if not message.guild.me.guild_permissions.manage_roles:
            await message.channel.send("I need Manage Roles in order to run this command")
            return
        if(message.guild):
            pass
        else:
            await message.channel.send("You can only set an autorole in a server.")
            return
        settings  = Libsettings(self.client)
        role_lst = [int(role.replace('<', '').replace('>', '').replace('@', '').replace('&', '')) for role in args]
        role_lst_unique = []
        [role_lst_unique.append(x) for x in role_lst if x not in role_lst_unique]
        await settings.set_setting(message.guild, "auto_roles", role_lst)
        await message.send(f"**Successfully addded autorole for {message.guild}**\nNew Autorole: {str(role_lst_unique)}")

def setup(client):
    client.add_cog(Autorole(client))
    print('Rootspring Autoroles has loaded successfully!')
