import discord
from discord.ext import commands
import time
from libmeow.libmeow import Libsettings, Libprefix, Libeconomy, Libportfolio, Libquiz

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.settings = Libsettings(client)

    # 1 Message = 1 Point
    @commands.Cog.listener()
    async def on_message(self, message):
        if(message.content in ["", " "] or len(message.content) < 5):
            return 
        if(message.guild):
            prefix = Libprefix(self.client.db)
            prefix = await prefix.get_prefix(message)
            if(message.content.startswith(prefix[0])):
                return
            # Create a libeconomy object
            eco = Libeconomy(self.client)
            port = Libportfolio(self.client)
            if(message.author.bot):
                return
            await eco.add_points(message.author, 1)
            await eco.increment_msg_count(message.author, message.guild)
            msg_count = await port.get_curr_msg_count(message.author, message.guild)
            print(msg_count, message.content)
            user_guild_level = await port.get_curr_user_guild_level(await port.get_user_guild_portfolio(message.author, message.guild))
            print(user_guild_level)
            eco_rate = await port.get_economy_rate(await port.get_guild_portfolio(message.guild))
            channel = await self.settings.get_setting(message.guild, "lvlchannel")
            channel = message.guild.get_channel(channel)
            if msg_count*5 >= (user_guild_level + 1)**eco_rate:
                await eco.level_up_guild(message.author, message.guild)
                if channel == None:
                  channel = message.channel
                await channel.send("Author: " + str(message.author) + "\nLevel: " + str(user_guild_level + 1) + "\nGuild Economy Rate: " + str(eco_rate) + "\nUser Message Count: " + str(msg_count))
            return

    @commands.command()
    async def quiz(self, ctx):
        quiz = Libquiz(self.client, ctx.message)
        await quiz.random_question()

    # t is the type
    @commands.command()
    async def reward(self, ctx, t: str, parity: str = None):
        eco = Libeconomy(self.client)
        port = Libportfolio(self.client)
        print(t, "----------------------------------")
        if(parity != None):
            return await ctx.message.channel.send(f"**Invalid arguments**\nUse {ctx.prefix}reward <type> where type is hourly, daily or weekly. Note that hourly and daily and weekly are different so you can have all three rewards at the same time.")            
        if(type(t) == list or t not in ["hourly", "daily", "weekly"]):
            return await ctx.message.channel.send(f"**Invalid arguments**\nUse {ctx.prefix}reward <type> where type is hourly, daily or weekly. Note that hourly and daily and weekly are different so you can have all three rewards at the same time.")
        user_portfolio = await port.get_user_portfolio(ctx.author)
        if t == "hourly":
            time_check = 60*60
            money = 5
        elif t == "daily":
            time_check = 60*60*24
            money = 5*4
        elif t == "weekly":
            time_check = 60*60*24*7
            money = 5*8
        epoch = await eco.get_epoch(user_portfolio, "epoch_" + t)
        # Check if it has been one hour since last daily
        # 3600 seconds is one hour
        if(time.time() - epoch > time_check):
            await eco.add_money(ctx.author, money)
            await eco.update_epoch(ctx.author, "epoch_" + t)
            return await ctx.send(f"I have successully given you {str(money)} dollars of {t} money!")
        else:
            return await ctx.send(f"**Not Eligible**\nPlease wait for {3600 - (round(time.time() - epoch))} seconds and try again")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def lvlchannel(self, ctx, channel: discord.TextChannel):
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await ctx.send(f"**I must have Send Messages on channel: {str(channel)} in order to use this command")
        await self.settings.set_setting(ctx.guild, "lvlchannel", channel.id)
        return await ctx.send(f"**Successfully set the level channel for {ctx.guild}.**")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def remlvlchannel(self, ctx):
        await self.settings.del_setting(ctx.guild, "lvlchannel")
        return await ctx.message.channel.send("**Levelling messages has been disabled**")


def setup(client):
    client.add_cog(Economy(client))
    print('Bristlefrost Economy has loaded successfully!')
    

