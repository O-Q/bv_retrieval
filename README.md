# Boolean Retrieval with Positional Indexing
### wikipedia-reader.py
- Takes some arguments as wikipedia article titles and save their contents into `pages` folder.

- Takes `RANDOM $number` to save `$number` wikipedia article(s).
##### Examples:
` python .\wikipedia-reader.py "Project I.G.I." "Dota 2"`

` python .\wikipedia-reader.py RANDOM 5`
### booleanretrieval.py
Get files in `pages` directory and after cleaning and filtering, make `dict(dict(list))` model which is `word`, `documnet name` and `positional index`.
##### NOTE
`stopwords` and `punkt` from nltk is required.
```
import nltk
nltk.download(['punkt','stopwords'])
```
### query.py
- Takes query and search in modela created in `booleanretrieval.py`. (`retrieval_inverted_index.dict` and `doc_names.list`)
- Also takes keywords (`AND`, `OR`, `WITH`, `NEAR` and `NOT`).
##### Example:
Search: `valve dota`

Search: `valve AND dota`

Search: `valve OR NOT dota`

Search: `valve NEAR5 dota`

Search: `valve WITH dota`

Search: `valve NOT WITH dota`

Search: `valve NOT NEAR10 dota`

Search: `\exit`
