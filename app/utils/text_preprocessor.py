import re

import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

_stemmer = PorterStemmer()


def preprocess_abstract(text: str | None) -> str:
    """Lowercase → remove special chars → tokenize → stem → join."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    tokens = word_tokenize(text)
    tokens = [_stemmer.stem(t) for t in tokens]
    return " ".join(tokens)
