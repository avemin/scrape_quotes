import json
import time

import aiohttp
import asyncio
from bs4 import BeautifulSoup

URL = 'https://quotes.toscrape.com/page/'
MAIN_URL = 'https://quotes.toscrape.com'
HEADERS = {
    'accept': (
            'text/html, application/xhtml + xml, application/xml;'
            'q = 0.9,image/avif,image/webp,*/*;q = 0.8'
            ),
    'user-agent': (
            'Mozilla/5.0(X11;Ubuntu;Linux x86_64; rv: 96.0) '
            'Gecko/20100101 Firefox/96.0'
                ),
}

quotes_date = []
urls = []


async def get_page_data(session, page):
    """Функция парсер страниц с постами"""
    url = URL + str(page)
    print(f'Скрапинг страницы №: {page}')
    async with session.get(url=url, headers=HEADERS) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        posts = soup.find_all('div', class_='quote')

        for a_tag in soup.findAll('a'):
            href = a_tag.attrs.get('href')
            if '/author/' in href:
                urls.append(href)
            if href == '' or href is None:
                # href пустой тег
                continue

        for i in range(len(posts)):
            post = posts[i]
            tags = post.find_all('a', class_='tag')
            tag_content = [tags[i].text for i in range(len(tags))]

            quotes_date.append(
                {'post': {
                    'author': post.find('small', class_='author').text,
                    'text': post.find('span', class_='text').text,
                    'tags': tag_content
                    }
                 }
            )


async def get_page_author(session, author_url):
    """Функция парсер страниц авторов"""
    async with session.get(
        url=MAIN_URL+author_url, headers=HEADERS
    ) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        author = soup.find('h3', class_='author-title').text.rstrip()
        print(f'Скрапинг страницы автора: {author}')
        quotes_date.append(
            {author: {
                'born_date':
                    soup.find('span', class_='author-born-date').text,
                'born_location':
                    soup.find(
                        'span', class_='author-born-location'
                        ).text,
                'description':
                    soup.find(
                        'div', class_='author-description'
                        ).text.lstrip()
                    }}
        )


async def gather_data():
    """
    Формирует необходимый список задач
    и парсим топ 10 тегов
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url=MAIN_URL) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            top_tags = soup.find_all('span', class_='tag-item')
            quotes_date.append(
                {'ten_top_tags':
                    [top_tags[i].text.strip() for i in range(len(top_tags))]}
                )
        tasks = []
        tasks1 = []

        for page in range(1, 11):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)
        await asyncio.gather(*tasks)

        for author_url in set(urls):
            task1 = asyncio.create_task(get_page_author(session, author_url))
            tasks1.append(task1)

        await asyncio.gather(*tasks1)


def main():
    start_time = time.time()
    asyncio.run(gather_data())
    with open(__file__ + '.json', 'w') as file:
        json.dump(quotes_date, file, indent=4, ensure_ascii=False)
    print(
        f'На выполнение парсинга затрачено:{time.time() - start_time} секунд')
    print(f'Количество записей в файле - {len(quotes_date)}')


if __name__ == '__main__':
    main()
