from time import sleep

from rich.console import Console

from zmq4.log import setup_logging
from zmq4.mapper import Mapper

setup_logging(log_level="INFO")
console = Console()
mappers = list()
reducer_numbers = [0, 1]

for i in range(3):
    m = Mapper(i, reducer_nums=reducer_numbers)
    m.start_mapping()
    mappers.append(m)

sleep(0.3)
# console.input(f"Press enter to stop the {len(mappers)} mappers :stop_sign: ")
