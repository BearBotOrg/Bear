import discord
import random
from discord.ext import commands
import asyncio
import os
import sys
from bearlib.corelib import Libquiz
yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

# Commands for owners
class BotAdmin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.in_quiz = False
        self.in_quiz_2 = False
        self.answer = ''
        self.quiz_q = ""
        self.p2 = False
        self.quiz_a = ""
        self.owners = client.config.BOT_ADMINS
    answer = ""

    @commands.command()
    async def quizadd(self, ctx):
        quiz = Libquiz(self.client, ctx.message)
        await quiz.add_qa_interactive(ctx.message, self.owners)

    @commands.command()
    async def quizlist(self, ctx):
        quiz = Libquiz(self.client, ctx.message)
        if(str(ctx.message.author.id) not in self.owners):
            await ctx.message.channel.send("**Error**\nOnly bot owners may view the quiz list")
            return
        questions = await quiz.get_questions_all() 
        msg = ""
        for question in questions:
            msg += f"**Question:** {question['quiz_question']}\n**Answer:** {question['quiz_answer']}\n"
        await ctx.send(msg)

def setup(client):
    client.add_cog(BotAdmin(client))
    print("Bot Admin Cog is loaded")

