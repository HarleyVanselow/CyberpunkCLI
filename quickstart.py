import os
import discord
import json
from src.router import route
from click.testing import CliRunner
import shlex
import time
from discord import DMChannel
from src import TABLE
from src.sheetio import disconnect_character
from datetime import datetime, timedelta
from json import JSONDecodeError
client = discord.Client()

connection_duration = timedelta(seconds=90)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if not message.author.bot:
            m = message.content
            guild = client.guilds[0]
            member = await guild.fetch_member(message.author.id)
            character = member.display_name
            args = ['--character', character]
            connected = False
            conn = open('connections.json', 'r+')
            try:
                connections = json.load(conn)
            except JSONDecodeError:
                connections = {}
            if character in connections.keys():
                connection = connections[character]
                connection_time = datetime.strptime(connection['connected_at'], '%Y-%m-%d %H:%M:%S.%f')
                now = datetime.now()
                if (connection_time + connection_duration) >= now:
                    auth = connection['auth']
                    connection['commands'].append(m)
                    args += ['connect', connection['connected_to'], '--cmds',
                            ':'.join(connection['commands']), '--auth', auth]
                    connected = True
                    conn.close()
                else:
                    disconnect_character(character)
                    args += shlex.split(m)
            else:
                conn.close()
                args += shlex.split(m)
            runner = CliRunner()
            print(args)
            try:
                m = runner.invoke(route, args, catch_exceptions=False).output
            except Exception as e:
                m = e
            if connected and not isinstance(message.channel, DMChannel):
                await message.delete()
                m = ">>>" + m
            if m != "":
                await message.channel.send(m)


client = MyClient()
client.run(os.environ['DISCORD_TOKEN'])
