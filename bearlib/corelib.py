import asyncpg, random
import time
from discord import Embed, Color, User
from discord.ext import commands
import string
import secrets
yellow = 0xFBFC7F

class Libguildcache():
    def __init__(self):
        # Make a new cache
        self.cache = [] # Cache is a list of dicts

    async def get_cached_prefix(self, gid):
        gid_cache = self.cache
        if(len(gid_cache) == 0):
            return None # Nothing in self.cache yet
        try:
            gid = int(gid)
        except:
            return None # Gid is invalid, so nothing

        for a in gid_cache: # Go through each dict in the list
            if(a["gid"] == gid):
                return a["prefix"]
        return None # Didn't get anything...

    async def remove_cached_prefix(self, gid):
        if(len(self.cache) == 0):
            return None # Nothing to remove
        i = 0
        while(i < len(self.cache)):
            # Keep looping through full thing
            if(self.cache[i]["gid"] == gid):
                self.cache[i] = None
            i+=1

    async def set_cached_prefix(self, gid, prefix):
        try:
            gid = int(gid)
        except:
            return None # Nope
        if(len(self.cache) == 0):
            self.cache.append({"gid": int(gid), "prefix": prefix})
        i = 0
        while(i < len(self.cache)):
            if(self.cache[i]["gid"] == gid):
                self.cache[i]["prefix"] = prefix
                return
            i+=1
        self.cache.append({"gid": int(gid), "prefix": prefix})
        return

global guild_cache # Global cache for guilds
guild_cache = Libguildcache() # Guild Cache

# Minimal Client Class
class CatClient():
    def __init__(self, db):
        self.db = db
        self.prefix = None # CatClients dont have prefixes

# A large part of this is in the cog but still, we need to handle modmail typing proxies here
class Libshadowmail():
    def __init__(self, client):
        self.client = client
        self.settings = Libsettings(client)

    async def is_blocked(self, user, guild):
        '''Returns if the user is blocked '''
        blocklist = await self.settings.get_setting(guild, "mm_blocks")
        if blocklist == "" or blocklist == None:
            return False, 0 # Nothing in blocklist yet
        blocklist = blocklist.split("||") # Get blocklist with the time epoch
        # This will return a list of all users with a | to denote epoch
        u = 0
        while(u < len(blocklist)):
            try:
                uid = blocklist[u].split("|")[0]
                epoch = blocklist[u].split("|")[1]
            except:
                u += 1
                uid = blocklist[u].split("|")[0]
                epoch = blocklist[u].split("|")[1]
            if(str(user.id) == str(uid)):
                # We know that the next element u + 1 has to contain the epoch till unblocked. This is set to 0 if infinite but that is for the client to process and use
                return True, epoch
            u+=1 # 2 because each user block is the user id and then end block epoch
        # If we get here, the answer is NO. The trailing 0 is for compatibility
        return False, 0

    async def block_user(self, guild, user, time=None):
        b = await self.is_blocked(user, guild)
        if(b[0] == True):
            return -1 # Already blocked
        if(time == None):
            time = 0
        if(await self.settings.get_setting(guild, "mm_blocks") == None or await self.settings.get_setting(guild, "mm_blocks") == ''):
            data = ""
        else:
            data = "||"        

        data += str(user.id) + "|" + str(time)
        await self.settings.append_setting(guild, "mm_blocks", data)        

    async def unblock_user(self, guild, user):
        b = await self.is_blocked(user, guild)
        if(b[0] == False):
            return -1 # Already unblocked
        # Get the current blocklist
        blocklist = await self.settings.get_setting(guild, "mm_blocks")
        if(blocklist == None):
            return None # No user found
        blist = blocklist.split("||")
        u = 0
        while(u < len(blist)):
            uid = blist[u]
            uid = uid.split("|")
            uid = uid[0]
            print(uid, user.id)
            if(uid == str(user.id)):
                del blist[u]
            u+=1
        nl = ""
        for b in blist:
            nl += b
        await self.settings.set_setting(guild, "mm_blocks", nl)


