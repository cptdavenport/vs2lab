from time import sleep

from rich.console import Console

from zmq4.log import setup_logging
from zmq4.mapper import Mapper

setup_logging()
console = Console()
mappers = list()

for i in range(3):
    m = Mapper(i)
    m.start_mapping()
    mappers.append(m)

sleep(0.3)
# console.input(f"Press enter to stop the {len(mappers)} mappers :stop_sign: ")
