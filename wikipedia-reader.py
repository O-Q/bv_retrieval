import sys
import wikipedia


def main():
    _check_create_directory('pages')
    titles = sys.argv[1:]
    _get_wikipedia_page_content(titles)


def _get_wikipedia_page_content(titles: list) -> None:
    """
    :param titles: list of wikipedia page titles or RANDOM `number`
    :return: None but create a directory 'pages' and save each content in separate file
    """
    if 'RANDOM' in titles[0]:
        titles = wikipedia.random(int(titles[1]))

    for title in titles:
        page = wikipedia.page(title)
        _save_page(page)


def _save_page(page):
    print(page.title)
    print(page.content)
    with open(f'pages/{page.title}', 'w', encoding='utf8') as f:
        f.write(page.content)


def _check_create_directory(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    main()
