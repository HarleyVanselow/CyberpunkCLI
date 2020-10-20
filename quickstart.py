import os
import discord
import json
from src.router import route
from click.testing import CliRunner
import shlex
import time
client = discord.Client()


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author.name == client.user.name:
            return
        elif message.content.startswith("!cp"):
            guild = client.guilds[0]
            member = await guild.fetch_member(message.author.id)
            character = member.display_name
            runner = CliRunner()
            args = shlex.split(message.content.split('!cp')[1])
            args = ['--character',character] + args
            result = runner.invoke(route, args)
            await message.channel.send(result.output)

client = MyClient()
with open('credentials.json') as cred:
    client.run(json.load(cred)['discord_token'])
