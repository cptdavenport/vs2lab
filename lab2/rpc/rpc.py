import logging
import threading
from typing import Tuple

import constRPC
from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client:
    def __init__(self):
        # self.chan = lab_channel.Channel()
        # self.client = self.chan.join("client")
        self.server = None
        # self.logger = logging.getLogger("vs2lab.lab2.channel.Client")

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup("server")

    def stop(self):
        self.chan.leave("client")

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        msgrcv = self.chan.receive_from(self.server)  # wait for response
        return msgrcv[1]  # pass it to caller

    def _call_method(
        self,
        method_name: str,
        args: tuple = None,
    ) -> Tuple[bool, str]:
        # add empty args tuple if none is given
        if args is None:
            args = ()
        # make sure args is a tuple, e.g. one arg as a single string
        if not isinstance(args, tuple):
            args = (args,)
        # check if method exists
        try:
            method = getattr(self, method_name)
        except AttributeError:
            return False, f'Method "{method_name}" not found'
        except TypeError:
            return False, f'Wrong number of arguments for"{method_name}" '
        return method(*args), "OK"

    def print_hello(self):
        print("hello")

    def print_string(self, string):
        print(string)


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join(constRPC.SERVER_CHANNEL)
        self.logger = logging.getLogger("vs2lab.lab2.channel.Server")
        self.timeout = 3
        self._thread = None
        self._runnable = False

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
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore
        self.logger.info(
            f'Server left channel "{constRPC.SERVER_CHANNEL}" with pid "{self.server}".'
        )

    def run(self):
        """Starts the server thread."""
        self.logger.info("Server starting...")
        # add check for already running server thread
        if self._thread is not None:
            raise RuntimeError("Server is already running.")

        # set stop variable to be runnable
        self._runnable = True

        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        self.logger.info("Server started.")

    def start(self):
        """Alias to run()"""
        self.run()

    def stop(self):
        """Stops the server thread."""
        self.logger.info("Server stopping...")
        # set stop variable
        self._runnable = False
        # wait for server thread to finish
        self._thread.join()
        # reset server thread
        self._thread = None
        self.logger.info("Server stopped.")
