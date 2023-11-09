import logging
from random import randint

from context import lab_logging
from lab2.rpc.client import Client
from lab2.rpc.constRPC import CLIENT_WORK_DURATION
from lab2.rpc.dblist import DBList

lab_logging.setup(stream_level=logging.INFO)


def update_list_object(db_list: DBList, new_list: DBList):
    print(f"update list object {db_list} with {new_list}")
    # replace db_list elements with new_list elements
    db_list.value = new_list.value


# create new client object
cl = Client()
# run client
cl.run()

# create a list and append an element with the client RPC call
base_list = DBList({"foo"})
cl.append("bar", base_list, update_list_object)

# do random time some ordinary work
cl.do_work(duration_s=randint(CLIENT_WORK_DURATION[0], CLIENT_WORK_DURATION[1]))

# second iteration
cl.append("batz", base_list, update_list_object)
cl.do_work(duration_s=randint(CLIENT_WORK_DURATION[0], CLIENT_WORK_DURATION[1]))

cl.stop()

# print the list
print(base_list)

# obviously, the list is not updated, because the callback has not accessed the
# list object yet. This is because the callback is executed in a new thread.
# To fix this, we could store the data in a class variable and access it from
# the callback.
