import json
import time

import aiohttp
import asyncio
from bs4 import BeautifulSoup


URL = 'https://quotes.toscrape.com/page/'
MAIN_URL = 'https://quotes.toscrape.com'

quotes_date = []
urls = []
authors = []


async def get_page_data(session, page):
    """Функция парсер"""
    url = URL + str(page)
    headers = {
        'accept': (
                'text/html, application/xhtml + xml, application/xml;'
                'q = 0.9,image/avif,image/webp,*/*;q = 0.8'
                ),
        'user-agent': (
                'Mozilla/5.0(X11;Ubuntu;Linux x86_64; rv: 96.0) '
                'Gecko/20100101 Firefox/96.0'
                 ),
    }
    print(f'Скрапинг страницы №: {page}')
    async with session.get(url=url, headers=headers) as response:
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
    #данный участок кода проходит 10 итераций, это снижает производительность
    for author_url in set(urls):
        async with session.get(
            url=MAIN_URL+author_url, headers=headers
        ) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            author = soup.find('h3', class_='author-title').text.rstrip()

            if author not in authors:
                authors.append(author)
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
        async with session.get(url=URL+str(1)) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, 'lxml')
            top_tags = soup.find_all('span', class_='tag-item')
            quotes_date.append(
                {'ten_top_tags':
                    [top_tags[i].text.strip() for i in range(len(top_tags))]}
                )
        tasks = []
        for page in range(1, 11):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


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