# Library for commands and errors
class Libcommand():
    def __init__(self, msg, db):
        self.msg = msg
        self.db = db

    async def blocked_cmd(self, msg):
        '''Returns if a command is blocked or not'''
        return 0 # For now, until this is implemented

    async def error(self):
        '''Takes an error and either sends an embed message or returns None depending on the error'''
        # Basic variables  
        content = self.msg.content
        author = self.msg.author
        if isinstance(author, User):
          admin = False
          mg = False
          bm = False
          km = False
          mm = False
          mum = False
        admin = author.guild_permissions.administrator
        mg = author.guild_permissions.manage_guild
        bm = author.guild_permissions.ban_members
        km = author.guild_permissions.kick_members
        mm = author.guild_permissions.manage_messages
        mum = author.guild_permissions.mute_members
        prefix = Libprefix(self.db)
        p = await prefix.get_prefix(self.msg)
        
        #error = Embed(title=f"**An error has occurred**", color = red)
        em = None
        ev = None
        # Not even a command errors
        if(content.startswith(p)):
            pass
        else:
            return None # Not the users fault if bot gets weird random errors

        # Kick Member
        if(content.startswith(f"{p}kick")):
            if(km):
                em = "Cannot Kick Member"
                ev = f"You either lack the permissions to kick this member or you are not using this command correctly.\nUsage: {p}kick <member> <reason (optional)>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Kick Members permission in order to use the {p}kick command"
        
        # Ban Member
        if(content.startswith(f"{p}ban")):
            if(bm):
                em = "Cannot Ban Member"
                ev = f"You either lack the permissions to ban this member or you are not using this command correctly.\nUsage: {p}ban <member> <reason (optional)>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Ban Members permission in order to use the {p}ban command"

        # Mute Member
        if(content.startswith(f"{p}mute")):
            if(mum):
                em = "Cannot Mute Member"
                ev = f"You either lack the permissions to mute this member or you are not using this command correctly.\nUsage: {p}mute <member> <reason (optional)>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Mute Members permission in order to use the {p}mute command"

        # Unmute Member
        if(content.startswith(f"{p}unmute")):
            if(mum):
                em = "Cannot Unmute Member"
                ev = f"You either lack the permissions to mute this member or you are not using this command correctly.\nUsage: {p}unmute <member>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Mute Members permission in order to use the {p}unmute command"

        # Autorole
        if(content.startswith(f"{p}autorole")):
            if(mg):
                em = "Cannot Find Role"
                ev = f"The role you are trying to setup for autorole does not exist. Please check the spelling and try again.\nUsage: {p}autorole <role>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Manage Server permission in order to use the {p}autorole command"
        
        # Mod Mail
        if(content.startswith(f">unblock")):
            if(km):
                em = "Invalid Syntax"
                ev = f"The user you are trying to unblock either does not exist or you have not actually provided a user.\nUsage: >unblock <user>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Kick Members permission in order to use the >unblock command"
        if(content.startswith(f">block")):
            if(km):
                em = "Invalid Syntax"
                ev = f"The user you are trying to block either does not exist or you have not actually provided a user.\nUsage: >block <user>"
            else:
                em = "Missing Permissions"
                ev = f"You must have the Kick Members permission in order to use the >block command"
        return em, ev
# Not yet done
class Libstaffapplication():
    def __init__(self, client, guild, app_type=None):
        self.client = client
        self.guild = guild

    async def list_questions(self):
        # Get all questions
        ql = await self.client.db.fetch("SELECT gid, qid, question, qcheck FROM guild_app_portfolio WHERE gid = $1", self.guild.id)
        return ql

    async def add_question(self, question, check):
        port = Libportfolio(self.client)
        await port.update_guild_app_portfolio("a", self.guild, question, check)
    async def remove_question(self, qid):
        # Note that remove question also removes duplicates
        r = await self.client.db.fetch("SELECT qid FROM guild_app_portfolio WHERE gid = $1 AND qid = $2", self.guild.id, qid)
        if not r:
            return "NO_QUESTIONS_IN_GUILD"
        # Get all questions
        ql = await self.list_questions()
        if(ql[0]["question"] == None):
            return "NO_QUESTIONS_IN_GUILD"
        port = Libportfolio(self.client)
        await port.update_guild_app_portfolio("r", self.guild, qid, None)
    async def add_check(self, qid, check):
        # Note that remove question also removes duplicates
        r = await self.client.db.fetch("SELECT qid FROM guild_app_portfolio WHERE gid = $1 AND qid = $2", self.guild.id, qid)
        print(r)
        if not r:
            return "NO_QUESTIONS_IN_GUILD"
        # Get all questions
        ql = await self.list_questions()
        if(ql[0]["question"] == None):
            return "NO_QUESTIONS_IN_GUILD"
        await self.client.db.execute("UPDATE guild_app_portfolio SET qcheck = $1 WHERE gid = $2 AND qid = $3", check, self.guild.id, qid)    
