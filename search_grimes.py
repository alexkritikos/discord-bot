import requests
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class SearchGrimes:
  def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.3'}
        self.url = 'https://americansongwriter.com/?s='

  def key_words_search_words(self, user_message):
    words = user_message.split()[2:]
    keywords = '+'.join(words)
    search_words = ' '.join(words)
    return keywords, search_words

  def search(self, keywords):
    response = requests.get(self.url + keywords, headers = self.headers)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    print(soup)
    print(soup.findAll('a'))
    result_links = soup.findAll('a')
    return result_links
      
  def send_link(self, result_links, search_words): 
    send_link = set()
    for link in result_links:
        text = link.text.lower()
        if search_words in text and len(send_link) < int(os.getenv('MAX_RETURNED_LINKS')):  
          send_link.add(link.get('href'))
    return send_link