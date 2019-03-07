# Create positional inverted indexing model
import json
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

DOC_PATH = 'pages'


class Retrieval:

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.model = defaultdict(lambda: defaultdict(list))
        self.ps = PorterStemmer()

    def fit(self, docs: dict) -> defaultdict:
        for doc_name in docs.keys():
            tokens = self._stem_filter_doc(docs[doc_name])
            for pos, token in enumerate(tokens):
                self.model[token][doc_name].append(pos)
        return self.model

    def _stem_filter_doc(self, doc: str) -> list:
        words_tokens = word_tokenize(doc)
        stemmed_filtered_tokens = [self.ps.stem(word) for word in words_tokens if word.lower() not in self.stop_words]
        return stemmed_filtered_tokens


def main():
    retrieval_model = Retrieval()
    doc_names = [f for f in listdir(DOC_PATH) if isfile(join(DOC_PATH, f))]
    docs = dict()
    for doc_name in doc_names:
        doc = str()
        with open(f'{DOC_PATH}/{doc_name}', encoding='utf8') as f:
            for line in f.readlines():
                line = _remove_whitespaces(line)
                if line:
                    doc += line
        docs[doc_name] = doc
    retrieval_model.fit(docs)
    json.dump(retrieval_model.model, open('retrieval_inverted_index.model', 'w'))


def _remove_whitespaces(line):
    line = line.replace('\n', '')
    line = line.replace('=', '')
    line = line.lstrip()
    return line


if __name__ == '__main__':
    main()
