from app.helpers.logger import logger
from app.helpers.browser import Browser
from app.helpers.response import Response

logger.announcement('Initializing News', 'info')
logger.announcement('Successfully initialized News', 'success')

def scrapeCNNHeadlines():

    logger.announcement('Scraping CNN Headlines', 'info')

    url = 'https://www.cnn.com'
    soup = Browser().scraper(url)

    # Find the sections containing headlines
    headlines = soup.find_all('div', class_='stack__items')

    news  = []
    for headline in headlines:
        for link in headline.find_all('a'):
            if ('•' not in link.get_text().strip()):
                news.append({'title':link.get_text().strip(), 'url':url + link.get('href')})

    logger.announcement('Successfully scraped CNN Headlines', 'success')
    return Response.success(news)
