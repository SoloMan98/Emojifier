import io
import re
import math
import sys
import discord
from discord.ext import commands
from PIL import Image, ImageSequence
import vars
from vars import bot
from gif_script import resize_gif
from classes import DiscordImage
import cv2
import numpy as np

# TODO Multi-alias


class EmojiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='emojify')
    async def full_emojify(self, ctx, name=None):

        image = DiscordImage()

        try:
            if re.findall(r'&emojify above', ctx.message.content):
                await above(self, ctx, image.read_attachment)
            else:
                await image.read_attachment(ctx.message)
        except Exception as e:
            print(f'error: {e}')

        image.name = await get_name(ctx.message, image.name)

        if image.data is None:
            return await ctx.send(vars.error_dict[101])
        # check filetype
        if image.filetype is None:
            return await ctx.send(vars.error_dict[104])

        # #make sure of valid name
        # image.name = re.sub(r'[^0-9a-zA-Z]+', '', image.name)
        # if len(image.name) < 3:
        #     image.name = f"emoji{image.name}"

        # show typing to user because this can take some time
        async with ctx.channel.typing():
            # convert attachment to bytes, open with pillow,
            # then resize the image to fit size param. output is in bytes
            if image.filetype == ".gif":
                byte_arr = downscale_gif(io.BytesIO(image.data))
            else:
                byte_arr = resize_image(Image.open(io.BytesIO(image.data)))

            await ctx.guild.create_custom_emoji(name=image.name,
                                                image=byte_arr)
            return await ctx.send(f"successfully added to {ctx.guild.name}'s emojis as :{image.name}:")

    @commands.command(name='resize')
    async def resize_emoji(self, ctx):

        image = DiscordImage()
        target = 256000

        try:
            if re.findall(r'&resize above', ctx.message.content):
                await above(self, ctx, image.read_attachment)
            else:
                await image.read_attachment(ctx.message)
        except Exception as e:
            print(f'error: {e}')
            return await ctx.send(vars.error_dict[101])

        image.name = await get_name(ctx.message, image.name)

        if image.data is None:
            return await ctx.send(vars.error_dict[101])

        if image.filetype is None:
            return await ctx.send(vars.error_dict[104])

        # check if image meets requirements already
        if get_size(Image.open(io.BytesIO(image.data))) <= target:
            return await ctx.send("This image is already good to go")

        closeimg = io.BytesIO(image.data)
        # read attachments in bytes
        imageIO = Image.open(io.BytesIO(image.data))
        async with ctx.channel.typing():
            if image.filetype == ".gif":
                imgByteArr = downscale_gif(closeimg)
            else:
                imgByteArr = resize_image(imageIO, target)

        accuracy = (sys.getsizeof(imgByteArr)/target) * 100

        await ctx.send(f"Accuracy: {round(accuracy, 2)}%\nSize:\ {sys.getsizeof(imgByteArr)/1000} KB")
        return await ctx.send(f"Resized Image:", file=discord.File(io.BytesIO(imgByteArr), filename=f'{image.name}{image.filetype}'))

    @commands.command(name='pngify')
    async def pngify(self, ctx):
        image = DiscordImage()

        try:
            if re.findall(r'&pngify above', ctx.message.content):
                await above(self, ctx, image.read_attachment)
            else:
                await image.read_attachment(ctx.message)
        except Exception as e:
            print(f'error: {e}')
            return await ctx.send(vars.error_dict[101])

        image.name = await get_name(ctx.message, image.name)

        if image.data is None:
            return await ctx.send(vars.error_dict[101])

        if image.filetype is None:
            return await ctx.send(vars.error_dict[104])

        async with ctx.channel.typing():
            open_cv_image = \
                np.array(Image.open(io.BytesIO(image.data)).convert('RGB'))
            open_cv_image = open_cv_image[:, :, ::-1].copy()

            gray_open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

            retVal, thresh = cv2.threshold(gray_open_cv_image, 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            image_contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                                 cv2.CHAIN_APPROX_SIMPLE)

            for i in image_contours:
                if cv2.contourArea(i) > 100:
                    break

            mask = np.zeros(open_cv_image.shape[:2], np.uint8)

            cv2.drawContours(mask, [i], -1, 255, -1)

            b, g, r = cv2.split(open_cv_image)

            rgba = [b, g, r, mask]

            new_img = cv2.merge(rgba, 4)

            is_success, im_buf_arr = cv2.imencode(".png", new_img)

        return await ctx.send(f"PNGified Image:", file=discord.File(io.BytesIO(im_buf_arr), filename=f'{image.name}.png'))


