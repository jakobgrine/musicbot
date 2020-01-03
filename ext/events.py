import discord
from discord.ext import commands

PASSTHROUGH_EXCEPTIONS = (
    commands.PrivateMessageOnly, commands.NoPrivateMessage, commands.NotOwner,
    commands.TooManyArguments, commands.BadArgument, commands.CommandNotFound,
    commands.DisabledCommand
)


async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = f'Required argument `{error.param.name}` is missing'
    elif isinstance(error, commands.BadUnionArgument):
        if len(error.converters) > 1:
            converters = ', '.join(map(
                lambda c: f'`{c.__name__}`', error.converters[:-1])) + f' and `{error.converters[-1].__name__}`'
        else:
            converters = f'`{error.converters[0].__name__}`'
        message = f'Converting to {converters} failed for parameter `{error.param.name}`'
    elif isinstance(error, commands.MissingPermissions):
        permissions = map(lambda p: f'`{p}`', error.missing_perms)
        message = f'You are missing permissions to run this command: {permissions}'
    elif isinstance(error, commands.BotMissingPermissions):
        permissions = map(lambda p: f'`{p}`', error.missing_perms)
        message = f'The bot is missing permissions to run this command: {permissions}'
    elif isinstance(error, commands.NSFWChannelRequired):
        message = f'This command can only be used in NSFW channels'
    elif isinstance(error, PASSTHROUGH_EXCEPTIONS):
        message = str(error).replace('"', '`')
    else:
        raise error
    await ctx.send(f':x: **Error:** {message}', delete_after=5)


def setup(bot):
    bot.event(on_command_error)
