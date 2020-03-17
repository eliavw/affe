import time

from ..io import (
    get_root_directory,
    get_flow_directory,
    insert_subdirectory,
    abspath,
    check_existence_of_directory,
    dump_object,
)

from ..flow import Flow

def get_dummy_fs():
    root_dir = get_root_directory()
    flow_dir = get_flow_directory(keyword="flow")

    dummy_fs = insert_subdirectory(root_dir, parent="out", child=flow_dir,)
    return dummy_fs


def get_dummy_config(message="hi", content=dict(a=3, b=4)):
    dummy_fs = get_dummy_fs()
    return dict(io=dict(fs=dummy_fs), message=message, content=content)


def dummy_imports():
    import time
    import affe
    from affe.io import (
        get_root_directory,
        get_flow_directory,
        insert_subdirectory,
        abspath,
        check_existence_of_directory,
        dump_object,
    )

    print("Imports succesful")

    return


def dummy_flow(config):
    print("Hello world")

    fs = config.get("io").get("fs")
    content = config.get("content")
    message = config.get("message")

    results_directory_key = "out.flow.results"
    check_existence_of_directory(fs, results_directory_key)
    fn_results = abspath(fs, results_directory_key, filename="{}.json".format(message))

    results = content

    dump_object(results, fn_results)

    # Some extra actions
    sleep_a_few_s = 2
    time.sleep(sleep_a_few_s)
    print("{} secs passed".format(sleep_a_few_s))
    print(message)

    return content


def get_dummy_flow(message="hi", content=dict(a=1, b=2), timeout_s=20):
    # config
    dummy_config = get_dummy_config(message=message, content=content)
    dummy_fs = dummy_config.get("io").get("fs")

    # flow-object
    logs_directory_key = "out.flow.logs"
    check_existence_of_directory(dummy_fs, logs_directory_key)
    log_filepath = abspath(dummy_fs, logs_directory_key, "logfile"+message)

    flows_directory_key = "out.flow.flows"
    check_existence_of_directory(dummy_fs, flows_directory_key)
    flow_filepath = abspath(dummy_fs, flows_directory_key, "flowfile-{}.pkl".format(message))

    f = Flow(
        config=dummy_config,
        imports=dummy_imports,
        flow=dummy_flow,
        timeout_s=timeout_s,
        flow_filepath=flow_filepath,
        log_filepath=log_filepath,
    )
    return f
