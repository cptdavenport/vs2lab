import logging
from threading import Thread, Event
from time import sleep


class Mapper(Thread):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._stop_event = Event()

    def run(self):
        while not self._stop_event.is_set():
            # Your main loop logic goes here
            self.logger.debug("Mapper running")
            sleep(1)

    def start_mapping(self):
        if not self.is_alive():
            self._stop_event.clear()
            self.start()

    def stop_mapping(self):
        self._stop_event.set()
        self.join()
