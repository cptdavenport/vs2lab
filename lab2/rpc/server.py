import logging
import random
import threading
from time import sleep

import constRPC
from context import lab_channel
from lab2.rpc.dblist import DBList


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join(constRPC.SERVER_CHANNEL)
        self.logger = logging.getLogger("vs2lab.lab2.channel.Server")
        self.timeout = 3
        self._thread = None
        self._runnable = False
        self._worker_thread_pool = list()

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    def _run(self):
        """Server thread main loop."""
        # connect to RPC channel
        self.chan.bind(self.server)
        self.logger.info(
            f'Server bound to channel "{constRPC.SERVER_CHANNEL}" with pid "{self.server}".'
        )
        # run server loop
        while self._runnable:
            msg_req = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msg_req is not None:
                client = msg_req[0]  # see who is the caller
                self.logger.info(f"received message from client{client}")
                msg_rpc = msg_req[1]  # fetch call & parameters
                if constRPC.APPEND == msg_rpc[0]:  # check what is being requested
                    self.chan.send_to({client}, constRPC.ACK)  # ACK msg
                    self.logger.info(f"ACK sent to client{client}")

                    # create new thread processing data and sending result
                    self._worker_thread_pool.append(
                        threading.Thread(
                            target=self.process_and_send_result,
                            kwargs={"clients": {client}, "msg_rpc": msg_rpc},
                            daemon=True,
                        )
                    )
                    # start thread created
                    self._worker_thread_pool[-1].start()
                    self.logger.info(
                        f"started worker-thread[{self._worker_thread_pool[-1].native_id}]"
                    )
                else:
                    pass  # unsupported request, simply ignore
        self.logger.info(
            f'server left channel "{constRPC.SERVER_CHANNEL}" with pid "{self.server}".'
        )

    def process_and_send_result(self, clients: dict, msg_rpc: tuple):
        """
        Async Process the request and send the result to the client.
        Args:
            clients (dict): dict of clients to send the result to
            msg_rpc: the message received from the client
        """
        current_thread_id = threading.get_ident()
        duration_s = random.randint(
            constRPC.SERVER_WORK_DURATION[0], constRPC.SERVER_WORK_DURATION[1]
        )
        self.logger.info(
            f"async calculating result for {duration_s}s "
            f"in thread with ID: {current_thread_id}"
        )
        result = self.append(msg_rpc[1], msg_rpc[2])  # do local call
        # fake some work
        sleep(duration_s)
        self.chan.send_to(clients, result)

        self.logger.info(
            f"result sent to client in thread with ID: {current_thread_id}"
        )

    def run(self):
        """Starts the server thread."""
        self.logger.info("server starting...")
        # add check for already running server thread
        if self._thread is not None:
            raise RuntimeError("server is already running.")

        # set stop variable to be runnable
        self._runnable = True

        # start server thread
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        self.logger.info("server started.")

    def start(self):
        """Alias to run()"""
        self.run()

    def stop(self):
        """Stops the server thread."""
        self.logger.info("server stopping...")
        # set stop variable
        self._runnable = False

        # wait for worker threads to finish
        for t in self._worker_thread_pool:
            t.join()
        # wait for server thread to finish
        self._thread.join()

        # reset server thread
        self._thread = None
        self.logger.info("server stopped.")
