import discord
import io
from PIL import Image
import numpy
import scipy
import scipy.cluster


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


async def dominant(asset: discord.Asset, n_clusters: int = 6) -> discord.Color:
    # Download the image
    result = io.BytesIO()
    await asset.save(fp=result)
    img = Image.open(result)

    # Convert the image if necessary
    if img.mode not in ['RGB', 'RGBA']:
        img = img.convert(mode='RGB')

    # Convert the image to a pixel array
    arr = numpy.asarray(img)
    shape = arr.shape
    arr = arr.reshape(numpy.prod(shape[:2]), shape[2]).astype(float)

    # Filter out transparent pixels
    if img.mode == 'RGBA':
        arr = arr[[pixel[3] > 0 for pixel in arr]]

    # Get dominant color
    codes, _ = scipy.cluster.vq.kmeans(arr, n_clusters)
    vecs, _ = scipy.cluster.vq.vq(arr, codes)
    counts, _ = numpy.histogram(vecs, len(codes))
    peak = codes[numpy.argmax(counts)]

    return discord.Color.from_rgb(int(peak[0]), int(peak[1]), int(peak[2]))


async def wait_to_delete(bot, invoked: discord.Message, sent: discord.Message, emoji: str = '❌'):
    def check(reaction, user):
        return reaction.message.id == sent.id and user != bot.user and reaction.emoji == emoji
    await sent.add_reaction(emoji)
    await bot.wait_for('reaction_add', check=check)
    await invoked.delete()
    await sent.delete()
