import random
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client



    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! `{round(self.client.latency * 1000)}ms`')



    @commands.command()
    async def rock(self, ctx):
        responses = ["Rock, we tied.",
                     "Paper, I win.",
                     "Scissors, you win!."]

        await ctx.send(random.choice(responses))



    @commands.command()
    async def paper(self, ctx):
        responses = ["Rock, you win!",
                     "Paper, we tied.",
                     "Scissors, I win."]

        await ctx.send(random.choice(responses))



    @commands.command()
    async def scissors(self, ctx):
        responses = ["Rock, I win.",
                     "Paper, you win!",
                     "Scissors, we tied."]

        await ctx.send(random.choice(responses))



    @commands.command()
    async def droll(self, ctx):
        responses = ['1',
                     '2',
                     '3',
                     '4',
                     '5',
                     '6']
        await ctx.send(random.choice(responses))



    @commands.command()
    async def cflip(self, ctx):
        responses = ['Heads',
                     'Tails']

        await ctx.send(random.choice(responses))



    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        responses = ['Yes',
                     'My sources say yes',
                     'Possibly',
                     'No',
                     "I don't know",
                     'Ask again later',
                     'Not a chance',
                     "I Don't think so"]

        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')



def setup(client):
    client.add_cog(Fun(client))
    print("Fun is loaded")
