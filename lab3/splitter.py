from rich.console import Console

from zmq4.log import setup_logging
from zmq4.splitter import Splitter

setup_logging(log_level="ERROR")
s = Splitter(limit_sentences=100)
console = Console()
console.input("Press RETURN to start? :rocket: ")
s.send_sentences()
