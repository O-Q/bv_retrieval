import json
import os
import time
from collections import defaultdict, Counter
from math import log10
from sys import argv

from nltk import PorterStemmer
from nltk.corpus import stopwords


class Query:
    keywords = ['AND', 'OR', 'NOT', 'WITH', 'NEAR']

    def __init__(self, model_address='retrieval_inverted_index.dict', doc_names_address='doc_names.list'):
        # TODO: defaultdict is not properly working
        self.model = defaultdict(
            lambda: defaultdict(lambda: {'tf_idf': float(), 'normalized_tf_idf': float(), 'positions': list()}),
            json.load(open(model_address)))
        self.doc_names: set = set(json.load(open(doc_names_address)))
        self.doc_count = len(self.doc_names)

    def query(self, text: str, vector_space=True):
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
                        # WITH NOT(NOT WITH)
                        first_word = terms[index - 3]
                        second_word = term
                        self._not_with_operation(first_word, second_word, filtered_docs)
                    else:
                        # NEAR NOT(NOT NEAR)
                        if current_operation[4:].isdigit():
                            max_dist = int(current_operation[4:])
                            first_word = terms[index - 3]
                            second_word = term
                            self._not_near_operation(first_word, second_word, max_dist, filtered_docs)
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
                            raise Exception('NOT Operation Error')

        # Finally or
        or_filter_list.append(filtered_docs)
        result = set()
        for filtered_docs in or_filter_list:
            result = result.union(filtered_docs)
        # vector ranking
        if vector_space and result:
            doc_tf_idf_multiply = defaultdict(float)
            max_frequency = Counter([token for token in text.split() if
                                     token not in self.keywords and token.find('NEAR') != 0]).most_common(1)[0][1]
            for token in text.split():
                if token == 'NOT':
                    raise Exception('NOT Operation Error')
                if token not in self.keywords and token.find('NEAR') != 0:
                    token_in_query_idf = log10(self.doc_count / len(self.model[token]))
                    token_in_query_tf = text.count(token) / max_frequency
                    token_in_query_tf_idf = token_in_query_tf * token_in_query_idf
                    for doc_name in result:
                        if self.model[token].get(doc_name):
                            token_in_doc_tf_idf = self.model[token][doc_name]['normalized_tf_idf']
                            doc_tf_idf_multiply[doc_name] += token_in_query_tf_idf * token_in_doc_tf_idf
            sorted_result = sorted(doc_tf_idf_multiply.items(), key=lambda kv: kv[1], reverse=True)
            return sorted_result
        else:
            return result

    def _not_operation(self, not_word, filtered_docs):
        if not_word not in stop_words:
            doc_to_remove = set()
            docs_positions: dict = self.model.get(not_word)
            if docs_positions:
                for doc in filtered_docs:
                    x = docs_positions.get(doc)
                    if x and x.get('positions'):
                        doc_to_remove.add(doc)
                filtered_docs.difference_update(doc_to_remove)

    def _and_operation(self, word, filtered_docs):
        if word not in stop_words:
            doc_to_remove = set()
            docs_positions: dict = self.model.get(word)
            if docs_positions:
                for doc in filtered_docs:
                    x = docs_positions.get(doc)
                    if not x or not x.get('positions'):
                        doc_to_remove.add(doc)
                filtered_docs.difference_update(doc_to_remove)
            else:
                filtered_docs.clear()

    def _with_operation(self, first_word, second_word, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            expected_positions_second_word = {position + 1 for position in self.model[first_word][doc]['positions']}
            positions_second_word = set(self.model[second_word][doc]['positions'])
            if not expected_positions_second_word.intersection(positions_second_word):
                doc_to_remove.add(doc)
        filtered_docs.difference_update(doc_to_remove)

    def _near_operation(self, first_word, second_word, max_dist, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            invalid_doc = True
            positions_second_word = set(self.model[second_word][doc]['positions'])
            for dist in range(-max_dist, max_dist):
                expected_positions_second_word = {position + dist for position in
                                                  self.model[first_word][doc]['positions'] if dist != 0}
                if expected_positions_second_word.intersection(positions_second_word):
                    invalid_doc = False
                    break
            if invalid_doc:
                doc_to_remove.add(doc)
        filtered_docs.difference_update(doc_to_remove)

    def _not_with_operation(self, first_word, second_word, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            expected_positions_second_word = {position + 1 for position in self.model[first_word][doc]['positions']}
            positions_second_word = set(self.model[second_word][doc]['positions'])
            if expected_positions_second_word.intersection(positions_second_word):
                doc_to_remove.add(doc)
        filtered_docs.difference_update(doc_to_remove)

    def _not_near_operation(self, first_word, second_word, max_dist, filtered_docs):
        # STOPWORDS ?
        doc_to_remove = set()
        for doc in filtered_docs:
            invalid_doc = False
            positions_second_word = set(self.model[second_word][doc]['positions'])
            for dist in range(-max_dist, max_dist):
                expected_positions_second_word = {position + dist for position in
                                                  self.model[first_word][doc]['positions'] if dist != 0}
                if expected_positions_second_word.intersection(positions_second_word):
                    invalid_doc = True
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
    is_vector = len(argv) < 2 or argv[1] == 'vector'
    while True:
        text = input('Search: ')
        if text == r'\exit':
            exit()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                start = time.time()
                clean_text = text_cleaner(text)
                print(f'text after cleaning: {clean_text}')
                print('searching...')
                result_docs = q.query(clean_text, vector_space=is_vector)
                end = time.time()
                print(f'{len(result_docs)} results ({(end - start):.2f} seconds)')
                for result in result_docs:
                    print(f'- {result}')
            except Exception as e:
                print(str(e))


if __name__ == '__main__':
    main()
