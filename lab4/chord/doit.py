#!/usr/bin/env python3

"""
Chord Application
- defines a DummyChordClient implementation
- sets up a ring of chord_node instances
- Starts up a DummyChordClient
- nodes and client run in separate processes
- multiprocessing should work on unix and windows
"""

import logging
import multiprocessing as mp
import random
import sys
from time import sleep

from rich.console import Console

import chordnode as chord_node
import constChord
from context import lab_channel, lab_logging

lab_logging.setup(stream_level=logging.INFO)
CONSOLE = Console()


class DummyChordClient:
    """A dummy client template with the channel boilerplate"""

    def __init__(self, channel):
        self.channel = channel
        self.n_bits = channel.n_bits
        self.node_id = channel.join("client")

    def enter(self):
        self.channel.bind(self.node_id)

    def run(self):
        self.lookup_random_key()
        CONSOLE.print("Stopping all nodes")
        self.channel.send_to(  # a final multicast
            {i.decode() for i in list(self.channel.channel.smembers("node"))},
            constChord.STOP,
        )

    def lookup_random_key(self):
        """Lookup a key in the ring"""
        # Generate a random key
        random_key_str = str(random.randint(0, 2**self.n_bits - 1))
        random_key = int(random_key_str)

        # Send LOOKUP request to a random node
        nodes_available = self.channel.subgroup("node")

        target_node_id = int(random.choice(list(nodes_available)))
        target_node_id_str = str(target_node_id)

        msg = [constChord.LOOKUP_REQ, random_key_str]

        CONSOLE.print(
            f"\n\nSending LOOKUP request for key {random_key:04n} to node #{target_node_id:04n}\n",
            style="bold blue",
        )
        self.channel.send_to({target_node_id_str}, msg)

        # Wait for the response
        response = self.channel.receive_from({target_node_id_str})
        sleep(0.1)

        if response:
            # Successfully found the node
            CONSOLE.print("\n\n")
            CONSOLE.rule(f"LOOKUP successful. Key {random_key:04n} found via path:")
            recursive_print(response, random_key)

        else:
            # Lookup failed
            CONSOLE.print(f"LOOKUP failed. Node with key {random_key:04n} not found.")


def recursive_print(response, key):
    if len(response) == 1:
        CONSOLE.print(f"[{key:04n}]", style="bold red")
        CONSOLE.rule()
        CONSOLE.print("\n\n")
    else:
        CONSOLE.print(f"(#{int(response[0])}) ->", end=" ")
        recursive_print(response[1], key)


def create_and_run(num_bits, node_class, enter_bar, run_bar):
    """
    Create and run a node (server or client role)
    :param num_bits: address range of the channel
    :param node_class: class of node
    :param enter_bar: barrier syncing channel population
    :param run_bar: barrier syncing node creation
    """
    chan = lab_channel.Channel(n_bits=num_bits)
    node = node_class(chan)
    enter_bar.wait()  # wait for all nodes to join the channel
    node.enter()  # do what is needed to enter the ring
    run_bar.wait()  # wait for all nodes to finish entering
    node.run()  # start operating the node


if __name__ == "__main__":  # if script is started from command line
    m = 6  # Number of bits for linear names
    n = 8  # Number of nodes in the chord ring

    # Check for command line parameters m, n.
    if len(sys.argv) > 2:
        m = int(sys.argv[1])
        n = int(sys.argv[2])

    # Flush communication channel
    chan = lab_channel.Channel()
    chan.channel.flushall()

    # we need to spawn processes for support of windows
    mp.set_start_method("spawn")

    # create barriers to synchronize bootstrapping
    bar1 = mp.Barrier(n + 1)  # Wait for channel population to complete
    bar2 = mp.Barrier(n + 1)  # Wait for ring construction to complete

    # start n chord nodes in separate processes
    children = []
    for i in range(n):
        node_proc = mp.Process(
            target=create_and_run,
            name="ChordNode-" + str(i),
            args=(m, chord_node.ChordNode, bar1, bar2),
        )
        children.append(node_proc)
        node_proc.start()

    # spawn client proc and wait for it to finish
    client_proc = mp.Process(
        target=create_and_run,
        name="ChordClient",
        args=(m, DummyChordClient, bar1, bar2),
    )
    client_proc.start()
    client_proc.join()

    # wait for node processes to finish
    for node_proc in children:
        node_proc.join()
