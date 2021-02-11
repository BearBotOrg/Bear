import discord 
from discord.ext import commands 
from libmeow.libmeow import Libsettings
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
    async def autorole(self, message, role: discord.Role):
        if not message.guild.me.guild_permissions.manage_roles:
            await message.channel.send("I need Manage Roles in order to run this command")
            return
        if(message.guild):
            pass
        else:
            await message.channel.send("You can only set an autorole in a server.")
            return
        settings  = Libsettings(self.client)
        await settings.set_setting(message.guild, "autorole", role.id)
        await message.send(f"**Successfully addded autorole for {message.guild}**\nNew Autorole: {str(role)}")

def setup(client):
    client.add_cog(Autorole(client))
    print('Rootspring Autoroles has loaded successfully!')
