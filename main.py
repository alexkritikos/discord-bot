import discord
import os
import random
import utils

from discord.ext import commands
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# instantiate discord client 
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$',intents=intents)
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
# If you are coding the bot on a local machine, use the python-dotenv package 
to get variables stored in .env file of your project from dotenv import load_dotenv
load_dotenv()
'''

load_dotenv()

@bot.command(name="summon_stalker")
async def join(ctx):
  if not ctx.message.author.voice:
    await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
    return
  else:
    channel = ctx.message.author.voice.channel
  await channel.connect()
  
@bot.command(name="dismiss_stalker")
async def leave(ctx):
  voice_client = ctx.message.guild.voice_client
  if voice_client.is_connected():
      await voice_client.disconnect()
  else:
      await ctx.send("The bot is not connected to a voice channel.")

# discord event to check when the bot is online 
@bot.event
async def on_ready():
  print(f"{bot.user} is now online!")

@bot.event
async def on_member_join(member):
  channel = bot.get_channel(1140325411126005903) # ίντριγκα
  await channel.send(f"{member.mention} " + utils.to_multi_line_text("welcome.txt"))

@bot.event
async def on_message(message): 
  # bot.process_commands(msg) is a couroutine that must be called here since we are overriding the on_message event
  await bot.process_commands(message)
  # make sure bot doesn't respond to it's own messages to avoid infinite loop
  if message.author == bot.user:
      return  
  # lower case message
  message_content = message.content.lower()  
  
  if message_content.startswith(f"{bot.user.mention} $help"):
    await message.channel.send(utils.to_multi_line_text("help.txt"))

  if message_content.startswith(f"{bot.user.mention} $real_name"):
    await message.channel.send("Claire Elise Boucher")

  if message_content.startswith(f"{bot.user.mention} $greet"):
    await message.channel.send(f"Master {message.author.name}, it is an honor to serve as your informant. On behalf of our Creators, I will do my best.")

  if message_content.startswith(f"{bot.user.mention} $retrieve"):
    news_results = newsapi.get_everything(q="grimes",
                                          qintitle="grimes",
                                          sources="business-insider",
                                          from_param=date.today() - timedelta(days=int(os.getenv("NEWS_API_DAYS_BEFORE_CURRENT"))),
                                          sort_by="publishedAt",
                                          page_size=int(os.getenv("NEWS_API_PAGE_SIZE")))  

    if len(news_results) > 0:
      for article in news_results["articles"]:
        if "grimes" in article["title"].lower():
          await message.channel.send(article["url"])
    else:
      await message.channel.send(f"My apologies master {message.author.name}, I was not able to find anything. Please try a few cycles later.")

  if message_content.startswith(f"{bot.user.mention} $fact"):
    facts = open("facts.txt").read().splitlines()
    random_fact = random.choice(facts)
    await message.channel.send(random_fact)

# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv("TOKEN"))