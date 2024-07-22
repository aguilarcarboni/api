import requests
from bs4 import BeautifulSoup
import time

def scrape_comics():

    res = requests.get('https://comicbookreadingorders.com/marvel/marvel-master-reading-order-part-1/')

    soup = BeautifulSoup(res.content, 'html.parser')
    print(soup.prettify())

    content = soup.find('div', id='panel-e1828-e29')
    paragraphs = content.find_all('p')

    comics = []

    for paragraph in paragraphs:
        comics.append(paragraph.text)

    return comics

def scrape_cnn_headlines():
    # URL of the news site
    url = 'https://www.cnn.com'

    # Send a request to fetch the HTML content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the web page.")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the sections containing headlines
    headlines = soup.find_all('div', class_='stack__items')

    for link in headlines[0].find_all('a'):
        print(link.get_text().strip())
        print(url + link.get('href'))
        print('\n')

scrape_cnn_headlines()
time.sleep(5)