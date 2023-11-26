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

running = True
with console.status(f"[bold] {len(mappers)} running mappers") as status:
    for m in mappers:
        m.start_mapping()
    while running:
        for m in mappers:
            running = running & m.is_alive()
        status.update(f"[bold] {len(mappers)} {mappers[0].state} mappers")
        sleep(0.5)
sleep(0.3)