class Libwarn():
    ''' The format of a warn in a user_guild_portfolio is as follows:
            - epoch|reason||next_epoch|next_reason
    '''
    def __init__(self, client, user, guild):
        self.client = client
        self.settings = Libsettings(self.client)
        self.user = user
        self.guild = guild

    async def add_warn(self, reason, t=None):
        if(t == None):
            t = str(time.time())
        else:
            t = str(t)
        print(t)
        if(reason.__contains__("|")):
            return "Reason for warn cannot contain |"
        port = Libportfolio(self.client)
        ugp = await port.get_user_guild_portfolio(self.user, self.guild)
        warnings = ugp[0]["warnings"] # Get old warnings
        if(warnings == ''):
            sep = ""
        else:
            sep = "||"
        warnings += sep + t + "|" + reason
        await port.update_user_guild_portfolio(ugp, "warnings", warnings)
        return "Done"
    async def list_warns(self):
        port = Libportfolio(self.client)
        ugp = await port.get_user_guild_portfolio(self.user, self.guild)
        warnings = ugp[0]["warnings"] # Get warnings        
        warnings = warnings.split("||") # Split it by ||
        return warnings
        
    async def del_warn(self, ctx, num):
        warnings = await self.list_warns()
        c = 0
        await self.clear_warn()
        while(c < len(warnings)):
            print(c, len(warnings))
            if(c == num - 1):
                c = c + 1
                continue # Skip the warning we want to remove
            warn = warnings[c]
            try:
                Wl = warn.split("|") # 1 = Reason, 0 = Time
                Re = float(Wl[0])
                Rw = Wl[1] # This is the reason
                await self.add_warn(Rw, Re)
                c = c + 1
            except:
                await ctx.send(f"**{str(self.user)} has no infractions**")

    async def decomp_warn(self, R):
        Wl = R.split("|")
        Re = time.ctime(float(Wl[0]))
        Rw = Wl[1]
        return Re, Rw

    async def clear_warn(self):
        port = Libportfolio(self.client)
        ugp = await port.get_user_guild_portfolio(self.user, self.guild)
        warnings = ""
        await port.update_user_guild_portfolio(ugp, "warnings", warnings)

class Libquiz():
    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.quiz_length = None
        self.questions = None
        self.question = None
        self.answer = None
        self.question_num = 0
        self.in_quiz = None
        self.pane = 0

    # Function to just get all questions
    async def get_questions_all(self):
        questions = await self.client.db.fetch("SELECT quiz_question, quiz_answer FROM bot_portfolio")
        return questions

    async def random_question(self):
        self.questions = await self.get_questions_all()
        self.quiz_length = len(self.questions)
        self.question_num = random.randint(0, self.quiz_length - 1)
        self.question = self.questions[self.question_num]["quiz_question"]
        self.answer = self.questions[self.question_num]["quiz_answer"]
        await self.message.channel.send(self.question)
        try:
            msg = await self.client.wait_for('message', check=lambda message: message.author == self.message.author, timeout = 10)
        except:
            await msg.channel.send("Uh Oh... Time's run out. Better luck next time")
            economy = Libeconomy(self.client)
            await economy.remove_money(self.message.author, 10)
        if(msg.content.lower() == self.answer.lower()):
            await msg.channel.send("You got the question correct!\nKeep it up!")
            economy = Libeconomy(self.client)
            await economy.add_money(self.message.author, 25)
        else:
            economy = Libeconomy(self.client)
            await msg.channel.send(f"**You sadly got the question wrong...**\n**Correct Answer:** {self.answer}")
            await economy.remove_money(self.message.author, 10)

    async def add_quiz_question(self, question, answer):
        await self.client.db.execute("INSERT INTO bot_portfolio (quiz_question, quiz_answer) VALUES ($1, $2)", question, answer)

    async def add_qa_interactive(self, message, owners):
        if(str(message.author.id) not in owners):
            await message.channel.send("**Error**\nOnly bot owners may add a question")
            return
        await message.channel.send("Please type the question to add?")
        question = await self.client.wait_for('message', check=lambda message: message.author == self.message.author)
        await message.channel.send("Please type the answer to this question?")
        answer = await self.client.wait_for('message', check=lambda message: message.author == self.message.author)
        await self.add_quiz_question(question.content, answer.content)
        await message.channel.send("Added quiz question!")

