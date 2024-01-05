import discord
import os
import random
import utils
import asyncio

from discord.ext import commands
from discord.ext.tasks import loop
from discord import FFmpegPCMAudio
from discord.utils import get
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# instantiate discord client 
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
# If you are coding the bot on a local machine, use the python-dotenv package 
to get variables stored in .env file of your project from dotenv import load_dotenv
load_dotenv()
'''

load_dotenv()

@loop(seconds=30)
async def check_all_members():
  guild = bot.get_guild(1140325411126005901) # Koutokomia
  MembersInServerCount = len(guild.members)
  channel = get(guild.channels, id=1192792733039996938) # Ψυχολογικά όντα
  amount = (MembersInServerCount)
  prevtname = str(f'{str("All Members: ")}{amount}')
  tname = channel.name
  if prevtname == tname:
      pass
  elif prevtname != tname:
      await channel.edit(name=f'{str("All Members: ")}{amount}')

@bot.command()
async def list_audio(ctx):
  await ctx.send("Here is a list of the available audio files:\n\t" 
                 + "\n\t".join(os.listdir("./audio")) 
                 + "\nTo play a file, copy-paste a file name from above and type:\n"
                 + "$play <song-name>")

@bot.command()
async def play(ctx, arg):
  if not ctx.message.author.voice:
    await ctx.send("My apologies master {}, but you must be in a voice channel so that I can join you.".format(ctx.message.author.name))
    return
  else:
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()
    source = FFmpegPCMAudio("./audio/" + arg)
    voice.play(source)

@bot.command()
async def pause(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
  else:
    await ctx.send("There is no audio to pause right now.")

@bot.command()
async def resume(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if voice.is_paused():
    voice.resume()
  else:
    await ctx.send("There is no paused audio right now.")

@bot.command()
async def stop(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  voice.stop()

@bot.command()
async def leave(ctx):
  if ctx.voice_client:
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send("I do not want to offend you master {}, but you must be seeing hallucinations, because I am not in a voice channel at the moment.".format(ctx.message.author.name))

# discord event to check when the bot is online 
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game("NieR: Automata™"))
  check_all_members.start()
  await asyncio.sleep(1)
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
  
  if "free" in message_content and message.channel.id == 1190706436683071648: #free-games
    await message.add_reaction("\U0001F42D")

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