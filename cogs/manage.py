import discord
import random
from discord.ext import commands
import asyncio
import os
import sys
from libmeow.libmeow import *
yerllow = 0xFBFC7F
green = 0x19CC1C
blue = 0x00BFFF
purple = 0x6E33FF
orange = 0xFEB50E
teal = 0x9BF2EA
red = 0xFF0000
pink = 0xF32EE2

# Commands for owners
class Manage(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.settings = Libsettings(client)
        self.ms = {}
        self.memcache = {}
        self.client.state_cache_app = {}
        self.port = Libportfolio(client)

    @commands.command()
    @commands.has_guild_permissions(manage_channels=True)
    async def newchannel(self, ctx, name, category: discord.CategoryChannel=None):
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.message.channel.send("I need Manage Channels in order to run this command")
            return
        await ctx.guild.create_text_channel(name, category=category)
    @commands.command()
    @commands.has_guild_permissions(manage_channels=True)
    async def delchannel(self, ctx, channel: discord.TextChannel, reason=None):
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.message.channel.send("I need Manage Channels in order to run this command")
            return
        await channel.delete(reason=reason)
 
    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def appadd(self, ctx, question):
        app = Libstaffapplication(self.client, ctx.guild)
        await app.add_question(question, None)
        await ctx.send(f"Done adding question to staff application.")

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def appcadd(self, ctx, qid, check):
        app = Libstaffapplication(self.client, ctx.guild)
        rc = await app.add_check(qid, check)
        if rc == "NO_QUESTIONS_IN_GUILD":
            await ctx.send(f"Could not add check to that staff application question as it does not exist")
            return
        await ctx.send(f"Done adding check to that staff application question")

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def appdel(self, ctx, qid):
        app = Libstaffapplication(self.client, ctx.guild)
        rc = await app.remove_question(qid)
        if rc == "NO_QUESTIONS_IN_GUILD":
            await ctx.send(f"Could not remove that staff application question as it does not exist")
        await ctx.send(f"Done removing question with that qid")

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def applist(self, ctx):
        app = Libstaffapplication(self.client, ctx.guild)
        ql = await app.list_questions()
        await ctx.send(ql)
    
    @commands.command()
    async def apply(self, ctx):
        # Get the state first
        if(self.client.state_cache.get(str(ctx.author.id))):
            pass
        else:
            up = await self.port.get_user_portfolio(ctx.author)
            self.client.state_cache[str(ctx.author.id)] = up[0]["mm_state"]
        state = self.client.state_cache[str(ctx.author.id)]
        if(state != 0 and state != None):
            # We are already in a modmail, do nothing
            await ctx.author.send("You cannot do a staff application while being in a modmail")
            return
        if(self.client.state_cache_app.get(str(ctx.author.id))):
            pass
        else:
            self.client.state_cache_app[str(ctx.author.id)] = 0 # Initial value
        if(self.client.state_cache_app[str(ctx.author.id)] == 1):
            await ctx.author.send("You cannot do a staff application while you are already in the middle of a staff application")    
            return        
        err = 0
        # Lets apply for staff!!!
        if not ctx.guild:
            # Get all mutual servers with the user
            mutuals = []
            for guild in self.client.guilds:
                if(guild.get_member(ctx.author.id) == None):
                    continue
                mutuals.append(guild)
            # Now that we have every mutual server, ask the user to choose which one 
            if(len(mutuals) == 1):
                guild = mutuals[0]
            m = ""
            i = 1

            for mutual in mutuals:
                m += f"**{i}.** {str(mutual)}\n"
                i+=1

            await ctx.author.send(f"**Please choose the guild you wish to start a staff application with**: \n\n{m}")
            msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == ctx.author.id and str(msg.channel.type) == "private")
            try:
                guild = mutuals[int(msg.content) - 1]
                self.client.state_cache_app[str(ctx.author.id)] = guild.id
            except ValueError:
                await ctx.author.send("Invalid guild. Please try again with $start and a proper guild.")
                self.client.state_cache_app[str(ctx.author.id)] = 0
                return
            ctx.guild = guild
            self.client.nog = True
        else:
            self.client.nog = False
        self.ms[str(ctx.author.id)] = []
        self.memcache[str(ctx.author.id)] = ctx.author.id, None
        applychannel = ctx.guild.get_channel(await self.settings.get_setting(ctx.guild, "applychannel"))
        if(applychannel == None):
            await ctx.send(f"An application channel has not been set. Please set it using {ctx.prefix}applychannel CHANNEL")
            return
        app = Libstaffapplication(self.client, ctx.guild)
        ql = await app.list_questions() # Get all the questions
        q = 0
        self.client.state_cache_app[str(ctx.author.id)] = 1 # Begin a staff app now
        if(self.client.nog == False):
            await ctx.send("Sent you a DM to start your application. Good luck!")
        await ctx.author.send(f"You are now starting a staff application on {str(ctx.guild)}\nIf you wish to stop at anytime, type stop to do so.")
        while(q < len(ql)):
            qa = ql[q] # get question
            await ctx.author.send(f"**{qa['question']}**")
            msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == self.memcache[str(ctx.author.id)][0] and str(msg.channel.type) == "private") # Wait for a message
            if(msg.content == "stop"):
                self.client.state_cache_app[str(ctx.author.id)] = 0 # Bye Bye!
                await ctx.author.send("Cancelled your application successfully!")
                return
            # Get the qcheck for the question
            # Examples of checks: int:0:13:stop:You must be over 13 years old to be a member
            if(qa["qcheck"] == None or qa["qcheck"].startswith("none")):
                self.ms[str(ctx.author.id)].append([qa['question'], msg.content])
                q += 1
                continue # Next question pls
            # The int check
            if(qa["qcheck"].startswith("int")):
                try:
                    intd = int(msg.content)
                    strd = None
                    err = 0
                except ValueError:
                    err = 1
            # The strint check
            elif(qa["qcheck"].startswith("strint")):
                try:
                    intd = int(msg.content)
                    strd = str(msg.content)
                    intd = None
                    err = 0
                except ValueError:
                    err = 1
            # The str check (only strings allowed, not ints)
            elif(qa["qcheck"].startswith("str")):
                try:
                    intd = int(msg.content)
                    err = 1
                except ValueError:
                    intd = None
                    strd = str(msg.content)
                    err = 0
            # Theres more, now check the indices in the check using : seperator
            spi = qa["qcheck"].split(":")
            # Abort early if an error occurred based on the last indice
            if(err != 0):
                fallback = spi[-1]
                try:
                    fallback = int(fallback)
                    fallback = f"Fallback error for check {qa['qcheck']}"
                except ValueError:
                    pass
                await ctx.author.send(fallback)
                if(spi[-2] == "stop"):
                    self.client.state_cache_app[str(ctx.author.id)] = 0 # Initial value
                    return # Stop execution
                continue # Without going to the next question pls

            if(len(spi) == 1):
                pass # We are good
            elif(len(spi) > 1):
                try:
                    spi[1] = int(spi[1])
                    # We have more one indice, check that content are less that first indice using intd or strd
                    if(intd == None):
                        # We are a string, check its length
                        if(len(strd) > spi[1]):
                            err = 0 # We re still good
                        else:
                            err = 1 # Now we're not
                    else:
                        # We are an int, check its length
                        if(intd > spi[1]):
                            err = 0
                        else:
                            err = 1
                except ValueError:
                    pass # Didn't do the check
            if(err != 0): # Abort again
                fallback = spi[-1]
                try:
                    fallback = int(fallback)
                    fallback = f"Fallback error for check {qa['qcheck']}"
                except ValueError:
                    pass
                if(spi[-2] == "stop"):
                    self.client.state_cache_app[str(ctx.author.id)] = 0 # Initial value
                    return
                await ctx.author.send(fallback)
                continue # Without going to the next question pls            
            if(len(spi) > 2):
                try:
                    spi[2] = int(spi[2])
                    # We have a second indice to check
                    if(intd == None):
                        # We are a string, check its length
                        if(len(strd) <= spi[2]):
                            err = 0 # We re still good
                        else:
                            err = 1 # Now we're not
                    else:
                        # We are an int, check its length
                        if(intd <= spi[2]):
                            err = 0
                        else:
                            err = 1
                except ValueError:
                    pass            
            if(err != 0): # Abort again
                fallback = spi[-1]
                try:
                    fallback = int(fallback)
                    fallback = f"Fallback error for check {qa['qcheck']}"
                except ValueError:
                    pass
                if(spi[-2] == "stop"):
                    self.client.state_cache_app[str(ctx.author.id)] = 0 # Initial value
                    return
                await ctx.author.send(fallback)
                continue # Without going to the next question pls   
            
            # Finally with all checks satisfied, add it to m and move on
            self.ms[str(ctx.author.id)].append([qa['question'], msg.content])
            q += 1
            continue # Next question pls
        t, editmsg = 0, 0
        while(t == 0):
            if(editmsg == 0):
                await ctx.author.send("Ready to submit?\nType submit to submit your staff application\nType edit to edit a question\nType stop to stop or cancel your application")
                msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == self.memcache[str(ctx.author.id)][0] and str(msg.channel.type) == "private") # Wait for a message
            if(msg.content.lower() == "submit"):
                t = 1
                continue
            if(msg.content.lower() == "stop"):
                self.client.state_cache_app[str(ctx.author.id)] = 0 # Bye Bye!
                await ctx.author.send("Cancelled your application successfully!")
                return
            if(msg.content.lower() == "edit" or editmsg == 1):
                # Ask which question
                await ctx.author.send("Which question would you like to edit (by number). Type exit to return to the submit menu")
                msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == self.memcache[str(ctx.author.id)][0] and str(msg.channel.type) == "private") # Wait for a message
                if(msg.content.lower() == "exit"):
                    editmsg = 0
                    continue
                try:
                    ct = int(msg.content)
                except ValueError:
                    await ctx.author.send("Invalid question")
                    editmsg = 1
                    continue
                try:
                    await ctx.author.send(f"**{self.ms[str(ctx.author.id)][ct - 1][0]}**\nPlease type your editted answer now")
                except IndexError:
                    await ctx.author.send("Invalid question")
                    editmsg = 1
                    continue                    
                msg = await self.client.wait_for('message', check=lambda msg: msg.author.id == self.memcache[str(ctx.author.id)][0] and str(msg.channel.type) == "private") # Wait for a message
                # Check the answer using the checks again
                ## CHECKS Begin

                qa = ql[ct - 1]
                # Examples of checks: int:0:13:stop:You must be over 13 years old to be a member
                if(qa["qcheck"] == None or qa["qcheck"].startswith("none")):
                    self.ms[str(ctx.author.id)][ct - 1][1] = msg.content
                    cp = 1
                else:
                    cp = 0
                # The int check
                if(qa["qcheck"].startswith("int")):
                    try:
                        intd = int(msg.content)
                        strd = None
                        err = 0
                    except ValueError:
                        err = 1
                # The strint check
                elif(qa["qcheck"].startswith("strint")):
                    try:
                        intd = int(msg.content)
                        strd = str(msg.content)
                        intd = None
                        err = 0
                    except ValueError:
                        err = 1
                # The str check (only strings allowed, not ints)
                elif(qa["qcheck"].startswith("str")):
                    try:
                        intd = int(msg.content)
                        err = 1
                    except ValueError:
                        intd = None
                        strd = msg.content
                        err = 0
                # Theres more, now check the indices in the check using : seperator
                spi = qa["qcheck"].split(":")
                # Abort early if an error occurred based on the last indice
                if(err != 0):
                    fallback = spi[-1]
                    try:
                        fallback = int(fallback)
                        fallback = f"Fallback error for check {qa['qcheck']}"
                    except ValueError:
                        pass
                    await ctx.author.send(fallback)
                    editmsg = 1
                    continue # Without going to the next question pls

                if(len(spi) == 1):
                    pass # We are good
                elif(len(spi) > 1):
                    try:
                        spi[1] = int(spi[1])
                        # We have more one indice, check that content are less that first indice using intd or strd
                        if(intd == None):
                            # We are a string, check its length
                            if(len(strd) > spi[1]):
                                err = 0 # We re still good
                            else:
                                err = 1 # Now we're not
                        else:
                            # We are an int, check its length
                            if(intd > spi[1]):
                                err = 0
                            else:
                                err = 1
                    except ValueError:
                        pass # Didn't do the check
                if(err != 0): # Abort again
                    fallback = spi[-1]
                    try:
                        fallback = int(fallback)
                        fallback = f"Fallback error for check {qa['qcheck']}"
                    except ValueError:
                        pass
                    editmsg = 1
                    await ctx.author.send(fallback)
                    continue       
                if(len(spi) > 2):
                    try:
                        spi[2] = int(spi[2])
                        # We have a second indice to check
                        if(intd == None):
                            # We are a string, check its length
                            if(len(strd) <= spi[2]):
                                err = 0 # We re still good
                            else:
                                err = 1 # Now we're not
                        else:
                            # We are an int, check its length
                            if(intd <= spi[2]):
                                err = 0
                            else:
                                err = 1
                    except ValueError:
                        pass            
                if(err != 0): # Abort again
                    fallback = spi[-1]
                    try:
                        fallback = int(fallback)
                        fallback = f"Fallback error for check {qa['qcheck']}"
                    except ValueError:
                        pass
                    editmsg = 1
                    await ctx.author.send(fallback)
                    continue # Without going to the next question pls   
                ## CHECKS END
                # We now have full confidence that we are correct
                if(cp == 0):
                    self.ms[str(ctx.author.id)][ct - 1][1] = msg.content
                await ctx.author.send("Updated your answers.")
                continue
        await applychannel.send(f"**Staff application for {str(ctx.author)}:**")
        qs = self.ms[str(ctx.author.id)]
        j = 0
        while(j < len(qs)):
            print(qs)
            await applychannel.send(f"**{qs[j][0]}: ** {qs[j][1]}")
            j+=1
        await ctx.author.send("Submitted your application successfully!")
        self.client.state_cache_app[str(ctx.author.id)] = 0 # Bye Bye!
        return

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    async def applychannel(self, ctx, channel: discord.TextChannel):
        await self.settings.set_setting(ctx.guild, "applychannel", channel.id)
        await ctx.send(f"Successfully set the application channel for this guild")

def setup(client):
    client.add_cog(Manage(client))
    print("Ashfur Manager is loaded")

