import discord
from discord.ext import commands
from bearlib.corelib import Libsettings, Libtable, Libshadowmail, Libprefix
from io import BytesIO
import time


# Shadowmail is Water Bots/Aqua's version of Mod Mail, it uses Libshadowmail
class ShadowMail(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.settings = Libsettings(client)
        self.port = Libtable(client)
        self.modmail = Libshadowmail(client)
        self.prefix = Libprefix(client.db)
        self.client.state_cache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.content.startswith(">modmail")):
            if (self.client.state_cache_app.get(str(message.author.id))):
                pass
            else:
                self.client.state_cache_app[str(
                    message.author.id)] = 0  # Initial value
            if (self.client.state_cache_app[str(message.author.id)] == 1):
                await message.author.send(
                    "You cannot start a modmail at the moment"
                )
                return
            state = self.client.state_cache_app[str(message.author.id)]
            print(state)
            if (state != 0 and state != None):
                # We are already in a modmail, do nothing
                await message.channel.send(
                    "You cannot start a modmail at the moment"
                )
                return
        else:
            return  # Not for us
        if (str(message.channel.type == "private")):
            pass
        else:
            await message.channel.send(
                "Modmail commands can only be used in DMs"
            )  # Don't do anything unless its in DM's
            return
        self.client.state_cache_app[str(message.author.id)] = 1
        # Get all mutual servers with the user
        mutuals = []
        for guild in self.client.guilds:
            if (guild.get_member(message.author.id) == None):
                continue
            mutuals.append(guild)
        # Now that we have every mutual server, ask the user to choose which one
        if (len(mutuals) == 1):
            guild = mutuals[0]
        m = ""
        i = 1

        for mutual in mutuals:
            m += f"**{i}.** {str(mutual)}\n"
            i += 1

        await message.author.send(
            f"**Please choose the guild you wish to start a modmail with**: \n\n{m}"
        )
        msg = await self.client.wait_for(
            'message',
            check=
            lambda msg: msg.author.id == message.author.id and str(msg.channel.type) == "private" and msg.content.__contains__("$start") == False
        )
        try:
            guild = mutuals[int(msg.content) - 1]
            self.client.state_cache_app[str(message.author.id)] = guild.id
        except ValueError:
            await message.author.send(
                "Invalid guild. Please try again with $start and a proper guild."
            )
            self.client.state_cache_app[str(message.author.id)] = 0
            return

        user = message.author
        channel = message.channel
        # Check if they are blocked in the guild
        b = await self.modmail.is_blocked(user, guild)
        if (b[0]):
            await channel.send(
                f"You have been blocked from using mod mail on this guild till epoch {b[1]}"
            )
            self.client.state_cache_app[str(message.author.id)] = 0
            return
        # Get modmail category
        catid = await self.settings.get_setting(guild, "mm_category")
        cat = discord.utils.get(guild.categories, id=catid)
        mcn = str(user).lower().replace(
            "#", "-")  # Rootspring#6701 = rootspring-6701 etc.
        # Take in to account old modmail threads that havent been deleted (Bot crash etc.) and garbage collect them
        mchannel = await guild.create_text_channel(f'{mcn}', category=cat)

        # Get welcome message and send it to the user
        wmsg = await self.settings.get_setting(guild, "mm_welcomemsg")
        if (wmsg == None):
            # No welcome message has been set. Use the generic one
            wmsg = f"Welcome to {str(guild)}'s Mod Mail!\nPlease type your queries here and wait for a staff member to come and assist you!"
        try:
            await user.send(wmsg)
        except:
            # User has DM's disabled
            await channel.send(
                "**Error**\nYour DM's are disabled right now. You need to enable them to use Mod Mail"
            )
        await self.do_mmail(message, mchannel, user, guild)

    async def do_mmail(self, message, mchannel, user, guild, new=True):
        # Get the old modlog
        #     async def get_setting(self, guild, setting, uid=None, table="guild_table"):
        if (new):
            await self.settings.append_setting(
                guild,
                "mm_logs",
                f"\nNEW THREAD AT {time.ctime()}\n",
                uid=int(user.id),
                table="user_modmail_table")
        p = await self.prefix.get_prefix(guild, type="guild")
        msgbak = None
        mcn = str(user).lower().replace(
            "#", "-")  # Rootspring#6701 = rootspring-6701 etc.
        tu = '\N{THUMBS UP SIGN}'
        while True:
            msg = await self.client.wait_for('message')
            if (msg.channel.id == mchannel.id
                    or msg.author == message.author and not msg.author.bot):
                pass
            else:
                continue
            if (str(msg.channel.type) == "private" and msg.author == user):
                # This is a users message to the mods, send this msg
                if (msg.content == "$start"):
                    continue  # Oops, dont send this
                if (msg.content == ">close"):
                    # User wants to close the mail, ask the mods...
                    await mchannel.send(
                        f"This user has closed this modmail thread and it has been archived. Messages you send here will not be sent to the user. You may however use this as a transcript.\nYou may use {p}kill to remove this thread or {p}killall <user> to remove all archived threads by this user"
                    )
                    await mchannel.edit(name=mcn + "-archivedaqua")
                    await mchannel.set_permissions(
                        guild.default_role, send_messages=False)
                    self.client.state_cache_app[str(message.author.id)] = 0
                    await user.send(
                        "You have successfully manually closed this thread. Note that mods can still see this thread."
                    )
                    # Send the modlog
                    return await mchannel.send(f"Mod Mail Log: https://Aqua.cheesycod.repl.co/shadowmail/{guild.id}/{user.id}")
                await mchannel.send(msg.content)
                if (msgbak != None):
                    await msgbak.reactions[0].remove(
                        self.client.user)  # Remove old reaction
                await msg.add_reaction(tu)  # And react that we have sent it
                await self.settings.append_setting(
                    guild,
                    "mm_logs",
                    f"(THREAD) {str(user)} TO MOD: " + msg.content + "\n",
                    uid=user.id,
                    table="user_modmail_table")
                msgbak = msg  # Backup old message so we can remove reaction when they send a new message

            elif (msg.channel.id == mchannel.id):
                # This is the mods message to the user
                if (msg.content == ">close"):
                    await mchannel.edit(name=mcn + "-archivedaqua")
                    await user.send(
                        f"Your thread has been closed by the moderators of {str(guild)}.\nThank you and have a nice day!"
                    )
                    await mchannel.send(
                        f"A moderator has closed this modmail thread and it has been archived. Messages you send here will not be sent to the user. You may however use this as a transcript.\nYou may use {p}kill to remove this thread or {p}killall <user> to remove all archived threads by this user"
                    )
                    self.client.state_cache_app[str(message.author.id)] = 0
                    await mchannel.set_permissions(
                        guild.default_role, send_messages=False)
                    # Send the modlog 
                    return await mchannel.send(f"Mod Mail Log: https://Aqua.cheesycod.repl.co/shadowmail/{guild.id}/{user.id}")
                if (msg.content == f">block"):
                    await self.modmail.block_user(guild, user)
                    await mchannel.send(f"{str(user)} has been blocked")
                    continue
                # Is the mod admin or mod or whatever (for consistency)
                level = msg.author.roles
                if (len(level) == 1):
                    if (msg.author.guild_permissions.administrator):
                        level = "Administrator"
                    elif (msg.author.guild_permissions.manage_guild):
                        level = "Manager"
                    elif (msg.author.guild_permissions.ban_members
                          or msg.author.guild_permissions.kick_members):
                        level = "Moderator"
                    else:
                        level = "Support"
                else:
                    level.reverse()
                    level = level[0]
                mts = f"**({level}) {str(msg.author)}:** {msg.content}"
                await msg.delete()
                await mchannel.send(mts)
                await user.send(mts)
                await self.settings.append_setting(
                    guild,
                    "mm_logs",
                    f"(THREAD) MOD TO {str(user)}: " + msg.content + "\n",
                    uid=user.id,
                    table="user_modmail_table")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unblock(self, ctx, user: discord.User):
        rc = await self.modmail.unblock_user(ctx.guild, user)
        if (rc == -1):
            await ctx.message.channel.send(
                f"{user} is already unblocked from modmail! Not doing anything..."
            )
            return
        await ctx.message.channel.send(
            f"{user} has been unblocked from modmail")

    @commands.command()
    async def start(self, ctx):
        pass

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def block(self, ctx, user: discord.User, t=None):
        rc = await self.modmail.block_user(ctx.guild, user, t)
        print(rc)
        if (rc == -1):
            await ctx.message.channel.send(
                f"{user} is already blocked from modmail! Not doing anything..."
            )
            return
        await ctx.message.channel.send(f"{user} has been blocked from modmail")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def kill(self, ctx, reason=None):
        await ctx.message.channel.send(
            "**Warning:** The kill command will delete this channel even if it isn't a modmail thread. It is meant to be an easy way to remove channels. Do not use unless you have a good reason to do so.\nShould I continue (Yes/No)?"
        )
        msg = await self.client.wait_for(
            'message',
            check=lambda msg: msg.author.id == ctx.message.author.id)
        if (msg.content == "Yes"):
            await ctx.message.channel.delete(reason=reason)
        else:
            await ctx.message.channel.send(
                "Not deleting thread as you requested")
            return

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        ''' Called when someone begins typing a message.
            The channel parameter can be a abc.Messageable instance. Which could either be TextChannel, GroupChannel, or DMChannel.
           If the channel is a TextChannel then the user parameter is a Member, otherwise it is a User.
            Parameters
                channel (abc.Messageable) – The location where the typing originated from.
                user (Union[User, Member]) – The user that started typing.
                when (datetime.datetime) – When the typing started as a naive datetime in UTC.
        '''
        print(self.client.command_prefix)
        print("started typing")
        try:
            if (self.client.state_cache.get(str(user.id))):
                state = self.client.state_cache[str(user.id)]
                state = int(state)
            else:
                # If the user is not in the state cache, dont do anything
                return
        except KeyError:
            state = 0
        if (state == 0):
            return  # Not in a modmail
        print(state)
        guild = self.client.get_guild(int(state))
        # DMChannel
        if (str(channel.type) == "private"):
            print("In private")
            # Set typing in mchannel
            mcn = str(user).lower().replace("#", "-")
            mchannel = discord.utils.get(guild.text_channels, name=mcn)
            print(mchannel)
            if (mchannel == None):
                print("Got here 3.0 in typing")
                return  # Return none
            await mchannel.trigger_typing()

        # TextChannel
        if (str(channel.type) == "text"):
            # Set typing in the DMChannel
            await user.trigger_typing()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def killall(self, ctx, user: discord.User = None):
        if (user == None):
            for channel in ctx.guild.channels:
                if (channel.__contains__("archivedaqua")):
                    await channel.delete()
        else:
            mcn = str(user).lower().replace("#", "-")
            mcn += "-archivedaqua"
            for channel in ctx.guild.channels:
                if (channel.name == mcn):
                    await channel.delete()

def setup(client):
    client.add_cog(ShadowMail(client))
    print('Shadowsight Mod Mail has loaded successfully!')
