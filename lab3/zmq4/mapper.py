import logging
from threading import Thread, Event

import zmq
from zmq4.constants import LOCALHOST, PORT_SPLITTER
from zmq4.constants import PORT_REDUCER_START


class Mapper(Thread):
    def __init__(self, mapper_num: int, reducer_nums: list[int]):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__} #{mapper_num}")
        # Socket to send messages to

        self._stop_event = Event()
        self._context = zmq.Context()
        self._timeout_s = 100

        # Socket to receive messages on
        self._receiver = self._context.socket(zmq.PULL)
        splitter_url = f"tcp://{LOCALHOST}:{PORT_SPLITTER}"
        self.logger.info(f"connecting to [b]splitter[/b] {splitter_url}")
        self._receiver.connect(splitter_url)

        # Sockets to send messages to
        self._senders = list()
        for s in reducer_nums:
            reducer_url = f"tcp://{LOCALHOST}:{PORT_REDUCER_START + s}"
            self.logger.info(f"connecting [b]reducer #{s}[/b] {reducer_url}")
            sender = self._context.socket(zmq.PUSH)
            sender.connect(reducer_url)
            self._senders.append(sender)

        print()

    def run(self):
        # set timeout to 1 second
        self._receiver.setsockopt(zmq.RCVTIMEO, self._timeout_s * 1000)
        while not self._stop_event.is_set():
            # use try/except to catch timeout errors to be able to close the thread
            try:
                s_num, sentence = self._receiver.recv_pyobj()
            except zmq.error.Again:
                self.logger.info(f"timeout after {self._timeout_s}s, shutting down")
                self.stop_mapping()
                break

            self.logger.info(f"[b]receive[/b] sentence[{s_num}]")
            self.logger.debug(f'[b]receive[/b] "{sentence}"')
            self.send_words_to_reducer(sentence)

    def send_words_to_reducer(self, sentence: list):
        for word in sentence:
            # send word to reducer,
            # decide by the length of the word modulo the number of reducers
            reducer_num = len(word) % len(self._senders)
            self.logger.debug(f'[b]send[/b] "{word}" to [b]reducer#{reducer_num}[/b]')
            sender = self._senders[reducer_num]
            sender.send_pyobj(word)

    def start_mapping(self):
        if not self.is_alive():
            self._stop_event.clear()
            self.start()

    def stop_mapping(self):
        self._stop_event.set()
        try:
            self.join()
        except RuntimeError:
            pass
        self.logger.debug("stopped mapping")
