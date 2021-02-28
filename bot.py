#!/usr/bin/python

import discord
import configparser
from storage import Storage
import os
import asyncio


class Bot(discord.Client):
    members = {}
    storage = None

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.storage = Storage()
        self.storage.setup()
        self.loop.create_task(self.listen())

    async def listen(self):
        while True:
            messages = self.storage.select_multiple(
                "SELECT * FROM messages ORDER BY id desc;")

            for message in messages:
                try:
                    subscriptions = self.storage.select_multiple(
                        "SELECT * FROM subscriptions where process_name = ?", [message['process_name']])
                    for subscription in subscriptions:
                        channel = self.get_channel(int(subscription['channel_id']))
                        embed = discord.Embed(
                            title="Notification", description="", color=0x00ff00)
                        embed.add_field(
                            name="Process", value=message['process_name'], inline=True)
                        embed.add_field(
                            name="State", value=message['content'], inline=True)
                        await channel.send(embed=embed)
                    self.storage.query(
                        "DELETE FROM messages WHERE id=?", [message['id']])
                except Exception as e:
                    print(e)

            await asyncio.sleep(5)


    async def on_message(self, message):
        if message.author.bot or message.author == self.user:
            return
        if message.content.startswith('!'):
            if message.content.startswith('!subscribe'):
                subscription = message.content.split(' ')
                if (len(subscription) < 2):
                    await self.embed_message(message.channel, 'You must provide a process name.')
                    return
                subscription = subscription[1]
                count = self.storage.select_multiple(
                    "SELECT * FROM subscriptions WHERE process_name = ? ORDER BY id desc;", [subscription])
                if (len(count) == 0):
                    self.storage.query("INSERT INTO subscriptions (process_name, channel_id, server_id) VALUES (?, ?, ?)", [
                                       subscription, message.channel.id, message.channel.guild.id])
                    await self.embed_message(message.channel, 'You have been subscribed.')
                else:
                    await self.embed_message(message.channel, 'You are already subscribed to this process.')

            elif message.content.startswith('!unsubscribe'):
                subscription = message.content.split(' ')
                if (len(subscription) < 2):
                    await self.embed_message(message.channel, 'You must provide a process name.')
                    return
                subscription = subscription[1]
                row = self.storage.select_row(
                    "SELECT * FROM subscriptions where process_name=? AND channel_id=?", [subscription, message.channel.id])
                if (row):
                    self.storage.query(
                        "DELETE FROM subscriptions WHERE id=?", [row['id']])
                    await self.embed_message(message.channel, 'You have been unsubscribed.')
                else:
                    await self.embed_message(message.channel, 'You are were not subscribed to this process.')

    async def embed_message(self, channel, content):
        embed = discord.Embed(
            title="Notification", description="", color=0x00ff00)
        # embed.add_field(
        #     name="Fetlife", value=user.fetlife_name, inline=True)
        embed.add_field(
            name="Message", value=content, inline=False)
        await channel.send(embed=embed)


config = configparser.ConfigParser()
file_location = os.path.dirname(os.path.realpath(__file__))
config.read('{}/config.ini'.format(file_location))

client = Bot()
client.run(config['DEFAULT']['TOKEN'])
