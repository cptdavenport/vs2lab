import logging
from time import sleep

import rpc
from context import lab_channel, lab_logging

lab_logging.setup(stream_level=logging.INFO)
logger = logging.getLogger("vs2lab.lab2.rpc.runsrv")

chan = lab_channel.Channel()
chan.channel.flushall()
logger.debug("Flushed all redis keys.")

srv = rpc.Server()
srv.run()
logger.info("run server for 10 seconds")
sleep(5)
srv.stop()
logger.info("stop server for 10 seconds")
sleep(5)
logger.info("restart server for 10 seconds")
srv.run()
sleep(5)
srv.stop()
