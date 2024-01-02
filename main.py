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
bot = commands.Bot(command_prefix='@GrimesStalker $',intents=intents)
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
# If you are coding the bot on a local machine, use the python-dotenv package 
to get variables stored in .env file of your project from dotenv import load_dotenv
load_dotenv()
'''

load_dotenv()

@bot.command(name="join")
async def join(ctx):
  if ctx.author.voice:
    channel = ctx.message.author.voice.channel
    await channel.connect()
  else:
    await ctx.send("My apologies, but you must be in a voice channel so that I can join you.")

@bot.command(name="leave")
async def leave(ctx):
  if ctx.voice_client:
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send("I do not want to offend you, but you must be seeing hallucinations, because I am not in a voice channel at the moment.")

# discord event to check when the bot is online 
@client.event
async def on_ready():
  print(f"{client.user} is now online!")

@client.event
async def on_member_join(member):
  channel = client.get_channel(1140325411126005903) # ίντριγκα
  await channel.send(f"{member.mention} " + utils.to_multi_line_text("welcome.txt"))

@client.event
async def on_message(message): 
  # make sure bot doesn't respond to it's own messages to avoid infinite loop
  if message.author == client.user:
      return  
  # lower case message
  message_content = message.content.lower()  
  
  if message_content.startswith(f"{client.user.mention} $help"):
    await message.channel.send(utils.to_multi_line_text("help.txt"))

  if message_content.startswith(f"{client.user.mention} $real_name"):
    await message.channel.send("Claire Elise Boucher")

  if message_content.startswith(f"{client.user.mention} $summon"):
    await message.channel.send(f"Master {message.author.name}, it is an honor to serve as your informant. On behalf of our Creators, I will do my best.")

  if message_content.startswith(f"{client.user.mention} $retrieve"):
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

  if message_content.startswith(f"{client.user.mention} $fact"):
    facts = open("facts.txt").read().splitlines()
    random_fact = random.choice(facts)
    await message.channel.send(random_fact)

# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv("TOKEN"))