# Portfolio API
class Libportfolio():
    def __init__(self, client=None):
        ''' Client is mostly needed for most functions.'''
        self.client = client

    async def create_user_modmail_portfolio(self, uid, gid):
        await self.client.db.execute("INSERT INTO user_modmail_portfolio VALUES ($1, $2, 0)", uid, gid)

    # Function to create a portfolio for a user and add it to a database
    async def create_user_portfolio(self, user):
        await self.client.db.execute("INSERT INTO user_portfolio VALUES ($1, 0, 0, 1, 'DEFAULT', 'SUBMARINE_BASIC LOCKPICK USER_MANUAL', $2, $2, $2, 0)", user.id, time.time())

    # Function to create a user guild portfolio of a user to a guild
    async def create_user_guild_portfolio(self, user, guild):
        await self.client.db.execute("INSERT INTO user_guild_portfolio VALUES ($1, $2, '0', '0', '')", guild.id, user.id)
    
    # Function to create a guild portfolio of a guild
    async def create_guild_portfolio(self, guild):
        portfolio = await self.client.db.fetch("SELECT gid FROM guild_portfolio WHERE gid = $1", guild.id)
        if not portfolio:
            # Default Guild expontential rate is 4
            await self.client.db.execute("INSERT INTO guild_portfolio (gid, guild_level, guild_money, guild_points, guild_perks, guild_economy_rate, private, mm_blocks) VALUES ($1, '1', '0', '0', 'BASIC VERIFIED', '4', 0, '')", guild.id)

    # Function to update guild app portfolio (set answer and check to None if deleting)
    async def update_guild_app_portfolio(self, o, guild, question, check):
        # In reality, question is qid in remove question
        if o in ["a", "add"]:
            #ql = await self.client.db.fetch("SELECT app_questions FROM guild_portfolio WHERE gid = $1", self.guild.id)
            qid = ''.join((secrets.choice(string.ascii_letters + "0123456789") for i in range(64)))
            await self.client.db.execute("INSERT INTO guild_app_portfolio VALUES ($1, $2, $3, $4)", guild.id, qid, question, check)
        elif o in ["r", "remove"]:
            await self.client.db.execute("DELETE FROM guild_app_portfolio WHERE gid = $1 AND qid = $2", guild.id, question)

    # Function to update a user guild portfolio
    async def update_user_guild_portfolio(self, user_guild_portfolio, setting, value):
        await self.client.db.execute(f"UPDATE user_guild_portfolio SET {setting}= $1 WHERE gid = $2 AND uid = $3", value, user_guild_portfolio[0]["gid"],user_guild_portfolio[0]["uid"])
    # Same thing for normal user portfolios
    async def update_user_portfolio(self, user_portfolio, setting, value):
        await self.client.db.execute(f"UPDATE user_portfolio SET {setting} = $1 WHERE uid = $2", value, user_portfolio[0]["uid"])
    # Function get user portfolio
    async def get_user_portfolio(self, user):
        portfolio = await self.client.db.fetch("SELECT * FROM user_portfolio WHERE uid = $1", user.id)
        if not portfolio:
            await self.create_user_portfolio(user)
            portfolio = await self.get_user_portfolio(user)
        user_portfolio = portfolio
        return user_portfolio

    # Function to get user guild portfolio
    async def get_user_guild_portfolio(self, user, guild):
        portfolio = await self.client.db.fetch("SELECT * FROM user_guild_portfolio WHERE uid = $1 AND gid = $2", user.id, guild.id)
        if not portfolio:
            await self.create_user_guild_portfolio(user, guild)
            portfolio = await self.get_user_guild_portfolio(user, guild)
        user_guild_portfolio = portfolio
        return user_guild_portfolio

    # Function to get guild portfolio
    async def get_guild_portfolio(self, guild):
        portfolio = await self.client.db.fetch("SELECT * FROM guild_portfolio WHERE gid = $1", guild.id)
        if not portfolio:
            await self.create_guild_portfolio(guild)
            portfolio = await self.get_guild_portfolio(guild)
        else:
            pass
        guild_portfolio = portfolio
        return guild_portfolio

    # Gets the Economy Rate
    async def get_economy_rate(self, guild_portfolio):
        return int(guild_portfolio[0]["guild_economy_rate"])

    # Function to get current user level
    async def get_curr_level(self, user_portfolio):
        return int(user_portfolio[0]["level"]) # I think (?) 

    # Function to get current user points
    async def get_curr_points(self, user_portfolio):
        return int(user_portfolio[0]["points"]) # I think (?)

    # Function to get current user guild_level
    async def get_curr_user_guild_level(self, user_guild_portfolio):
        return int(user_guild_portfolio[0]["user_guild_level"]) # I think (?)

    # Function to get current user level
    async def get_curr_money(self, user_portfolio):
        return int(user_portfolio[0]["money"]) # I think (?)

    # Function to get current message count
    async def get_curr_msg_count(self, user, guild):
      user_guild_portfolio = await self.get_user_guild_portfolio(user, guild)
      return int(user_guild_portfolio[0]["msg_count"])

    async def gen_portfolio_embed(self, user, guild=None):
        avatar = user.avatar_url
        user_portfolio = await self.get_user_portfolio(user)
        if(guild):
            user_guild_portfolio = await self.get_user_guild_portfolio(user, guild)
        embed_intro = Embed(title=f"**{str(user)}'s Portfolio's**", color = yellow)
        embed_up = Embed(title = f"**User Portfolio**", description = f"**Money:** {await self.get_curr_money(user_portfolio)}\n**Points:** {await self.get_curr_points(user_portfolio)}\n**User Level:** {await self.get_curr_level(user_portfolio)}", color = Color.green())
        if(guild):
            embed_guild = Embed(title = f"**User Guild Portfolio**", description = f"**User Guild Level:** {await self.get_curr_user_guild_level(user_guild_portfolio)}\n**Message Count:** {await self.get_curr_msg_count(user, guild)}", color=Color.red())
        else:
            embed_guild = None
        embed_intro.set_thumbnail(url=avatar)
        return embed_intro, embed_up, embed_guild

