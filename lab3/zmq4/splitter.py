import logging

import nltk
from nltk.corpus import gutenberg


class Splitter:
    def __init__(self, text="bible-kjv.txt"):
        # use nltk to get words and sentences https://www.nltk.org/book/ch02.html
        # Download the Gutenberg corpus (if not already downloaded)
        nltk.download("gutenberg")
        # Download the punkt tokenizer (if not already downloaded)
        nltk.download("punkt")

        self.logger = logging.getLogger(__name__)

        # Get the text of a specific book from the Gutenberg corpus
        # i don't use this, but it's here for reference to the raw text
        # and the use of tokenization
        # self._text = gutenberg.raw(text)
        # self._sentences = sent_tokenize(self._text)
        self._sentences = gutenberg.sents(text)

    def get_sentences(self):
        for i, sentence in enumerate(self._sentences, start=1):
            self.logger.debug(f"Sentence {i}: {sentence}")
            for j, word in enumerate(sentence, start=1):
                if word.isalpha():
                    self.logger.debug(f"Word {j}: {word}")
            if i > 10:
                break
