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
    length = len(titles)
    for index, title in enumerate(titles):
        print_progress_bar(index + 1, length, prefix='Progress:', suffix='Complete', bar_length=50)
        page = wikipedia.page(title)
        _save_page(page)
    print()


def _save_page(page):
    with open(f'pages/{page.title}', 'w', encoding='utf8') as f:
        f.write(page.content)


def _check_create_directory(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percents = f'{100 * (iteration / float(total)):.2f}'
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = f'{"█" * filled_length}{"-" * (bar_length - filled_length)}'
    sys.stdout.write(f'\r{prefix} |{bar}| {percents}% {suffix}'),


if __name__ == '__main__':
    main()
