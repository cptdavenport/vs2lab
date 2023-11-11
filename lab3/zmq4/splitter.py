import logging

import nltk
import zmq
from nltk.corpus import gutenberg
from rich.console import Console
from zmq4.constants import LOCALHOST, PORT_SPLITTER


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
        self._sentences = self._sentences[:10]  # limit to 10 sentences for testing

        self._context = zmq.Context()
        self._sender = self._context.socket(zmq.PUSH)  # create a push socket
        self._sender.bind(
            f"tcp://{LOCALHOST}:{PORT_SPLITTER}"
        )  # bind socket to address
        self.logger.info(
            f"start splitter [b]source[/b] tcp://{LOCALHOST}:{PORT_SPLITTER}"
        )

    def send_sentences(self):
        console: Console = self.logger.parent.handlers[0].console
        with console.status("[bold green]Splitting sentences...") as status:
            for i, sentence in enumerate(self._sentences):
                # remove punctuation
                sentence = [word for word in sentence if word.isalpha()]

                self.logger.info(f"[b]send[/b] sentence[{i}]")
                self.logger.debug(f"\"{' '.join(sentence)}\"")
                self._sender.send_pyobj((i, sentence))

    def get_sentences(self):
        for i, sentence in enumerate(self._sentences, start=1):
            self.logger.debug(f"[b]send[/b]sentence[{i}]: {sentence}")
            for j, word in enumerate(sentence, start=1):
                if word.isalpha():
                    self.logger.debug(f"Word {j}: {word}")
