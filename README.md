# Boolean Retrieval with Positional Indexing
### wikipedia-reader.py
- Take some arguments as wikipedia article titles and save their contents into `pages` folder.

- Take `RANDOM $number` to save `$number` wikipedia article(s).
##### Examples:
` python .\wikipedia-reader.py "Project I.G.I." "Dota 2"`

` python .\wikipedia-reader.py RANDOM 5`
### booleanretrieval.py
Get files in `pages` directory and after cleaning and filtering, make `dict(dict(list))` model which is `word`, `documnet name` and `positional index`.
#####NOTE
`stopwords` and `punkt` from nltk is required.
```
import nltk
nltk.download(['punkt','stopwords'])
```
### query.py
`Will be updated soon...`