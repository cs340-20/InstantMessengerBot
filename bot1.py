# bot1.py
# A rewrite of bot.py, changing to the bot subclass from client superclass
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='$')

# Create new channels
## NEEDS TO: determine admin permissions of the cmd caller, 
# and check if the room being made already exists
@bot.command(name='makechannel')
#@commands.has_role('admin')
async def makechannel(ctx, channel_name='Voltron-Conference'):
	guild = ctx.guild
	existing_channel = discord.utils.get(guild.channels, name=channel_name)
	if not existing_channel:		
		print(f'Creating new channel: {channel_name}')
		await guild.create_text_channel(channel_name)

bot.run(TOKEN)
