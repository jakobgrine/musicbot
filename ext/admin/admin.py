import discord
from discord.ext import commands
from PIL import Image
import requests
import numpy
import scipy
import scipy.misc
import scipy.cluster
from .converter import GuildConverter, ExtensionConverter
from . import utils
import io
import traceback
from collections import deque
import asyncio
import speedtest
import psutil
import os
import datetime


class Admin(commands.Cog):
    STATUS_TRANSFORMS = {
        discord.Status.online: 'Online',
        discord.Status.offline: 'Offline',
        discord.Status.idle: 'IDle',
        discord.Status.dnd: 'Do Not Disturb',
        discord.Status.invisible: 'Invisible'
    }

    def __init__(self, bot):
        self.bot = bot
        self.eval_cache = deque()

    @commands.command(aliases=['poweroff'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Turns off the bot"""
        await ctx.message.delete()
        await ctx.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: ExtensionConverter):
        """Hot reloads an extension"""
        ctx.bot.reload_extension(extension)

        await ctx.send(f':recycle: **Extension `{extension}` was reloaded**', delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx: commands.Context, all: bool = False):
        """Deletes certain messages (either bot related messages or all)"""
        messages_to_delete = []

        async for message in ctx.channel.history(limit=None, before=ctx.message):
            if all or message.author == ctx.bot.user or message.content.startswith(ctx.bot.command_prefix):
                messages_to_delete.append(message)

        for messages in utils.divide_chunks(messages_to_delete, 100):
            await ctx.channel.delete_messages(messages)

        await ctx.send(f':recycle: **Deleted {len(messages_to_delete)} message(s)**', delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: commands.Context, *, code: str):
        """Evaluates arbitrary code and shows the result"""
        eval_globals = {'discord': discord, 'commands': commands, 'bot': ctx.bot, 'ctx': ctx,
                        'cache': self.eval_cache, 'last': self.eval_cache[0] if self.eval_cache else None, **ctx.bot.cogs}

        try:
            result = eval(code, eval_globals)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception:
            response = f'```{traceback.format_exc()}```'
        else:
            self.eval_cache.appendleft(result)
            if str(result) != result.__repr__():
                response = f'```python\n{str(result)}``````python\n{result.__repr__()}```'
            else:
                response = f'```python\n{result.__repr__()}```'
        finally:
            msg = await ctx.send(response)
            await utils.wait_to_delete(self.bot, ctx.message, msg)

    @commands.command()
    @commands.is_owner()
    async def speedtest(self, ctx: commands.Context):
        embed = discord.Embed(color=discord.Color.blue()) \
            .set_author(name='Testing...', icon_url='https://gist.githubusercontent.com/jakobgrine/e4022476a46d15d0df28e2af50e82278/raw/431c96ea40faa216258184144fd6160f80780e15/hourglass_animated.gif')
        msg = await ctx.send(embed=embed)

        sp = speedtest.Speedtest()
        sp.download()
        sp.upload()

        await msg.edit(content=sp.results.share(), embed=None)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @commands.command()
    @commands.is_owner()
    async def uptime(self, ctx: commands.Context):
        pid = os.getpid()
        proc = psutil.Process(pid)
        start = datetime.datetime.fromtimestamp(proc.create_time())
        diff = datetime.datetime.now() - start
        start_str = start.strftime('%Y-%m-%d %H:%M:%S')
        diff_str = str(diff).split(".")[0]
        emoji = 'clock' + str(start.hour % 12) + \
            ('30' if start.second >= 30 else '')
        await ctx.send(f':{emoji}: **The bot is up since `{start_str}` (`{diff_str}`)**', delete_after=5)

    @commands.group()
    @commands.is_owner()
    async def info(self, ctx: commands.Context):
        """Shows information about one of the following"""
        if ctx.invoked_subcommand is None:
            if ctx.subcommand_passed is None:
                raise commands.CommandNotFound('Subcommand not found')
            else:
                raise commands.CommandNotFound(
                    f'Subcommand "{ctx.subcommand_passed}" is not found')

    @info.command(aliases=['u'])
    async def user(self, ctx: commands.Context, user: discord.User):
        """Shows information about a user"""
        asset = user.avatar_url_as(format='png', size=32)
        dominant = await utils.dominant(asset)

        embed = discord.Embed(color=dominant) \
            .set_thumbnail(url=user.avatar_url_as(size=256)) \
            .set_author(name=str(user)) \
            .add_field(name='ID', value=user.id) \
            .add_field(name='Created at', value=user.created_at.strftime('%d.%m.%Y %H:%M'))
        if user.bot:
            embed.description = 'This is a bot account'
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @info.command(aliases=['m'])
    async def member(self, ctx: commands.Context, user: discord.Member):
        """Shows information about a member"""
        asset = user.avatar_url_as(format='png', size=32)
        dominant = await utils.dominant(asset)

        embed = discord.Embed(color=dominant) \
            .set_thumbnail(url=user.avatar_url_as(size=256)) \
            .set_author(name=str(user)) \
            .add_field(name='ID', value=user.id) \
            .add_field(name='Created at', value=user.created_at.strftime('%d.%m.%Y %H:%M')) \
            .add_field(name='Joined at', value=user.joined_at.strftime('%d.%m.%Y %H:%M'))
        if len(user.activities):
            activity_description = ''
            for activity in user.activities:
                if activity.type == discord.ActivityType.listening:
                    activity_description = f'Listening to `{activity.title}` by `{activity.artist}`'
                elif activity.type == discord.ActivityType.playing:
                    activity_description = f'Playing `{activity.name}`'
                elif activity.type == discord.ActivityType.streaming:
                    activity_description = f'Streaming `{activity.name}`'
                    if activity.twitch_name is not None:
                        activity_description += f' by `{activity.twitch_name}`'
                elif activity.type == discord.ActivityType.watching:
                    activity_description = f'Watching `{activity.name}`'
            embed.add_field(name='Activity', value=activity_description)
        if len(user.roles) > 1:
            roles = ', '.join(map(lambda r: f'`{r.name}`', user.roles[1:]))
            embed.add_field(name='Roles', value=roles)
        if user.is_on_mobile():
            embed.add_field(
                name='Status', value=f'{self.STATUS_TRANSFORMS[user.mobile_status]} (on mobile)')
        else:
            embed.add_field(
                name='Status', value=f'{self.STATUS_TRANSFORMS[user.status]}')
        if user.premium_since is not None:
            embed.add_field(name='Premium since',
                            value=user.premium_since.strftime('%d.%m.%Y %H:%M'))
        if user.voice is not None:
            if user.voice.afk:
                value = 'AFK'
            elif len(user.voice.channel.members) == 2:
                value = f'in `{user.voice.channel}` with `1` other person'
            elif len(user.voice.channel.members) > 2:
                value = f'in `{user.voice.channel}` with `{len(user.voice.channel.members) - 1}` other people'
            else:
                value = f'in `{user.voice.channel}`'
            embed.add_field(name='Voice State', value=value)
        if user.bot:
            embed.description = 'This is a bot account'
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @info.command(aliases=['r'])
    async def role(self, ctx: commands.Context, role: discord.Role):
        """Shows information about a role"""
        embed = discord.Embed(title=f'{role.name}', color=role.color) \
            .add_field(name='ID', value=role.id) \
            .add_field(name='Permissions', value=role.permissions.value)
        if len(role.members):
            members = ', '.join(map(lambda m: f'`{m.name}`', role.members))
            embed.add_field(name='Members', value=members)
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @info.command(aliases=['g'])
    async def guild(self, ctx: commands.Context, guild: GuildConverter):
        """Shows information about a guild/server"""
        asset = guild.icon_url_as(format='png', size=32)
        if asset:
            dominant = await utils.dominant(asset)
            embed = discord.Embed(
                title=guild.name, description=guild.description, color=dominant)
        else:
            embed = discord.Embed(
                title=guild.name, description=guild.description)

        embed.add_field(name='ID', value=guild.id) \
            .set_thumbnail(url=guild.icon_url_as(size=256)) \
            .add_field(name='Owner', value=f'`{str(guild.owner)}`') \
            .add_field(name='Members', value=f'`{guild.member_count}` members') \
            .add_field(name='Created at', value=guild.created_at.strftime('%d.%m.%Y %H:%M'))
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @info.command(aliases=['t', 'tc', 'text'])
    async def textchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Shows information about a text channel"""
        embed = discord.Embed(title='#' + channel.name, description=channel.topic) \
            .add_field(name='ID', value=channel.id) \
            .add_field(name='Created at', value=channel.created_at.strftime('%d.%m.%Y %H:%M'))
        if channel.is_nsfw():
            embed.add_field(name='NSFW', value='This channel is NSFW')
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)

    @info.command(aliases=['v', 'vc', 'voice'])
    async def voicechannel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """Shows information about a voice channel"""
        embed = discord.Embed(title=channel.name) \
            .add_field(name='ID', value=channel.id) \
            .add_field(name='Created at', value=channel.created_at.strftime('%d.%m.%Y %H:%M')) \
            .add_field(name='Bitrate', value=channel.bitrate)
        if channel.user_limit > 0:
            embed.add_field(name='User limit', value=channel.user_limit)
        members = ', '.join(map(lambda m: f'`{m.name}`', channel.members))
        if len(channel.members) > 1:
            embed.add_field(
                name='Members', value=f'`{len(channel.members)}` people ({members})')
        elif len(channel.members) > 0:
            embed.add_field(name='Members', value=f'`1` person ({members})')
        msg = await ctx.send(embed=embed)
        await utils.wait_to_delete(self.bot, ctx.message, msg)


def setup(bot):
    bot.add_cog(Admin(bot))