class Libeconomy():
    def __init__(self, client):
        self.client = client
        self.portfolio = Libportfolio(client)

    # Function to level up a user
    async def level_up(self, user):
        user_portfolio = await self.portfolio.get_user_portfolio(user)
        level = await self.portfolio.get_curr_level(user_portfolio) + 1
        await self.client.db.execute("UPDATE user_portfolio SET level = $1 WHERE uid=$2", (int(level), user.id))

    # Function to level up a user's guild level
    async def level_up_guild(self, user, guild):
        user_guild_portfolio = await self.portfolio.get_user_guild_portfolio(user, guild)
        level = await self.portfolio.get_curr_user_guild_level(user_guild_portfolio) + 1
        await self.client.db.execute("UPDATE user_guild_portfolio SET user_guild_level = $1 WHERE uid=$2 AND gid = $3", int(level), user.id, guild.id)

    # Function to increment users message count by 1
    async def increment_msg_count(self, user, guild):
        # Add to cache
        port = Libportfolio(self.client)
        curr_msg_count = await port.get_curr_msg_count(user, guild)
        await self.set_msg_count(user, guild, curr_msg_count + 1)

    # Function to set a new msg count
    async def set_msg_count(self, user, guild, msg_count):
        await self.client.db.execute("UPDATE user_guild_portfolio SET msg_count = $1 WHERE uid = $2 AND gid = $3", int(msg_count), user.id, guild.id)

    # Function to add money to a user
    async def add_money(self, user, amt):
        if(user.bot):
            return
        user_portfolio = await self.portfolio.get_user_portfolio(user)
        money = await self.portfolio.get_curr_money(user_portfolio) + amt
        await self.client.db.execute("UPDATE user_portfolio SET money = $1 WHERE uid = $2", int(money), user.id)

    # Function to remove money from a user
    async def remove_money(self, user, amt):
        if(user.bot):
            return
        user_portfolio = await self.portfolio.get_user_portfolio(user)
        money = await self.portfolio.get_curr_money(user_portfolio) - amt
        await self.client.db.execute("UPDATE user_portfolio SET money = $1 WHERE uid = $2", money, user.id)

    # Function to remove points from a user
    async def remove_points(self, user, amt):
        if(user.bot):
            return
        user_portfolio = await self.portfolio.get_user_portfolio(user)
        points = await self.portfolio.get_curr_points(user_portfolio) - amt
        await self.client.db.execute("UPDATE user_portfolio SET points = $1 WHERE uid = $2", points, user.id)

    # Function to add points to a user (with money also added too)
    async def add_points(self, user, amt):
        if(user.bot):
            return
        user_portfolio = await self.portfolio.get_user_portfolio(user)
        points = await self.portfolio.get_curr_points(user_portfolio) + amt
        money_add = 0
        while(points >= 15):
            money_add += 1
            points -= 15
        await self.add_money(user, money_add)
        await self.client.db.execute("UPDATE user_portfolio SET points = $1 WHERE uid = $2", int(points), user.id)

    # Updates the Epoch on the user
    async def update_epoch(self, user, t):
        if(user.bot):
            return
        await self.client.db.execute(f"UPDATE user_portfolio SET {t} = $1 WHERE uid = $2", time.time(), user.id)

    # Get current epoch of user
    async def get_epoch(self, user_portfolio, t):
        return user_portfolio[0][t]

