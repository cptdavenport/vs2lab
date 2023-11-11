from zmq4.log import setup_logging
from zmq4.splitter import Splitter

setup_logging()
s = Splitter()
s.get_sentences()