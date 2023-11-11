from time import sleep

from rich.console import Console

from zmq4.log import setup_logging
from zmq4.reducer import Reducer

setup_logging()
console = Console()
reducers = list()

for i in range(2):
    r = Reducer(i)
    r.start_reducing()
    reducers.append(r)

sleep(1)
# console.input(f"Press enter to stop the {len(mappers)} mappers :stop_sign: ")
