import logging
import time
from threading import Thread, Event

import zmq
from rich.console import Console
from zmq4.constants import PORT_REDUCER_START, STATE_WAITING, STATE_RUNNING, LOCALHOST


class Reducer(Thread):
    def __init__(self, reducer_num: int):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__} #{reducer_num}")
        # Socket to send messages to

        self._stop_event = Event()
        self._context = zmq.Context()
        self._timeout_s = 10

        # Socket to receive messages on
        self._receiver = self._context.socket(zmq.PULL)
        receiver_url = f"tcp://{LOCALHOST}:{PORT_REDUCER_START + reducer_num}"
        self.logger.info(f"start reducer [b]sink[/b] {receiver_url}")
        self._receiver.bind(receiver_url)
        self._words = dict()
        self._last_update = time.time() - 10

    def run(self):
        # set timeout to 1 second
        self._receiver.setsockopt(zmq.RCVTIMEO, self._timeout_s * 1000)
        while not self._stop_event.is_set():
            # use try/except to catch timeout errors to be able to close the thread
            try:
                word = self._receiver.recv_pyobj()
            except zmq.error.Again:
                self.logger.info(f"timeout after {self._timeout_s}s, shutting down")
                self.stop_reducing()
                break

            self.reduce_word(word)

    def reduce_word(self, word: str):
        if word in self._words:
            self._words[word] += 1
        else:
            self._words[word] = 1
        self.logger.debug(f'[b]reduce[/b] "{word}"[{self._words[word]}]')
        self._last_update = time.time()

    def start_reducing(self):
        if not self.is_alive():
            self._stop_event.clear()
            self.start()

    def stop_reducing(self):
        self._stop_event.set()
        try:
            self.join()
        except RuntimeError:
            pass
        self.logger.debug("stopped reducer")
        # log words sorted by value
        console: Console = self.logger.parent.handlers[0].console

    def get_sorted_wordlist(self):
        return dict(sorted(self._words.items(), key=lambda item: item[1], reverse=True))

    @property
    def state(self):
        if self._last_update + 1 < time.time():
            state = STATE_WAITING
        else:
            state = STATE_RUNNING
        return state
