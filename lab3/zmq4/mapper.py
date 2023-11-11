import logging
from threading import Thread, Event

import zmq
from zmq4.constants import LOCALHOST, PORT_SPLITTER


class Mapper(Thread):
    def __init__(self, mapper_num: int):
        super().__init__()
        self._mapper_num = mapper_num
        self.logger = logging.getLogger(f"{__name__} #{mapper_num}")
        self._stop_event = Event()
        self._context = zmq.Context()
        self._timeout_s = 3

        # Socket to receive messages on
        self._receiver = self._context.socket(zmq.PULL)

    def run(self):
        splitter_url = f"tcp://{LOCALHOST}:{PORT_SPLITTER}"
        self.logger.debug(f"connecting to splitter {splitter_url}")
        self._receiver.connect(splitter_url)

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
            self.send_words_to_reducer(sentence)

    def send_words_to_reducer(self, sentence: list):
        self.logger.debug(f"[b]send[/b] {sentence}")
        for word in sentence:
            pass

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
