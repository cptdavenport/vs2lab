import logging
import random
import threading
from time import sleep

import constRPC
from lab2.rpc.dblist import DBList
from lib import lab_channel


class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join(constRPC.CLIENT_CHANNEL)
        self.server = None
        self.logger = logging.getLogger("vs2lab.lab2.channel.Client")
        self._thread_pool = list()  # add empty thread pool

    def run(self):
        """
        Start the client by binding to the server channel.
        """
        self.chan.bind(self.client)
        self.server = self.chan.subgroup(constRPC.SERVER_CHANNEL)

    def stop(self):
        """
        Stop the client by unbinding from the server channel.
        """
        # join all threads in thread pool
        for t in self._thread_pool:
            t.join()

        # leave server channel
        self.chan.leave(constRPC.CLIENT_CHANNEL)

    def append(self, data, db_list, callback: callable):
        """
        Append data to db_list by sending a RPC to the server. The sever will
        call the append method of the DBList object and return the result to the
        client. The client will then call the callback with the result as argument.

        The callback will be called in a new thread and update the db_list object.

        Args:
            data (object): the data to append to the list
            db_list (DBList): the list to append to
            callback (callable): the callback to call with the result from the server
        """
        # check if db_list is a DBList
        assert isinstance(db_list, DBList)

        # create message payload of tuple with 3 elements (int, str, DBList)
        msg_lst = (constRPC.APPEND, data, db_list)

        # send message to server and wait for ACK
        self.chan.send_to(self.server, msg_lst)
        self.logger.info("Message sent to server")
        # wait for ACK, blocking
        # use _ to ignore first arg of sender id
        # see tuple unpacking at
        # https://docs.python.org/3/tutorial/controlflow.html#tut-unpacking-arguments
        _, srv_ack = self.chan.receive_from(self.server)

        # check if ACK is OK
        if srv_ack == constRPC.ACK:
            self.logger.info("ACK received")
        else:
            self.logger.error("ERROR, wrong ACK received")
            return

        # wait for result in new thread
        # first add thread to thread pool
        self._thread_pool.append(
            threading.Thread(
                target=self.wait_for_result,
                kwargs={"callback": callback, "original_db_list": db_list},
                daemon=True,
            )
        )
        # then start last added thread
        self._thread_pool[-1].start()
        self.logger.info(f"started thread[{self._thread_pool[-1].native_id}]")

    def wait_for_result(self, callback: callable, original_db_list: DBList):
        """
        Wait for result from server and call callback with result.
        Args:
            callback (callable): callback function to call with result from server
            original_db_list (DBList): the list to update with the result
        """
        # get thread id of current running thread
        current_thread_id = threading.get_native_id()
        self.logger.info(f"WORKER[{current_thread_id}]: waiting for result ...")

        # blocking wait for result
        # use _ to ignore first arg of sender id
        # see tuple unpacking at
        # https://docs.python.org/3/tutorial/controlflow.html#tut-unpacking-arguments
        _, new_db_list = self.chan.receive_from(self.server)
        self.logger.info(f"WORKER[{current_thread_id}]: received result from server")
        self.logger.info(f"WORKER[{current_thread_id}]: calling callback ...")

        # call callback with result
        callback(original_db_list, new_db_list)
        self.logger.info(f"WORKER[{current_thread_id}]: finished.")

    def update_list_object(self, db_list: DBList, new_list: DBList):
        print(f"update list object {db_list} with {new_list}")
        # replace db_list elements with new_list elements
        db_list = new_list

    def do_work(self, duration_s: int = None):
        """
        Do some work for a given amount of time. If no duration is given, a random
        duration between 1 and 10 seconds is chosen.
        Args:
            duration_s (int, optional): duration in seconds to do work
        """
        # optional duration. set to random int between 1 and 10 if not given
        if duration_s is None:
            duration_s = random.randint(1, 10)

        # do work by sleeping for given duration
        self.logger.info(f"starting work for {duration_s} seconds")
        sleep(duration_s)
        self.logger.info(f"finished work for {duration_s} seconds")
