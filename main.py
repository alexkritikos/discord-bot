import discord
import os
import random

from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# instantiate discord client 
client = discord.Client(intents=intents)
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

'''
# If you are coding the bot on a local machine, use the python-dotenv package 
to get variables stored in .env file of your project from dotenv import load_dotenv
load_dotenv()
'''

load_dotenv()

# discord event to check when the bot is online 
@client.event
async def on_ready():
  print(f'{client.user} is now online!')

@client.event
async def on_member_join(member):
  channel = client.get_channel(1140325411126005903)
  await channel.send()

@client.event
async def on_message(message): 
  # make sure bot doesn't respond to it's own messages to avoid infinite loop
  if message.author == client.user:
      return  
  # lower case message
  message_content = message.content.lower()  
  
  if message_content.startswith(f'{client.user.mention} $test'):
    with open('welcome.txt') as file:
      welcome_text = "\n".join(line.strip() for line in file)
    message.channel.send(welcome_text)

  if message_content.startswith(f'{client.user.mention} $help'):
    with open('help.txt') as file:
      help_text = "\n".join(line.strip() for line in file)
    message.channel.send(help_text)

  if message_content.startswith(f'{client.user.mention} $real_name'):
    await message.channel.send("Claire Elise Boucher")

  if message_content.startswith(f'{client.user.mention} $summon'):
    await message.channel.send(f'Master {message.author.name}, it is an honor to serve as your informant. On behalf of our Creators, I will do my best.')

  if message_content.startswith(f'{client.user.mention} $retrieve'):
    news_results = newsapi.get_everything(q='grimes',
                                          qintitle='grimes',
                                          sources='business-insider',
                                          from_param=date.today() - timedelta(days=int(os.getenv('NEWS_API_DAYS_BEFORE_CURRENT'))),
                                          sort_by='publishedAt',
                                          page_size=int(os.getenv('NEWS_API_PAGE_SIZE')))  

    if len(news_results) > 0:
      for article in news_results['articles']:
        if "grimes" in article['title'].lower():
          await message.channel.send(article['url'])
    else:
      await message.channel.send(f'My apologies master {message.author.name}, I was not able to find anything. Please try a few cycles later.')

  if message_content.startswith(f'{client.user.mention} $fact'):
    facts = open('facts.txt').read().splitlines()
    random_fact = random.choice(facts)
    await message.channel.send(random_fact)

# get bot token from .env and run client
# has to be at the end of the file
client.run(os.getenv('TOKEN'))