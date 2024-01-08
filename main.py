import discord
import os
import random
import asyncio
import utils

from discord.ext import commands
from discord.ext.tasks import loop
from discord import FFmpegPCMAudio
from discord.utils import get
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta
from constants import *

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# instantiate discord client 
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

'''
# If you are coding the bot on a local machine, use the python-dotenv package 
to get variables stored in .env file of your project from dotenv import load_dotenv
load_dotenv()
'''

load_dotenv()

@loop(seconds=MEMBER_COUNT_LOOP_SECONDS)
async def check_all_members():
  guild = bot.get_guild(GUILD_ID)
  MembersInServerCount = len(guild.members)
  bots = list(filter(utils.filter_bots, guild.members))
  channel = get(guild.channels, id=MEMBER_COUNT_CHANNEL_ID)
  amount = (MembersInServerCount - len(bots))
  new_channel_name = str(f'{str(MEMBER_COUNT_CHANNEL_PREFIX)}{amount}')
  current_channel_name = channel.name
  if new_channel_name == current_channel_name:
    pass
  elif new_channel_name != current_channel_name:
    await channel.edit(name=new_channel_name)

@bot.command()
async def list_audio(ctx):
  await ctx.send("Ακολουθεί η λίστα με τις διαθέσιμες ηχογραφήσεις:\n\t" 
                 + "\n\t".join(os.listdir(AUDIO_DIR)) 
                 + "\nΓια αναπαραγωγή ηχογράφησης, αντέγραψε το όνομα της ηχογράφησης από τις παραπάνω και γράψε:\n"
                 + "\t$play <το-όνομα-της-ηχογράφησης>")

@bot.command()
async def play(ctx, arg):
  if not ctx.message.author.voice:
    await ctx.send("Ζητώ συγνώμη δάσκαλε {}, αλλά πρέπει να είσαι σε voice channel για να κάνω join.".format(ctx.message.author.name))
    return
  else:
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()
    source = FFmpegPCMAudio(AUDIO_DIR + arg)
    voice.play(source)

@bot.command()
async def pause(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
  else:
    await ctx.send("Δεν ακούω κάποια ηχογράφηση για να μπορώ να την κάνω pause.")

@bot.command()
async def resume(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if voice.is_paused():
    voice.resume()
  else:
    await ctx.send("Παίζει ήδη μια ηχογράφηση, οπότε με τρόπο αγνοώ την εντολή resume.")

@bot.command()
async def stop(ctx):
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  voice.stop()

@bot.command()
async def leave(ctx):
  if ctx.voice_client:
    await ctx.guild.voice_client.disconnect()
  else:
    await ctx.send("Δεν θέλω να σε προσβάλω δάσκαλε {}, αλλά φαίνεται ότι βλέπεις παραισθήσεις, επειδή δεν είμαι σε voice channel αυτή τη στιγμή.".format(ctx.message.author.name))

# discord event to check when the bot is online 
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Game(PLAYING_ACTIVITY))
  check_all_members.start()
  await asyncio.sleep(ONE)
  print(f"{bot.user} is now online!")

@bot.event
async def on_member_join(member):
  channel = bot.get_channel(SYSTEM_CHANNEL_ID)
  await channel.send(f"{member.mention} " + utils.to_multi_line_text(WELCOME_FILE))

@bot.event
async def on_message(message): 
  # bot.process_commands(msg) is a couroutine that must be called here since we are overriding the on_message event
  await bot.process_commands(message)
  # make sure bot doesn't respond to it's own messages to avoid infinite loop
  if message.author == bot.user:
      return  
  # lower case message
  message_content = message.content.lower()  
  
  if FREE_STR in message_content and FREE_GAMES_CHANNEL_ID == message.channel.id:
    await message.add_reaction(FREE_GAMES_REACTION)

  if message_content.startswith(f"{bot.user.mention} " + HELP_COMMAND):
    await message.channel.send(utils.to_multi_line_text(MAGIC_FILE))

  if message_content.startswith(f"{bot.user.mention} " + REAL_NAME_COMMAND):
    await message.channel.send(REAL_NAME_RESPONSE)

  if message_content.startswith(f"{bot.user.mention} " + GREET_COMMAND):
    await message.channel.send(f"Δάσκαλε {message.author.name}, είναι τιμή μου που σε υπηρετώ. Εκ μέρους των Δημιουργών μας, θα κάνω ό,τι καλύτερο μπορώ.")

  if message_content.startswith(f"{bot.user.mention} " + RETRIEVE_COMMAND):
    news_results = newsapi.get_everything(q=GRIMES_STR,
                                          qintitle=GRIMES_STR,
                                          sources=BUSINESS_INSIDER,
                                          from_param=date.today() - timedelta(days=int(os.getenv("NEWS_API_DAYS_BEFORE_CURRENT"))),
                                          sort_by=PUBLISHED_AT,
                                          page_size=int(os.getenv("NEWS_API_PAGE_SIZE")))  

    if len(news_results) > ZERO:
      for article in news_results[ARTICLES]:
        if GRIMES_STR in article[TITLE].lower():
          await message.channel.send(article[URL_STR])
    else:
      await message.channel.send(f"Ζητώ συγνώμη δάσκαλε {message.author.name}, δεν κατάφερα να βρω κάτι. Παρακαλώ δοκίμασε μερικούς κύκλους αργότερα.")

  if message_content.startswith(f"{bot.user.mention} " + FACT_COMMAND):
    facts = open(FACTS_FILE).read().splitlines()
    random_fact = random.choice(facts)
    await message.channel.send(random_fact)

# get bot token from .env and run client
# has to be at the end of the file
bot.run(os.getenv("TOKEN"))