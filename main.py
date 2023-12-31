import discord
import os
import random
import search_grimes # search class

from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import date, timedelta

intents = discord.Intents.default()
intents.message_content = True

# instantiate discord client 
client = discord.Client(intents=intents)
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))


# instantiate SearchGrimes class from search_grimes.py
grimes_web = search_grimes.SearchGrimes()

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
async def on_message(message): 
  # make sure bot doesn't respond to it's own messages to avoid infinite loop
  if message.author == client.user:
      return  
  # lower case message
  message_content = message.content.lower()  
  
  if message_content.startswith(f'{client.user.mention} $help'):
    with open('help.txt') as f:
      help_text = "\n".join(line.strip() for line in f)
    await message.channel.send(help_text)

  if message_content.startswith(f'{client.user.mention} $real name'):
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
        await message.channel.send(article['url'])
    else:
      await message.channel.send(f'My apologies master {message.author.name}, I was not able to find anything. Please try a few cycles later.')


    # key_words, search_words = grimes_web.key_words_search_words(message_content)
    # result_links = grimes_web.search(key_words)
    # links = grimes_web.send_link(result_links, search_words)
    
    # if len(links) > 0:
    #   for link in links:
    #    await message.channel.send(link)
    # else:
    #   await message.channel.send(f'My apologies master {message.author.name}, I was not able to find anything. Please try a few cycles later.')

  if message_content.startswith(f'{client.user.mention} $fact'):
    facts = open('facts.txt').read().splitlines()
    random_fact = random.choice(facts)
    await message.channel.send(random_fact)

# get bot token from .env and run client
# has to be at the end of the file
client.run(os.getenv('TOKEN'))