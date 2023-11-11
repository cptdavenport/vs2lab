from rich.console import Console

from zmq4.log import setup_logging
from zmq4.splitter import Splitter

setup_logging()
s = Splitter()
console = Console()
console.input("Press  ready to start? :rocket: ")
s.send_sentences()
