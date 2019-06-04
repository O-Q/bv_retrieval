# Create positional inverted indexing model
import json
from collections import defaultdict
from math import log10, sqrt
from os import listdir
from os.path import isfile, join
from sys import argv

from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

DOC_PATH = 'pages'


class DocObject:

    def __init__(self):
        self.tf_idf = float()
        self.normalized_tf_idf = float()
        self.positions = list()

    @staticmethod
    def serializable():
        return DocObject().__dict__


class Retrieval:
    keywords = ['AND', 'OR', 'NOT', 'WITH', 'NEAR']

    def __init__(self, docs_count: int):
        self.docs_count = docs_count
        self.stop_words = set(stopwords.words('english'))
        self.model = defaultdict(
            lambda: defaultdict(
                lambda: {'tf_idf': float(), 'normalized_tf_idf': float(), 'positions': list(), 'count': int()}))
        self.ps = PorterStemmer()

    def fit(self, docs: dict, model='vector') -> defaultdict:
        if model == 'vector':
            name_stemmed_tokens_docs = dict()
            print('Generating Vector Space Model...')
            for doc_name in docs.keys():
                tokens = self._stem_filter_doc(docs[doc_name])
                name_stemmed_tokens_docs[doc_name] = tokens
                for pos, token in enumerate(tokens):
                    self.model[token][doc_name]['positions'].append(pos)
                    self.model[token][doc_name]['count'] += 1
            print('Stemming and Positions Docs DONE!')
            for token in self.model.keys():
                idf = self._idf(token)
                for doc_name in self.model[token].keys():
                    tf = self._tf(token, name_stemmed_tokens_docs[doc_name], self.model[token][doc_name].get('count'))
                    tf_idf = tf * idf
                    self.model[token][doc_name]['tf_idf'] = tf_idf
            print('Calculating TF-IDF DONE!')
            for token in self.model.keys():
                for doc_name in self.model[token].keys():
                    self.model[token][doc_name]['normalized_tf_idf'] = self._tf_idf_normalizer(
                        self.model[token][doc_name]['tf_idf'], name_stemmed_tokens_docs[doc_name], doc_name)
            print('TF-IDF Normalization DONE!')
        elif model == 'boolean':
            print('Generating Boolean Model...')
            for doc_name in docs.keys():
                tokens = self._stem_filter_doc(docs[doc_name])
                for pos, token in enumerate(tokens):
                    self.model[token][doc_name]['positions'].append(pos)
            print('Stemming and Positions Docs DONE!')
        print('All Done!')
        return self.model

    def _stem_filter_doc(self, doc: str) -> list:
        words_tokens = word_tokenize(doc)
        stemmed_filtered_tokens = [self.ps.stem(word) for word in words_tokens if word.lower() not in self.stop_words]
        return stemmed_filtered_tokens

    def _tf(self, token: str, stemmed_filtered_tokens: list, most_common_word_frequency: int) -> float:
        return stemmed_filtered_tokens.count(token) / most_common_word_frequency

    def _idf(self, token: str) -> float:
        return log10(self.docs_count / len(self.model[token]))

    def _tf_idf_normalizer(self, tf_idf: float, stemmed_filtered_tokens: list, doc_name: str) -> float:
        sum_square_tf_idf = float()
        for token in stemmed_filtered_tokens:
            sum_square_tf_idf += self.model[token][doc_name]['tf_idf'] ** 2
        return tf_idf / sqrt(sum_square_tf_idf)


def main():
    model = argv[1] if len(argv) > 1 and argv[1] == 'vector' or 'boolean' else None
    doc_names = [f for f in listdir(DOC_PATH) if isfile(join(DOC_PATH, f))]
    retrieval_model = Retrieval(len(doc_names))
    docs = dict()
    for doc_name in doc_names:
        doc = str()
        with open(f'{DOC_PATH}/{doc_name}', encoding='utf8') as f:
            for line in f.readlines():
                line = _remove_whitespaces(line)
                if line:
                    doc += line
        docs[doc_name] = doc
    retrieval_model.fit(docs, model) if model else retrieval_model.fit(docs)
    json.dump(doc_names, open('doc_names.list', 'w'))
    json.dump(retrieval_model.model, open('retrieval_inverted_index.dict', 'w'))


def _remove_whitespaces(line: str) -> str:
    line = line.replace('\n', '')
    line = line.replace('=', '')
    line = line.lstrip()
    return line


if __name__ == '__main__':
    main()