# Login to PostgreSQL
async def setup_db(pg_user, pg_pwd):
    db = asyncpg.create_pool(host = "127.0.0.1", port=5432, user=pg_user, password=pg_pwd, database="bear")
    return db

# Change a setting (prefix) etc
class Libprefix():
    '''Libprefix is an API to allow you to view and change prefixes. To use this, pass in db, which is usually exposed as self.client.db and cache, which is exposed as self.client.cache'''
    def __init__(self, db):
        self.db = db
        self.miniclient = CatClient(db)

    async def set_prefix(self, guild, prefix, cgp=True):
        r = await self.db.fetch("SELECT * FROM guild_portfolio WHERE gid = $1", guild.id)
        if not r:
            if(cgp):
                port = Libportfolio(self.miniclient)
                await port.create_guild_portfolio(guild)
        await self.db.execute("UPDATE guild_portfolio SET prefix = $1 WHERE gid = $2", prefix, guild.id)
        # Get the new prefix
        await self.get_prefix(guild, type = "guild")
        await guild_cache.set_cached_prefix(guild.id, prefix)
        await self.get_prefix(guild, type = "guild")

    # returns prefix
    async def get_prefix(self, message, type=None):
        if(type == None):
            guild = message.guild
        elif(type == "guild"):
            guild = message
            pass # User is directly passing in guild and not a message
        #Only allow custom prefixs in guild
        if guild:
            # First check cache
            custom_prefixes = await guild_cache.get_cached_prefix(guild.id)
            if(custom_prefixes == None):
                pass
            else:
                return custom_prefixes

            custom_prefixes = await self.db.fetchrow(f"SELECT prefix from guild_portfolio WHERE gid = $1", guild.id)   
            try:
                custom_prefixes = custom_prefixes["prefix"]
            except:
                custom_prefixes = ">"
            if(custom_prefixes == None):
                custom_prefixes = ">"
            # Set custom_prefixes in cache
            await guild_cache.set_cached_prefix(guild.id, custom_prefixes)
            return custom_prefixes
        return "$" # Not in guild, use default $

    # Same as get_prefix, but for initial bot setup
    async def bot_get_prefix(self, bot, message):
        extras = await self.get_prefix(message) # returns a list
        ret = commands.when_mentioned_or(extras)(bot, message)
        print(ret)
        bot.command_prefix = ret # Force new prefix
        return ret