async def above(self, ctx, fn):

    # get attachments from last 5 messages
    async for message in ctx.channel.history(limit=5):
        if(await fn(message)):
            return await fn(message)
        else:
            pass
    return None


def resize_image(image, target=256000, size_out=False):

    x, y = image.size
    asp_ratio = y/x
    start_size = (target/1000) * 4  # the starting dimensions for the image
    size = start_size, start_size * asp_ratio  # maintain aspect ratio

    counter = 0
    while True:
        counter += 1
        image.thumbnail(size)  # scale image with pillow

        # return binary data
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        bytesize = sys.getsizeof(imgByteArr)
        # bytesize = get_size(image)

        # stats
        # dims = [int(dim) for dim in size]
        # print(f"Dimensions: {dims}")
        # print("Bytes: {:,}".format(bytesize))
        # print("Difference in Bytes: {:,}".format(bytesize - target))

        # check size
        if bytesize <= target:
            print(f"{counter} loops")
            break

        factor = calc_factor(bytesize - target, target)
        # adjust size of image based on multiplier
        size = tuple(factor * x for x in size)

    return imgByteArr if not size_out else size


def downscale_gif(gif, target=256000, size_out=False):
    start_size = (target/1000)  # the starting dimensions for the image
    size = start_size, start_size  # maintain aspect ratio

    counter = 0
    while True:
        counter += 1
        imgByteArr = resize_gif(gif, size)
        bytesize = sys.getsizeof(imgByteArr)

        # stats
        # dims = [int(dim) for dim in size]
        # print(f"Dimensions: {dims}")
        # print("Bytes: {:,}".format(bytesize))
        # print("Difference in Bytes: {:,}".format(bytesize - target))

        # check size
        if bytesize <= target:
            print(f"{counter} loops")
            break

        factor = calc_gif_factor(bytesize - target, target)
        # adjust size of image based on multiplier
        size = tuple(factor * x for x in size)
    return imgByteArr if not size_out else size


# calculate sizing factor based on byte differential
def calc_factor(difference, target):
    if difference > target * 3:
        return .5
    if difference > target / 2:
        return .9
    if difference > 100000:
        return .95
    if difference > 10000:
        return .99
    return .995


# calculate sizing factor based on byte differential
def calc_gif_factor(difference, target):
    if difference > target * 3:
        return .5
    if difference > target / 2:
        return .9
    if difference > 100000:
        return .95
    if difference > 10000:
        return .98
    return .99


def get_size(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    return sys.getsizeof(imgByteArr)


# make sure of valid name
async def get_name(msg, name):

    message = msg.content
    message = message.replace(" above", "")
    message = re.sub(r' https?://[^\s]+', '', message)
    try:
        name = re.findall(r'&emojify\s([0-9a-zA-Z]*)?', message)[0]
    except Exception as e:
        print(f"error: {e}")

    if name == "":
        try:
            name = msg.attachments[0].filename[:-4]
        except Exception as e:
            print(f"error: {e}")
            name = ""

    #make sure of valid name
    name = re.sub(r'[^0-9a-zA-Z]+', '', name)
    if len(name) < 3:
        name = f"emoji{name}"

    return name


def setup(bot):
    bot.add_cog(EmojiCommands(bot))
