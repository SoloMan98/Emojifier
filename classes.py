import requests
import re


class DiscordImage:

    def __init__(self, data=None, filetype=None, name=""):
        self.data = data
        self.filetype = filetype
        self.name = name

    async def read_attachment(self, message):
        if url:=re.findall(r'https?://[^\s]+',
                           message.content):
            try:
                self.data, self.filetype = await self.read_link(message, url)
            except Exception as e:
                print(f'error: {e}')
        elif await self.__get_attachments(message):
            self.data = await self.__get_attachments(message)
            if (self.__check_type(
             message.attachments[0].filename[-4:]))is None:
                self.data = None
            else:
                self.filetype = self.__check_type(
                        message.attachments[0].filename[-4:])
                self.name = message.attachments[0].filename[:-4]
        if self.data is None or self.filetype is None:
            return False
        else:
            return True

    async def read_link(self, message, url):
        response = requests.get(url[0])

        filetype = re.findall(r'PNG|b\'\\xff|GIF', str(response.content))

        if filetype:
            filetype = filetype[0]
            if filetype == "b\'\\xff":
                filetype = "JPG"
            filetype = filetype.lower()
            filetype = f".{filetype}"
            filetype = self.__check_type(filetype)
        return response.content, filetype

    async def __get_attachments(self, msg):
        if msg.attachments:
            return await msg.attachments[0].read()

    def __check_type(self, ext):
        type = None
        # loops through supported extensions and checks if image has one
        for filetype in (".png", ".jpg", ".gif"):
            if ext == filetype:
                type = filetype
                break
        return type
