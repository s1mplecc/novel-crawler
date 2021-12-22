import os
import re
import time
from concurrent.futures import ProcessPoolExecutor
from urllib import request

from bs4 import BeautifulSoup

NOVEL_NETLOC = 'https://www.biquge.com.cn'


def _fetch_html(url, decode='UTF-8'):
    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with request.urlopen(req) as res:
        return res.read().decode(decode)


def _html_parser(url, decode):
    html = _fetch_html(url, decode)
    return BeautifulSoup(html, 'html.parser')


def extract_title(novel_id, prefix=NOVEL_NETLOC, decode='UTF-8'):
    main_page = _html_parser(f'{prefix}/book/{novel_id}/', decode)
    return main_page.h1.string


def extract_chapters(novel_id, prefix=NOVEL_NETLOC, decode='UTF-8'):
    main_page = _html_parser(f'{prefix}/book/{novel_id}/', decode)
    chapters = main_page.find_all('a', href=re.compile(rf'/{novel_id}/'))
    return [(chapter.get_text(), prefix + chapter['href']) for chapter in chapters if chapter.parent.name == 'dd']


def _extract_chapter_content(chapter, decode='UTF-8'):
    print('parsing', chapter[0], chapter[1])
    chapter_page = _html_parser(chapter[1], decode)
    content = chapter_page.find('div', id='content').get_text()
    return chapter[0] + '\n\n' + content.replace('\xa0\xa0\xa0\xa0', '\n\b\b') + '\n\n'


def download(chapters, parallelism=4):
    with ProcessPoolExecutor(parallelism) as executor:
        contents = executor.map(_extract_chapter_content, chapters)
    return contents


def write_to_file(title, contents, encoding='UTF-8'):
    os.makedirs('downloads', exist_ok=True)
    with open(f'./downloads/{title}.txt', 'wt+', encoding=encoding) as f:
        f.writelines(contents)


def novel_crawler(novel_id):
    title = extract_title(novel_id)
    chapters = extract_chapters(novel_id)
    contents = download(chapters, parallelism=64)
    write_to_file(title, contents)


if __name__ == '__main__':
    start = time.time()
    novel_crawler('25644')
    print(f'Time spent: {time.time() - start}s')
