# Create positional inverted indexing model
import pickle
from sys import argv
import json
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from math import log10, sqrt
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

    def __init__(self, docs_count: int):
        self.docs_count = docs_count
        self.stop_words = set(stopwords.words('english'))
        self.model = defaultdict(
            lambda: defaultdict(lambda: {'tf_idf': float(), 'normalized_tf_idf': float(), 'positions': list()}))
        self.ps = PorterStemmer()

    def fit(self, docs: dict, model='vector') -> defaultdict:
        if model == 'vector':
            for doc_name in docs.keys():
                tokens = self._stem_filter_doc(docs[doc_name])
                for pos, token in enumerate(tokens):
                    self.model[token][doc_name]['positions'].append(pos)
            for token in self.model.keys():
                idf = self._idf(token)
                for doc_name in self.model[token].keys():
                    tf = self._tf(token, docs[doc_name])
                    tf_idf = tf * idf
                    self.model[token][doc_name]['tf_idf'] = tf_idf
            for token in self.model.keys():
                for doc_name in self.model[token].keys():
                    self.model[token][doc_name]['normalized_tf_idf'] = self._tf_idf_normalizer(
                        self.model[token][doc_name]['tf_idf'], docs[doc_name], doc_name)
        elif model == 'boolean':
            for doc_name in docs.keys():
                tokens = self._stem_filter_doc(docs[doc_name])
                for pos, token in enumerate(tokens):
                    self.model[token][doc_name]['positions'].append(pos)

        return self.model

    def _stem_filter_doc(self, doc: str) -> list:
        words_tokens = word_tokenize(doc)
        stemmed_filtered_tokens = [self.ps.stem(word) for word in words_tokens if word.lower() not in self.stop_words]
        return stemmed_filtered_tokens

    def _tf(self, token: str, doc: str) -> float:
        stemmed_filtered_tokens = self._stem_filter_doc(doc)
        return stemmed_filtered_tokens.count(token) / len(stemmed_filtered_tokens)

    def _idf(self, token: str) -> float:
        return log10(self.docs_count / len(self.model[token]))

    def _tf_idf_normalizer(self, tf_idf: float, doc: str, doc_name: str) -> float:
        stemmed_filtered_tokens = self._stem_filter_doc(doc)
        sum_square_tf_idf = float()
        for token in stemmed_filtered_tokens:
            sum_square_tf_idf += self.model[token][doc_name]['tf_idf'] ** 2
        return tf_idf / sqrt(sum_square_tf_idf)


def main():
    model = argv[2] if len(argv) > 1 and argv[2] == ('vector' or 'boolean') else None
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
