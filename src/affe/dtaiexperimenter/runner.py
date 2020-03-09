"""
experimenter.runner - Wrapper to run a given command line entry

__author__ = "Wannes Meert, Anton Dries"
__copyright__ = "Copyright 2017 KU Leuven, DTAI Research Group"
__license__ = "APL"

..
    Part of the DTAI experimenter code.

    Copyright 2017 KU Leuven, DTAI Research Group

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
from . import __version__
from .process import Process, logger
from .monitor import Print, Logfile, MemoryLimit, TimeLimit, FileSizeLimit
from .utils import levels
from .remote.push import PushToRemote


def run_external_binary(cmd=None, memory_limit=None, unbuffered=False, force=False, cwd=None,
                        timeout=None, remote=None, file_limit=None, memory_available=None,
                        hide_output=False, log_lvl=levels.INFO, logfile="testlog", **kwargs):
    """
    Excute a command with monitoring.

    :param cmd: List representing the command and arguments
    :param memory_limit: Max memory in MiB
    :param unbuffered: Run binary in pseudo-terminal instead as pipe
    :param force: Force run, even if there is a successful log file
    :param cwd: Current Working Directory
    :param timeout: Max time in seconds
    :param remote: Remote IP address where the remoteviewer runs
    :param file_limit: Max file size in MiB (structure is 'filepath:size')
    :param memory_available: Min memory that should be available on the system in MiB
    :param hide_output: Do not print stdout/stderr to logfile
    :param log_lvl: Verbosity level (default is levels.INFO)
    :param logfile: Path to log file
    :param kwargs: Other arguments (all ignored)
    :return:
    """
    monitors = list()

    # Write output to stdout
    include_stdout = not hide_output
    monitors.append(Print(log_lvl=log_lvl, include_stdout=include_stdout))

    # Write output and information to a log file
    monitors.append(Logfile(logfile, force))

    # Write information to a remote viewer
    if remote is not None:
        if ":" in remote:
            host, port = remote.split(":")
            port = int(port)
        else:
            host = remote
            port = None
        monitors.append(PushToRemote(host=host, port=port,
                                     keep_alive=True, msg_queue_size=0))

    # Monitor memory usage of process
    if memory_limit is not None or memory_available is not None:
        monitors.append(MemoryLimit(maxmem=memory_limit, minavailable=memory_available))

    # Monitor runtime of process
    if timeout is not None:
        monitors.append(TimeLimit(timeout))

    # Monitor filesize of a given file
    if file_limit is not None:
        filename, filesize = file_limit.split(":")
        filesize = float(filesize)
        monitors.append(FileSizeLimit(filename=filename, maxsize=filesize*1024*1024))

    # Run the actual process with a list of monitors
    p = Process(cmd, unbuffered=unbuffered, monitors=monitors, cwd=None, hide_output=hide_output)
    p.run()


def get_log_lvl(verbose=None, quiet=None, **kwargs):
    dec = 0
    if verbose is not None:
        dec += verbose
    if quiet is not None:
        dec -= quiet
    return levels.INFO-10*dec  # Default is level INFO


def usage_examples(binary_name="example.py"):
    return "\n".join([
        "Examples:",
        "  {} binary --memlimit=100 --timeout=300".format(binary_name),
        "",
        "Copyright 2017, DTAI KU Leuven, https://dtai.cs.kuleuven.be"
    ])


def build_parser_experimenter(parser):
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite logfile')
    parser.add_argument('--logfile', default='testlog', help='Logfile filename')
    parser.add_argument('--memlimit', dest='memory_limit', default=None, help='Memory limit (MiB)')
    parser.add_argument('--memavailable', dest='memory_available', default=None,
                        help='Minimal amount of memory that should still be available (MiB)')
    parser.add_argument('--timeout', default=None, help="Timeout (sec)")
    parser.add_argument('--filelimit', dest='file_limit', default=None,
                        help="Max file size for given file. Format=filename:size_mb")
    parser.add_argument('--remote', help="Send monitoring information to remote at this address")
    parser.add_argument('--unbuffered', action='store_true', help='Replace pipe with pseudo-terminal')
    parser.add_argument('--hideoutput', dest='hide_output', action='store_true',
                        help='Do not print the subprocess output to screen')
    parser.add_argument('--cwd', help='Current working directory')


def build_parser_general(parser):
    parser.add_argument('cmd', help='Command to run', nargs='?')
    parser.add_argument('--version', action='version', version='Experimenter ' + __version__)
    parser.add_argument('--verbose', '-v', action='count', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='count', help='Silence output')
