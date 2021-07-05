import requests
from bs4 import BeautifulSoup
import sqlite3
import csv

HOST = 'https://www.gazeta.uz'
URL = 'https://www.gazeta.uz/ru/coronavirus/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}


def entry_data(data):
    con = sqlite3.connect('news.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news
        (title VARCHAR, description TEXT, link_news VARCHAR, date VARCHAR, image VARCHAR)
    """)

    for news in data:
        title = news['title']
        description = news['description']
        link_news = news['link_news']
        date = news['date']
        image = news['image']
        if not cur.execute("SELECT link_news FROM news WHERE link_news = ?", (link_news,)).fetchall():
            cur.execute("INSERT INTO news VALUES(?, ?, ?, ?, ?)", (title, description, link_news, date, image))
        else:
            print('Данные существуют в таблице')

    con.commit()
    con.close()


# https://www.gazeta.uz/ru/coronavirus?page=5
def get_html(url, params={}):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='nblock')
    news = []

    for item in items:
        news.append(
            {
                'title': item.find('h3').get_text(strip=True),
                'description': item.find('p').get_text(strip=True),
                'link_news': HOST + item.find('h3').find('a')['href'],  # .get('href')
                'date': item.find('div', class_='ndt').get_text(strip=True),
                'image': item.find('img', class_='lazy')['data-src'],
            }
        )
    return news


def parser():
    PAGENATION = int(input('Укажите количество страниц для парсинга: ').strip())
    html = get_html(URL)
    if html.status_code == 200:
        news = []
        for page in range(1, PAGENATION + 1):
            print(f'Парсим страницу: {page}')
            html = get_html(URL, params={'page': page})
            news.extend(get_content(html.text))
        entry_data(news)
    else:
        print('Error')


parser()
