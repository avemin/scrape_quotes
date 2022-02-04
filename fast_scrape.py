import json
import time

import aiohttp
import asyncio
from bs4 import BeautifulSoup


URL = 'https://quotes.toscrape.com/page/'
quotes_date = []


async def get_page_data(session, page):
    """Функция парсер"""
    url = URL + str(page)
    headers = {
        "accept": (
                "text/html, application/xhtml + xml, application/xml;"
                "q = 0.9,image/avif,image/webp,*/*;q = 0.8"
                ),
        "user-agent": (
                "Mozilla/5.0(X11;Ubuntu;Linux x86_64; rv: 96.0) "
                "Gecko/20100101 Firefox/96.0"
                 ),
    }
    print(f"Скрапинг страницы №: {page}")
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        posts = soup.find_all('div', class_='quote')
        for i in range(len(posts)):
            post = posts[i]
            tags = post.find_all('a', class_='tag')
            tag_content = [tags[i].text for i in range(len(tags))]

            quotes_date.append(
                {"author": post.find('small', class_='author').text,
                 "text": post.find('span', class_='text').text,
                 "tags": tag_content
                 }
            )


async def gather_data():
    """
    Формирует необходимый список задач
    """
    async with aiohttp.ClientSession() as session:
        # так как код асинхронный
        # не смог реализовать автономный подсчет страниц
        # response = await session.get(url=URL)
        # soup = BeautifulSoup(await response.text(), "lxml")
        # page_nav = soup.find_all('li', class_='next')
        tasks = []
        for page in range(1, 11):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    start_time = time.time()
    asyncio.run(gather_data())
    with open(__file__ + ".json", "w") as file:
        json.dump(quotes_date, file, indent=4, ensure_ascii=False)
    print(
        f"На выполнение парсинга затрачено:{time.time() - start_time} секунд")
    print(f"Количество записей в файле - {len(quotes_date)}")


if __name__ == "__main__":
    main()
