import json
import os
import time

from nltk.corpus import stopwords
from nltk import PorterStemmer


class Query:
    keywords = ['AND', 'OR', 'NOT', 'WITH', 'NEAR']

    def __init__(self, model_address='retrieval_inverted_index.dict', doc_names_address='doc_names.list'):
        self.model: dict = json.load(open(model_address))
        self.doc_names: set = set(json.load(open(doc_names_address)))

    def query(self, text: str) -> set:
        or_filter_list = list()
        filtered_docs: set = self.doc_names.copy()
        terms = text.split()
        not_operation = False
        current_operation = str()
        for index, term in enumerate(terms):  # walk in terms
            if term == 'OR':
                or_filter_list.append(filtered_docs)
                filtered_docs: set = self.doc_names.copy()
                current_operation = ''
            elif term == 'NOT':
                not_operation = True
            elif term == 'AND' or term == 'WITH' or term.find('NEAR') == 0:
                current_operation = term
            else:  # term is word
                if not_operation:
                    not_operation = False
                    if current_operation != 'WITH' or current_operation.find('NEAR') == 0:
                        # current operation is empty(empty or OR) or AND
                        self._not_operation(term, filtered_docs)
                    elif current_operation == 'WITH':
                        # with not
                        print()
                    else:
                        # NEAR not
                        print()
                else:  # without not
                    # intersect with filtered_docs (AND-like operation)
                    self._and_operation(term, filtered_docs)
                    if current_operation == 'WITH':
                        first_word = terms[index - 2]
                        second_word = term
                        self._with_operation(first_word, second_word, filtered_docs)
                    elif current_operation.find('NEAR') == 0:
                        if current_operation[4:].isdigit():
                            max_dist = int(current_operation[4:])
                            first_word = terms[index - 2]
                            second_word = term
                            self._near_operation(first_word, second_word, max_dist, filtered_docs)
                        else:
                            return {'NEAR OPERATION ERROR!!!'}

        # Finally or
        or_filter_list.append(filtered_docs)
        result = set()
        for filtered_docs in or_filter_list:
            result = result.union(filtered_docs)
        return result

    def _not_operation(self, not_word, filtered_docs):
        if not_word not in stop_words:
            doc_to_remove = set()
            docs_positions: dict = self.model.get(not_word)
            if docs_positions:
                for doc in filtered_docs:
                    if docs_positions.get(doc):
                        doc_to_remove.add(doc)
                filtered_docs.difference_update(doc_to_remove)

    def _and_operation(self, word, filtered_docs):
        if word not in stop_words:
            doc_to_remove = set()
            docs_positions: dict = self.model.get(word)
            if docs_positions:
                for doc in filtered_docs:
                    if not docs_positions.get(doc):
                        doc_to_remove.add(doc)
                filtered_docs.difference_update(doc_to_remove)
            else:
                filtered_docs.clear()

    def _with_operation(self, first_word, second_word, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            expected_positions_second_word = {position + 1 for position in self.model[first_word][doc]}
            positions_second_word = set(self.model[second_word][doc])
            if not expected_positions_second_word.intersection(positions_second_word):
                filtered_docs.add(doc)
        filtered_docs.difference_update(doc_to_remove)

    def _near_operation(self, first_word, second_word, max_dist, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            invalid_doc = True
            positions_second_word = set(self.model[second_word][doc])
            for dist in range(-max_dist, max_dist):
                expected_positions_second_word = {position + dist for position in
                                                  self.model[first_word][doc] if dist != 0}
                if expected_positions_second_word.intersection(positions_second_word):
                    invalid_doc = False
                    break
            if invalid_doc:
                doc_to_remove.add(doc)
        filtered_docs.difference_update(doc_to_remove)


stop_words = set(stopwords.words('english'))
ps = PorterStemmer()


def text_cleaner(text: str):
    text = text.replace('\n', '').replace('=', '').lstrip()
    clean_words = list()
    for word in text.split():
        if word in ['AND', 'OR', 'NOT', 'WITH'] or word.find('NEAR') == 0:
            clean_words.append(word)
        else:
            clean_words.append(ps.stem(word))
    return ' '.join(clean_words)


def main():
    q = Query()
    while True:
        text = input('Search: ')
        if text == r'\exit':
            exit()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            start = time.time()
            clean_text = text_cleaner(text)
            print(f'text after cleaning: {clean_text}')
            print('searching...')
            result_docs: set = q.query(clean_text)
            end = time.time()
            print(f'{len(result_docs)} results ({(end - start):.2f} seconds)')
            for result in result_docs:
                print(f'- {result}')


if __name__ == '__main__':
    main()
