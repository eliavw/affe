"""
experimenter.remote.push - Remote Listening

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
import platform
import traceback
import uuid
import datetime

import zmq

from ..monitor import ProcessMonitor
from ..utils import levels

logger = logging.getLogger("be.kuleuven.cs.dtai.experimenter")


class PushToRemote(ProcessMonitor):
    def __init__(self, host=None, port=None,
                 keep_alive=None, msg_queue_size=None,
                 tunnel=None):
        """A monitor that sends the information messages (no stdin or stdout)
        to a remote listener.
        :param host: ip address of instance where the listener is running.
        :param port: port to which the remote instance listens.
        :param keep_alive: keep process active until the queue has been sent to remote viewer
            for the given amount of milliseconds. A value of -1 means wait forever.
            Default is to drop all remaining messages and immediately quit.
        :param msg_queue_size: Number of messages to remember if no remote is found.
            Default is 0 which is an unlimited queue.
            A value of -1 remembers only last message and does not listen to keep_alive.
        :param tunnel: Server to use as tunnel, format is user@server:port
        """
        super().__init__()
        if port is None:
            self.port = 5556
        else:
            self.port = int(port)
        if host is None:
            self.host = "127.0.0.1"
        else:
            self.host = host
        self.context = None
        self.socket = None
        self.node = platform.node()
        self.unique_node = "{}-{}".format(self.node, uuid.uuid1().hex)
        self.listen_to_output = True
        if keep_alive is None:
            self.linger = 0  # Discard immediately
        else:
            self.linger = int(keep_alive)
        if msg_queue_size is None:
            self.msg_queue_size = 0  # No limit
        elif msg_queue_size == -1:
            self.msg_queue_size = None  # Only last
        elif msg_queue_size > 0:
            self.msg_queue_size = msg_queue_size  # Nb of messages
        else:
            self.msg_queue_size = 0
        self.tunnel = tunnel

    def _set_up(self, parent, popen_args=None):
        # http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pushpull.html
        self.info("Starting node: {}".format(self.unique_node))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        # self.socket.setsockopt(zmq.SNDBUF, 2048)
        if self.msg_queue_size is None:
            self.socket.setsockopt(zmq.CONFLATE, 1)
        else:
            self.socket.set_hwm(self.msg_queue_size)
        if self.tunnel is not None:
            from zmq import ssh
            self.info("Subscribe to {}:{} over server {}".format(self.host, self.port, self.tunnel))
            ssh.tunnel_connection(self.socket, "tcp://{}:{}".format(self.host, self.port), self.tunnel)
        else:
            self.info("Subscribe to {}:{}".format(self.host, self.port))
            self.socket.connect("tcp://{}:{}".format(self.host, self.port))

    def _tear_down(self, returncode):
        self.info("Closing remote connection")
        self.socket.close(linger=self.linger)  # Discard unsent messages
        self.context.term()

    def get_log(self, msg, identifier):
        if self.socket is None:
            logger.info('No socket connected')
        else:
            if identifier <= levels.CRITICAL and not self.socket.closed:
                ts = datetime.datetime.now().isoformat()
                try:
                    # result of poll is 0=can't write, 2=can write
                    # result = self.socket.poll(timeout=1000, flags=3)  # get_log should not block
                    # print(result, msg)
                    self.socket.send_json([self.unique_node, identifier, msg, ts], flags=zmq.NOBLOCK)
                except zmq.error.Again as exc:
                    # Message cannot be delivered
                    logger.warning("Cannot send information to remote viewer ({})".format(exc))
                except zmq.error.ZMQError as exc:
                    logger.warning("Problem connecting with remote ({})".format(exc))
                except Exception as exc:
                    traceback.print_exc()
                    logger.warning("Exception in remote ({})".format(exc))
