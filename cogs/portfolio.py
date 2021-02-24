import discord
import random
from discord.ext import commands
import asyncio
import os
from random import randint
import datetime
import sched
import time
from bearlib.corelib import *
class Portfolio(commands.Cog):
    def __init__(self, client):
        self.client = client
    # 1 Message = 1 Point
    @commands.command()
    async def portfolio(self, message):
        port = Libportfolio(self.client)
        embeds = await port.gen_portfolio_embed(message.author, message.guild)
        for embed in embeds:
            if(embed != None):
                await message.channel.send(embed=embed)

def setup(client):
    client.add_cog(Portfolio(client))
    print('Bristlefrost Portfolio has loaded successfully!')
    
