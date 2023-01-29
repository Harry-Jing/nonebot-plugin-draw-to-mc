import re
import httpx
import json
import asyncio
import websockets

from io import BytesIO
from asyncio import sleep


from nonebot import Bot
from nonebot import get_driver
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent

from .config import Config

plugin_config = Config.parse_obj(get_driver().config).dict()


command_send = on_command(cmd = '保存到mc', aliases={'保存到MC'})


@command_send.handle()
async def drawtomc(event: MessageEvent, arg: Message = CommandArg()):
    if event.reply:
        match_obj = re.search(r'\[CQ:image.*?url=(?P<url>.*?)\]', str(event.reply.message))
    else:
        match_obj = re.search(r'\[CQ:image.*?url=(?P<url>.*?)\]', str(arg))
    if not match_obj:
        await command_send.finish('未找到图片')
    url = match_obj.group('url')
    logger.info('url = '+url)
    file_name = re.sub(r'\s+', '', arg.extract_plain_text())
    if not file_name:
        await command_send.finish('未找到定义名称')
    data = json.dumps({'url':url, 'file_name': file_name}).encode(encoding='utf-8')
    logger.debug(f'{data=}')
    async with websockets.connect("ws://localhost:8765/save/url") as websocket:
        try:
            await websocket.send(data)
            response = await websocket.recv()
        except Exception as exc:
            await command_send.send('操作未完成')
            raise exc
        await command_send.finish(f'返回消息：{response}')