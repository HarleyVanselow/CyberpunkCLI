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
            m = message.content.split('!cp ')[1]
            guild = client.guilds[0]
            member = await guild.fetch_member(message.author.id)
            character = member.display_name
            args = ['--character',character]
            connected = False
            with open('connections.json') as conns:
                connections = json.load(conns)
                if character in connections.keys():
                    connected = True
                    connection = connections[character].split(":")
                    connection.append(m)
                    args += ['connect', connection[0], '--cmds', ':'.join(connection[1:])]
                else:
                    args += shlex.split(m)
            runner = CliRunner()
            print(args)
            m = runner.invoke(route, args).output
            if connected:
                await message.delete()
                m = ">>>" + m
            if m != "":
                await message.channel.send(m)

client = MyClient()
with open('credentials.json') as cred:
    client.run(json.load(cred)['discord_token'])