class FakeMessage():
    def __init__(self, guild):
        self.guild = guild

class Libsettings():
    def __init__(self, client):
        self.client = client
        self.db = client.db
    async def set_setting(self, guild, setting, value, uid=None, portfolio="guild_portfolio", noconv=False):
        '''Sets a setting. Takes in the following arguments
            guild - The guild in which to change the setting
            setting - The name of the setting (in the database) that you want to change.
            value - The new value of the setting
        '''
        # Make sure there is a guild portfolio created
        r = await self.db.fetch(f"SELECT * FROM {portfolio} WHERE gid = $1", guild.id)
        if not r:
            port = Libportfolio(self.client)
            if(portfolio == "user_modmail_portfolio"):
                await port.create_user_modmail_portfolio(uid, guild.id)
            await port.create_guild_portfolio(guild)
        if(uid == None):
            r = await self.db.fetch(f"SELECT * FROM {portfolio} WHERE gid = $1", guild.id)
        else:
            r = await self.db.fetch(f"SELECT {setting} from {portfolio} WHERE gid = $1 AND uid = $2", guild.id, uid)         
        try:
            if(noconv==False):
                value = int(value)
        except:
            pass
        if(uid == None):
            await self.db.execute(f"UPDATE {portfolio} SET {setting}=$1 WHERE gid=$2", value, guild.id)
        else:
            await self.db.execute(f"UPDATE {portfolio} SET {setting}=$1 WHERE gid=$2 AND uid=$3", value, guild.id, uid)


    async def get_setting(self, guild, setting, uid=None, portfolio="guild_portfolio"):
        if(type(guild) == str):
            try:
                guild = int(guild)
            except:
                pass
        if(type(guild) == int):
            gid = guild
        else:
            gid = guild.id
        if(uid == None):
            r = await self.db.fetch(f"SELECT {setting} from {portfolio} WHERE gid = $1", gid)
        else:
            r = await self.db.fetch(f"SELECT {setting} from {portfolio} WHERE gid = $1 AND uid = $2", gid, uid)         
        try:
            r = r[0][setting]
        except:
            if(portfolio == "user_modmail_portfolio"):
                return ''
            return None
        return r
    async def del_setting(self, guild, setting, portfolio="guild_portfolio"):
        '''Deletes a setting. Takes in the following arguments
            guild - The guild in which to change the setting
            setting - The name of the setting (in the database) that you want to change.
        '''
        # Make sure there is a guild portfolio created
        r = await self.db.fetch(f"SELECT * FROM {portfolio} WHERE gid = $1", guild.id)
        if not r:
            if(portfolio != "guild_prtfolio"):
                return -1
            port = Libportfolio(self.client)
            await port.create_guild_portfolio(guild)
        r = await self.db.fetch("SELECT * FROM guild_portfolio WHERE gid = $1", guild.id)
        await self.db.execute(f"UPDATE guild_portfolio SET {setting}=null WHERE gid=$1", guild.id)
    async def setting_in_use(self, setting, value, portfolio="guild_portfolio"):
        in_use = await self.db.fetch(f"SELECT * from {portfolio} WHERE {setting} = $1", value)
        if(in_use == []):
            pass
        else:
            in_use = in_use[0][setting]
            if(in_use.lower() == value.lower()):
                return 0
        return 1
    async def get_guild_from_setting(self, setting, value, portfolio="guild_portfolio"):
        target = await self.db.fetchrow(f"SELECT * FROM {portfolio} WHERE {setting} = $1", value)
        if target:
            target = target["gid"]
        else:
            target = None
        return target
    async def append_setting(self, guild, setting, value, uid=None, portfolio="guild_portfolio"):
        # Append another value to a setting
        old_value = await self.get_setting(guild, setting, uid, portfolio)
        new_value = str(old_value) + str(value)
        await self.set_setting(guild, setting, new_value, uid, portfolio)

class Libremove():
    def __init__(self, message, guild, setting, name):
        self.message = message
        self.guild = guild
        self.setting = setting
        self.name = name

    async def remove(self):
        settings = Libsettings(self.client)
        await settings.del_setting(self.guild, self.setting)
        await self.message.channel.send(f"{self.name} for {self.guild} has been stopped")
    
