from time import sleep

from rich.console import Console

from zmq4.log import setup_logging
from zmq4.reducer import Reducer

setup_logging(log_level="DEBUG")
console = Console()
reducers: list[Reducer] = list()

for i in range(2):
    r = Reducer(i)
    reducers.append(r)

running = True
with console.status(f"[bold] {len(reducers)} {reducers[0].state} reducers") as status:
    for r in reducers:
        r.start_reducing()
    while running:
        for r in reducers:
            running = running & r.is_alive()
        status.update(f"[bold] {len(reducers)} {reducers[0].state} reducers")
        sleep(0.5)

for i, r in enumerate(reducers):
    wordlist = r.get_sorted_wordlist()
    console.log(f"reducer #{i} top {10} words:\n{wordlist}")
