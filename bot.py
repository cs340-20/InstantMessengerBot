# bot1.py
# A rewrite of bot.py, changing to the bot subclass from client superclass

import os
import discord
import word_filter
import asyncio
import urllib

from datetime import datetime 
from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands, tasks
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='$')

base_role_name = "Plebs"
time_out_time = 0

#Boolean used to see if it is midnight
def checkIfMidnight():
	now = datetime.now()
	seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
	return seconds_since_midnight == 0


#Prints to console connection confirmation, initializes roles needed for bot functionality
@bot.event
async def on_ready():

	guild = discord.utils.get(bot.guilds, name=GUILD)
	guild_roles = guild.roles
	found = False

	print(
		f'{bot.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)
	#removes permmisions from @everyone
	for i in guild_roles:
		if i.name == "@everyone":
			general_permissions = i.permissions
			await i.edit(permissions = discord.Permissions.none())
								
	#intitalizes base role type that gives user permissions normally given by @everyone
	for i in guild_roles:
		if base_role_name == i.name:
			found = True		
	
	if found == False:
		await guild.create_role(name = base_role_name, permissions = general_permissions )


# Welcome DM to new user
@bot.event
async def on_member_join(member):
	
	guild = discord.utils.get(bot.guilds, name=GUILD)
	guild_roles = guild.roles

	for i in guild_roles:
		if i.name == base_role_name:
			base_role = i

	await member.create_dm()
	await member.edit(roles = [base_role])
	await member.dm_channel.send(
		content = f'VOLTRON WELCOMES YOU, {member.name}'
	)

#client message parsing 
@bot.event
async def on_message(message):

	if (message.author == bot.user):
		return

	#checks all user input against list of banned words
	if (word_filter.banned_string(message.content)):
		user = message.author
		await message.delete()
		await message.author.send('Please no swearing in my Christian Discord Server')
		print(f'Banned message from {user}')

	await bot.process_commands(message)
	
@bot.command(name = "meme")
async def caption(ctx, fontsize:int, x:int=0, y:int=0, *, Text:str):

	fp = ctx.message.attachments[0].filename
	await ctx.message.attachments[0].save(fp, seek_begin=True, use_cached=False)
	
	image = Image.open(fp)
	font_type = ImageFont.truetype("arial.ttf", fontsize)
	draw = ImageDraw.Draw(image)
	draw.text(xy = (x, y), text= Text, fill = (255,255,255), font = font_type)
	image.save(fp)

	final = open(fp, "rb")
	final_send = discord.File(final)

	await ctx.channel.send(file = final_send)

	final.close()
	os.remove(fp)


#documentation for the bot
@bot.command(name = 'documentation')
async def documentation(ctx):
	await ctx.channel.send("Please see this link for a detailed list of commands and their syntax: https://github.com/cs340-20/InstantMessengerBot/blob/master/README.md")

  
#Kicks a user from the server. They may join back at any time
@bot.command(name = 'kick')
async def kick(ctx, member : discord.Member, *, reason = "none"):

	if (reason != "none"):
		await member.create_dm()
		await member.dm_channel.send( content = ("You were kicked for the following reason: %s" % (reason)) )

	await member.kick(reason = reason)


#bans a user from the server.
@bot.command(name = 'ban')
async def ban(ctx, member : discord.Member, days = 0, *, reason = "none"):

	if (reason != "none"):
		await member.create_dm()
		await member.dm_channel.send( content = ("You were banned for the following reason: %s" % (reason)) )

	await member.ban(reason = reason, delete_msg_days = days)

#puts a user in timeout, prventing them from sending any messages but keeping them in the server
@bot.command(name = 'timeout')
async def timeout(ctx, member : discord.Member, TO_time = 0):

	guild = ctx.guild
	old_roles = member.roles	
	guild_roles = guild.roles
	timeout_role_name = "Timeout"
	found = False
	
	time_out_time = TO_time

	for i in guild_roles:
		if i.name == timeout_role_name: 
			timeout_role = i
			found = True
	
	if found == False:
		timeout_role = await guild.create_role(name = timeout_role_name)

	await member.edit(roles = [timeout_role])

	loop = asyncio._get_running_loop()
	end_time = loop.time() + (TO_time *60)

	await member.create_dm()
	await member.dm_channel.send( content = ("You have been timed out from the server for %d minutes." % (TO_time)) )

	while True:
		
		if(loop.time() + 1) >= end_time:
			await member.edit(roles = old_roles)
			break
		await asyncio.sleep(1)
	
	await member.dm_channel.send( content = ("You are no longer timed out") )

#adds a word to a file containing all banned words
@bot.command(name='ban_word')
async def ban_word(ctx, *, word = ''):
	
	if(word != ''):
		word_filter.ban_string(word)


#makes squad function
@bot.command(name='squad')
async def makechannel(ctx, num_user=5, cname='Temp Voice'):
#check if name is in cat list
	guild = ctx.guild
	cat = discord.utils.get(ctx.guild.categories, name='Member Channels')
	if not cat:
		await ctx.guild.create_category('Member Channels')
		await ctx.send("There is no category for Member channels. Creating one now and try again :-)")
		return

	#make user channel
	await guild.create_voice_channel(cname, category=cat, user_limit=num_user)


#deletes text channels from user input
@bot.command(name='deletechannel')
async def makechannel(ctx, channel_name=''):
	guild = ctx.guild
	existing_channel = discord.utils.get(guild.channels, name=channel_name)
	cat = discord.utils.get(ctx.guild.categories, name='Member Channels')

#check if name is in cat list
	for channel in cat.channels:
		if (channel.name == channel_name):
			await ctx.send("Deleting temporary user channel")
			await channel.delete()
			return
	
	await ctx.send("There is no user text channel in Member channels with that name, you cant delete non-temp channels.")
	return


#makes text channels from user input
@bot.command(name='makechannel')
#@commands.has_role('admin')
async def makechannel(ctx, channel_name='Voltron-Conference'):
	guild = ctx.guild
	existing_channel = discord.utils.get(guild.channels, name=channel_name)
	cat = discord.utils.get(ctx.guild.categories, name='Member Channels')
	if not cat:
		await ctx.guild.create_category('Member Channels')
		print(f'Creating new channel: {channel_name}')
		await ctx.send("There is no category for Member channels. Creating one now and try again :-)")
		return

	if not existing_channel:		
		print(f'Creating new channel: {channel_name}')
		await guild.create_text_channel(channel_name, category=cat)
	

#translate command 
@bot.command(name='translate')
async def translate(ctx, msg="ex phrase: $translate \"Hello!\" french" , dst='english'):
    
    #sets up translator object
    translator = Translator()
    
    #A list made of a key-map for languages
    LANGUAGES = {
        'af': 'afrikaans',
        'sq': 'albanian',
        'am': 'amharic',
        'ar': 'arabic',
        'hy': 'armenian',
        'az': 'azerbaijani',
        'eu': 'basque',
        'be': 'belarusian',
        'bn': 'bengali',
        'bs': 'bosnian',
        'bg': 'bulgarian',
        'ca': 'catalan',
        'ceb': 'cebuano',
        'ny': 'chichewa',
        'zh-cn': 'chinese',
        'co': 'corsican',
        'hr': 'croatian',
        'cs': 'czech',
        'da': 'danish',
        'nl': 'dutch',
        'en': 'english',
        'eo': 'esperanto',
        'et': 'estonian',
        'tl': 'filipino',
        'fi': 'finnish',
        'fr': 'french',
        'fy': 'frisian',
        'gl': 'galician',
        'ka': 'georgian',
        'de': 'german',
        'el': 'greek',
        'gu': 'gujarati',
        'ht': 'haitian',
        'ha': 'hausa',
        'haw': 'hawaiian',
        'iw': 'hebrew',
        'hi': 'hindi',
        'hmn': 'hmong',
        'hu': 'hungarian',
        'is': 'icelandic',
        'ig': 'igbo',
        'id': 'indonesian',
        'ga': 'irish',
        'it': 'italian',
        'ja': 'japanese',
        'jw': 'javanese',
        'kn': 'kannada',
        'kk': 'kazakh',
        'km': 'khmer',
        'ko': 'korean',
        'ku': 'kurdish',
        'ky': 'kyrgyz',
        'lo': 'lao',
        'la': 'latin',
        'lv': 'latvian',
        'lt': 'lithuanian',
        'lb': 'luxembourgish',
        'mk': 'macedonian',
        'mg': 'malagasy',
        'ms': 'malay',
        'ml': 'malayalam',
        'mt': 'maltese',
        'mi': 'maori',
        'mr': 'marathi',
        'mn': 'mongolian',
        'my': 'myanmar',
        'ne': 'nepali',
        'no': 'norwegian',
        'ps': 'pashto',
        'fa': 'persian',
        'pl': 'polish',
        'pt': 'portuguese',
        'pa': 'punjabi',
        'ro': 'romanian',
        'ru': 'russian',
        'sm': 'samoan',
        'gd': 'gaelic',
        'sr': 'serbian',
        'st': 'sesotho',
        'sn': 'shona',
        'sd': 'sindhi',
        'si': 'sinhala',
        'sk': 'slovak',
        'sl': 'slovenian',
        'so': 'somali',
        'es': 'spanish',
        'su': 'sundanese',
        'sw': 'swahili',
        'sv': 'swedish',
        'tg': 'tajik',
        'ta': 'tamil',
        'te': 'telugu',
        'th': 'thai',
        'tr': 'turkish',
        'uk': 'ukrainian',
        'ur': 'urdu',
        'uz': 'uzbek',
        'vi': 'vietnamese',
        'cy': 'welsh',
        'xh': 'xhosa',
        'yi': 'yiddish',
        'yo': 'yoruba',
        'zu': 'zulu',
        'fil': 'Filipino',
        'he': 'Hebrew'
    }
    LANGCODES = dict(map(reversed, LANGUAGES.items()))
    
    #translator(phrase, destination lang, source language)
    newlang = translator.translate(msg, LANGCODES[dst.lower()], src='auto')

    #print to console and print to server
    print(f'translated {msg} to {newlang.text}')
    await ctx.send(newlang.text)

bot.run(TOKEN)

