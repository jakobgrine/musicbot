import discord
from discord.ext import commands
import asyncio


class Context(commands.Context):
    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, both=True):
        ret = await super().send(content=content, tts=tts, embed=embed, file=file, files=files, nonce=nonce)
        if self.bot.config.get('delete_messages') and delete_after is not None:
            if both:
                await self.message.delete(delay=delete_after)
            await ret.delete(delay=delete_after)
        return ret


class Bot(commands.Bot):
    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)
