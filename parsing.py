import aiohttp
from bs4 import BeautifulSoup
import typing as tp
import datetime
import os

import models


async def get_articles_habr(links_global) -> tp.List[models.Article]:
    async with aiohttp.ClientSession() as session:
        await session.get('https://account.habr.com/login')

        cookie_token = [val.value for key, val in session.cookie_jar.filter_cookies(
            "https://account.habr.com/login").items()][0]
        payload_login = {
            'state': '',
            'consumer': 'default',
            'email': os.environ.get('HABR_MAIL'),
            'password': os.environ.get('HABR_PASSWORD'),
            'captcha': '',
            'g-recaptcha-response': '',
            'captcha_type': 'recaptcha'
        }
        headers = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript,'
                      ' */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '129',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': f'acc_csid={cookie_token};',
            'DNT': '1',
            'Host': 'account.habr.com',
            'Origin': 'https://account.habr.com',
            'Referer': 'https://account.habr.com/login/',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        await session.post('https://account.habr.com/ajax/login/', data=payload_login, headers=headers)
        await session.get('https://habr.com/kek/v1/auth/habrahabr/?back=/ru/all/&hl=ru')
        news_page = await session.get('https://habr.com/ru/feed/')
        news = await news_page.read()
        pages = BeautifulSoup(news, 'html.parser').find_all('article', {'class': 'tm-articles-list__item'})

        data = []
        for el in pages:
            if el.find('div', {'class': 'tm-article-snippet'}) is not None:
                link = 'https://habr.com' + el.find('a', {'class': 'tm-article-snippet__title-link'}).get('href'),
                rating = el.find('span', {'data-test-id': 'votes-meter-value'}).text,
                date = datetime.datetime.strptime(el.find('time').get('title'), '%Y-%m-%d, %H:%M')

                if link[0] not in links_global and (datetime.date.today() - date.date()).days in (0, 1, 2):
                    data.append((link[0], rating[0], date))
                    links_global.append(link[0])

    return [await models.Article.from_page(el) for el in data]


async def get_articles_tds(links_global) -> tp.List[models.Article]:
    async with aiohttp.ClientSession() as session:
        domain = 'https://towardsdatascience.com'
        news_page = await session.get(domain)
        news = await news_page.read()
        pages_all = BeautifulSoup(news, 'html.parser').find_all('article')
        links = [domain + el.find('a', {'aria-label': 'Post Preview Title'}).get('href').split('?')[0]
                 for el in pages_all]

        data = []
        for link in links:
            article = await session.get(link)
            article_content = await article.read()
            article_soup = BeautifulSoup(article_content, 'html.parser')

            rating = ''
            art = link
            date = datetime.datetime.strptime(str(datetime.datetime.now().year) + ' ' +
                                              article_soup.find('p', {'class': 'pw-published-date bn b bo bp co'}).text,
                                              '%Y %b %d')
            if link not in links_global and (datetime.date.today() - date.date()).days in (0, 1, 2):
                data.append((art, rating, date))
                links_global.append(link)

    return [await models.Article.from_page(el) for el in data]
