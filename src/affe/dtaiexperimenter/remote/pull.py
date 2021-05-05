"""
experimenter.remote.pull - Remote Listening

__author__ = "Wannes Meert"
__copyright__ = "Copyright 2016 KU Leuven, DTAI Research Group"
__license__ = "APL"

..
    Part of the DTAI experimenter code.

    Copyright 2016 KU Leuven, DTAI Research Group

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import logging
import zmq

from ..utils import levels, level_prefix


logger = logging.getLogger("be.kuleuven.cs.dtai.experimenter")


class Pull:
    def __init__(self, port=None):
        """Start a pull process that listens to messages on the given port.
        :param port: Port to listen to.
        """
        # http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pushpull.html
        if port is None:
            self.port = 5556
        else:
            self.port = int(port)
        self.host = "*"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        logger.info("Start listening at {}:{}".format(self.host, self.port))
        self.socket.bind("tcp://{}:{}".format(self.host, self.port))

    def process_msg(self, node, identifier, msg, ts):
        """Do something with the message send by a node.
        :param node: Name of node that sends the message
        :param identifier: Log level according to process.levels
        :param msg: The actual message
        """
        if identifier >= levels.STDOUT:
            print(
                "{:<20} - {:<20}: {} {}".format(
                    ts, node, level_prefix[identifier], msg
                ),
                end="",
            )
        else:
            print(
                "{:<20} - {:<20}: {} {}".format(ts, node, level_prefix[identifier], msg)
            )

    def run(self):
        try:
            while True:
                msg = self.socket.recv_json()
                self.process_msg(*msg)
        except KeyboardInterrupt:
            print("\nStopping remote viewer")
