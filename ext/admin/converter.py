import discord
from discord.ext import commands
import re

__all__ = (
    'ExtensionConverter',
    'GuildConverter'
)


class ExtensionConverter(commands.Converter):
    """Converts to a :class:`~types.ModuleType`"""
    async def convert(self, ctx, argument):
        if not argument in ctx.bot.extensions:
            raise commands.BadArgument(f'Extension "{argument}" not found')
        return argument


class GuildConverter(commands.IDConverter):
    """Converts to a :class:`~discord.Guild`.

    All lookups are via the global guild cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID
    2. Lookup by name    
    """
    async def convert(self, ctx, argument):
        match = self._get_id_match(argument) or re.match(
            r'<@!?([0-9]+)>$', argument)

        if match is not None:
            guild_id = int(match.group(1))
            result = ctx.bot.get_guild(guild_id)
        else:
            def predicate(g): return g.name == argument
            result = discord.utils.find(predicate, ctx._state._guilds.values())

        if result is None:
            raise commands.BadArgument(f'Guild "{argument}" not found')

        return result
