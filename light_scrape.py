import time

from bs4 import BeautifulSoup
import requests
import json

URL = 'https://quotes.toscrape.com/page/'
quotes_date = []


def get_date():
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

    for page in range(9999):
        url = URL + str(page + 1)
        response = requests.get(url=url, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        posts = soup.find_all('div', class_='quote')
        page_nav = soup.find_all('li', class_='next')
        print("Скрапинг страницы №: %d" % (page + 1))

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

        if not len(page_nav):
            print(f"Максимальный номер страницы:{page+1}")
            break


def main():
    start_time = time.time()
    get_date()
    with open(__file__ + ".json", "w") as file:
        json.dump(quotes_date, file, indent=4, ensure_ascii=False)
    print(
        f"На выполнение парсинга затрачено:{time.time() - start_time} секунд")
    print(f"Количество записей в файле - {len(quotes_date)}")


if __name__ == "__main__":
    main()
