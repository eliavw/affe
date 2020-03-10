import json

import numpy as np
import pandas as pd

from ..dtaiexperimenter.monitor import Logfile, TimeLimit
from ..dtaiexperimenter.process import Process

VERBOSITY = 0

def get_monitors(log_filepath, timeout):
    """
    Create a monitor to go with a command.

    A monitor's job is to monitor a process. So, instead of just executing a
    command (i.e., running a process), we first build a monitor, and then pass
    monitor and command together to a dedicated Process class.

    This Process class executes the command, but also uses the monitor to
    capture logs and guard the timeout.

    Parameters
    ----------
    log_filepath: str
        Filename of log life
    timeout: int
        Timeout in seconds. Script is automatically aborted after this period.

    Returns
    -------

    """
    assert isinstance(log_filepath, str)
    assert isinstance(timeout, (int, np.int64))
    timeout = int(timeout)

    msg = """
    File is:        {}\n
    log_filepath is:   {}\n
    timeout is:     {}\n
    """.format(
        __file__, log_filepath, timeout
    )
    debug_print(msg, V=VERBOSITY)

    monitors = [Logfile(log_filepath), TimeLimit(timeout)]

    return monitors




# LEGACY
def debug_print(msg, level=1, V=0, **kwargs):

    """
    def get_var_name(var):
        var_name = [k for k, v in locals().items() if v is var][0]
        return var_name

    if kwargs.keys() > {'msg', 'level', 'V'}:
        print('INSIDE')
        relevant = {k:v for k,v in kwargs.items()
                    if k not in {'msg', 'level', 'V'}}
        for k,v in relevant.items():
            msg+="k: {}".format(v)
    """

    if V >= level:
        print(msg + "\n")
    return


def load_config(filename_config):
    with open(filename_config, "r") as f:
        config = json.load(f)
    return config


# Run
def run_script(
    script_fname, config_fname, log_filepath, fold=None, timeout=None, q_idx=None
):
    """
    Run an external script as an independent process, with logging and timeout.

    This method does three things:
        1. Generate the command to be executed in a terminal
        2. Generate the monitors that will be used to monitor its execution
        3. Execute the command, accompanied by its monitor

    So, we distinguish between a command, which is a very specifically formatted
    string to be entered in the terminal, and a process, which is the actual
    execution of this command.

    Parameters
    ----------
    script_fname: str
        Filename of script
    config_fname: str
        Filename of config file
    log_filepath: str
        Filename of log life
    fold: {int, None}
        Fold to be executed.
    timeout: int
        Timeout in seconds. Script is automatically aborted after this period.

    Returns
    -------

    """

    msg = """
    Fold:               {}
    Timeout:            {}
    type(Fold):         {}
    type(Timeout):      {}
    """.format(
        fold, timeout, type(fold), type(timeout)
    )
    debug_print(msg, V=VERBOSITY)

    if isinstance(q_idx, type(np.nan)):
        q_idx = None

    cmd = generate_command(
        script_fname, config_fname, fold=fold, q_idx=q_idx
    )  # Build command
    mon = generate_monitor(log_filepath, timeout)

    return run_process(cmd, mon)


def generate_command(
    script_fname, config_fname, script_prefix="python", fold=None, q_idx=None
):
    """
    Generate the command to be executed.

    A command is a very specifically formatted string, to be entered in a
    terminal. When this happens, the process linked to this command will be
    executed by the computer.

    Parameters
    ----------
    script_fname: str
        Filename of script
    config_fname: str
        Filename of config file
    script_prefix: str, default="python"
        First entry of the command. Usually specifies the programming language.
        If this is the empty string, it is completely ignored and not added to
        the cmd array.
    config_prefix: str, default=""
        Flag that precedes the config_fname. If this is the empty string, it is
        completely ignored and not added to the cmd array.
            E.g.; $ -c config.json
    fold: int, default=None
        Fold that has to run.

    Returns
    -------
    cmd: array[str]
        Array of strings that represent the things that are entered in the
        terminal.

    """

    assert isinstance(script_fname, str)
    assert isinstance(config_fname, str)
    assert isinstance(script_prefix, str)

    cmd = []

    if len(script_prefix) > 0:
        cmd.append(script_prefix)

    cmd.append(script_fname)

    cmd.append("--config_fname")
    cmd.append(config_fname)

    msg = """
    Fold provided: {}
    """
    debug_print(msg, V=VERBOSITY)

    if fold is not None:
        assert isinstance(fold, (int, np.int64))
        cmd.append(str(fold))

    if q_idx is not None:
        assert isinstance(q_idx, (int, float, np.int64))

        cmd.append("--q_idx")
        cmd.append(str(int(q_idx)))

    return cmd


def generate_monitor(log_filepath, timeout):
    """
    Create a monitor to go with a command.

    A monitor's job is to monitor a process. So, instead of just executing a
    command (i.e., running a process), we first build a monitor, and then pass
    monitor and command together to a dedicated Process class.

    This Process class executes the command, but also uses the monitor to
    capture logs and guard the timeout.

    Parameters
    ----------
    log_filepath: str
        Filename of log life
    timeout: int
        Timeout in seconds. Script is automatically aborted after this period.

    Returns
    -------

    """
    assert isinstance(log_filepath, str)
    assert isinstance(timeout, (int, np.int64))
    timeout = int(timeout)

    msg = """
    File is:        {}\n
    log_filepath is:   {}\n
    timeout is:     {}\n
    """.format(
        __file__, log_filepath, timeout
    )
    debug_print(msg, V=VERBOSITY)

    monitors = [Logfile(log_filepath), TimeLimit(timeout)]

    return monitors


# Helpers
def run_process(command, monitors=None, cwd=None):
    """
    Execute the command, monitored by the specified monitors.

    Parameters
    ----------
    command: list, shape(nb_strings, )
        List of strings that constitute the command to be entered in the
        terminal
    monitors: list, shape (nb_monitors)
        List of monitors, which will be used to monitor the process that
        executes the command.

    Returns
    -------

    """
    if monitors is None:
        msg = """
        Running process without monitors
        """
        print(msg)
    p = Process(command, monitors=monitors, cwd=cwd)  # Init Process
    return p.run()
