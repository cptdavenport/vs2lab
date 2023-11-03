import logging
from time import sleep

from context import lab_channel, lab_logging
from lab2.rpc.server import Server

lab_logging.setup(stream_level=logging.INFO)
logger = logging.getLogger("vs2lab.lab2.rpc.runsrv")

chan = lab_channel.Channel()
chan.channel.flushall()
logger.debug("Flushed all redis keys.")

runtime = 600
srv = Server()
srv.run()
logger.info(f"run server for {runtime} seconds")
sleep(runtime)
srv.stop()
