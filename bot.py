# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


# Welcome DM
@client.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send(
		f'VOLTRON WELCOMES YOU, {member.name}'
	)


# Sends a volton message on Assemble!
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '$assemble!':
        response = 'LETS GO VOLTRON FORCE! ASSEMBLE!'
        await message.channel.send(response)

# Keep track of new users who join
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


client.run(TOKEN)

