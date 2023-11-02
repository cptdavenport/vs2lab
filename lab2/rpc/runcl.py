import logging
from time import sleep

import rpc
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl._call_method("print_string", ("asd"))

sleep(500)
cl.run()

base_list = rpc.DBList({"foo"})
result_list = cl.append("bar", base_list)

print("Result: {}".format(result_list.value))

cl.stop()
