import sys
import wikipedia


def main():
    _check_create_directory('pages')
    args = sys.argv[1:]
    for name in args:
        with open(f'pages/{name}.txt', 'w', encoding='utf8') as f:
            content = wikipedia.page(name).content
            print(content)
            f.write(content)


def _check_create_directory(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)


if __name__ == '__main__':
    main()
