from discord.ext import commands
from bearlib.corelib import *
class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def prefix(self, message, prefix):
        guild = message.guild
        if(guild):
            pass
        else:
            await message.send("You can only set prefix in a server.")
            return
        lprefix = Libprefix(self.client.pcur) # Create a Libprefix object
        await lprefix.set_prefix(guild, prefix)
        await message.send(f"**Successfully addded prefix for {guild}**\nNew Prefix: {prefix}")
        self.client.command_prefix = lprefix.bot_get_prefix

def setup(client):
    client.add_cog(Prefix(client))
    print('Rootspring Prefixes has loaded successfully!')
