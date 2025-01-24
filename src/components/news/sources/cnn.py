from src.utils.browser import Browser
from datetime import datetime

browser = Browser()

url = 'https://www.cnn.com'
max_articles = 30

def scrape_articles():

    all_data = []
    soup = browser.scraper(url)
    article_urls = set()
    current_year = datetime.now().year

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href and href.startswith('/') and href != '#':
            full_url = f"{url}{href}"
        else:
            full_url = href
            
        if url_is_article(full_url, current_year):
            article_urls.add(full_url)
            
    for article_url in list(article_urls)[:max_articles]:
        parsed_data = parse(article_url)
        all_data.append(parsed_data)
        
    return all_data

def url_is_article(url, current_year):
    if url:
        if 'cnn.com/{}/'.format(current_year) in url and '/gallery/' not in url:
            return True
    return False

def return_text_if_not_none(element):
    if element:
        return element.text.strip()
    else:
        return ''

def parse(article_url):
    soup = browser.scraper(article_url)
    title = return_text_if_not_none(soup.find('h1', {'class': 'headline__text'}))
    author = soup.find('span', {'class': 'byline__name'})
    if not author:
        author = soup.find('span', {'class': 'byline__names'})
    author = return_text_if_not_none(author)
    article_content = return_text_if_not_none(soup.find('div', {'class': 'article__content'}))
    timestamp = return_text_if_not_none(soup.find('div', {'class': 'timestamp'}))
    
    # Find main image
    image_container = soup.find('div', {'class': 'image__container'})
    main_image = ''
    if image_container:
        img_tag = image_container.find('img', {'class': 'image__dam-img'})
        if img_tag and 'src' in img_tag.attrs:
            main_image = img_tag['src']
    
    timestamp_data = parse_timestamp(timestamp) if timestamp else ['', '', '', '']
    
    return {
        'title': title.strip(),
        'author': author.strip(),
        'content': article_content.strip(),
        'url': article_url,
        'timestamp_type': timestamp_data[0],
        'time': timestamp_data[1],
        'day': timestamp_data[2],
        'year': timestamp_data[3],
        'image': main_image
    }

def parse_timestamp(timestamp):
    if 'Published' in timestamp:
        timestamp_type = 'Published'
    elif 'Updated' in timestamp:
        timestamp_type = 'Updated'
    else:
        timestamp_type = ''

    article_time, article_day, article_year = timestamp.replace('Published', '').replace('Updated', '').split(', ')
    return timestamp_type, article_time.strip(), article_day.strip(), article_year.strip()