import sys
import wikipedia


def main():
    _check_create_directory('pages')
    titles = sys.argv[1:]
    _get_wikipedia_page_content(titles)


def _get_wikipedia_page_content(titles: list) -> None:
    """
    :param titles: list of wikipedia page titles
    :return: None but create a directory 'pages' and save each content in separate file
    """
    for name in titles:
        with open(f'pages/{name}', 'w', encoding='utf8') as f:
            page = wikipedia.page(name)
            print(page.title)
            print(page.content)
            f.write(page.content)


def _check_create_directory(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    main()
