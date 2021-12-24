import os
from urllib import request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
from tabulate import multiline_formats, tabulate

_BASE_URL_ = 'http://libgen.is/'

# config
DOWNLOAD_PATH = "./download"
N_AUTHORS = 1
MAX_CHARS_AUTHORS = 25


def get_results(term):
    parms = urlencode({'req': term})
    url = _BASE_URL_ + 'index.php?%s' % parms
    raw = request.urlopen(url)
    soup = BeautifulSoup(raw, 'lxml')
    books_found = re.search(r'(\d+) files found', str(soup))
    books = soup.find_all('tr')
    books = books[3:-1]

    return books


def format_books(books):
    fmt_books = []
    books_mirrors = []

    for rawbook in books:
        book_attributes = rawbook.find_all('td')
        authors = [a.text for a in book_attributes[1].find_all('a')]
        author = ', '.join(authors[:N_AUTHORS])
        author = author[:MAX_CHARS_AUTHORS]

        title = book_attributes[2].find(title=True).text
        publisher = book_attributes[3].text
        year = book_attributes[4].text
        no_pages = book_attributes[5].text
        language = book_attributes[6].text
        size = book_attributes[7].text
        ext = book_attributes[8].text

        mirror_list = {}  # Dictionary of all the four mirrors
        for i in range(10, 15):
            mirror = i - 10
            if book_attributes[i].a:
                mirror_list[mirror] = book_attributes[i].a.attrs['href']
        book = (author, title, publisher, year, no_pages, language, size, ext)
        book_mirrors = {'title': title, 'mirrors': mirror_list}
        books_mirrors.append(book_mirrors)
        fmt_books.append(book)

    return (fmt_books, books_mirrors)


def select_book(books, mirrors):
    heading = ['#', 'Author', 'Title', 'Publisher', 'Year', 'Language', 'Size', 'Ext']
    print(tabulate(books[-25:25], heading, showindex='always'))

    while True:
        id = input("Enter the Book Id (#) to download or 'q' to Quit: ")

        if id.isnumeric():
            choice = int(id)
            title = '{}'.format(mirrors[choice]['title'])
            ext = books[choice][-1]
            download_book(mirrors[choice]['mirrors'][0], title, ext)

        elif id == 'q' or id == 'Q':
            return False


def download_book(link, file_name, ext):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    accept_charset = 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
    accept_lang = 'en-US,en;q=0.9'
    connection = 'keep-alive'

    headers = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Charset': accept_charset,
        'Accept-Language': accept_lang,
        'Connection': connection,
    }

    req = request.Request(link, headers=headers)
    source = request.urlopen(req)
    soup = BeautifulSoup(source, 'lxml')
    a = soup.find('a').get('href')
    download_url = 'http://libgen.lc/' + a

    # saving the book
    if os.path.exists(DOWNLOAD_PATH) and os.path.isdir(DOWNLOAD_PATH):
        bad_chars = '\/:*?"<>|'
        for char in bad_chars:
            file_name = file_name.replace(char, " ")

        path = '{}/{}'.format(DOWNLOAD_PATH, file_name)
        path += '.' + ext
        print('Downloading....!')
        request.urlretrieve(download_url, path)
        print('Book downloaded to {}'.format(os.path.abspath(path)))


def main():
    query = input("Enter the Book Name: ")
    raw_data = get_results(query)
    fmt_book, mirrors = format_books(raw_data)
    select_book(fmt_book, mirrors)


if __name__ == "__main__":
    main()
