from lxml import html
import requests
import pandas as pd
import numpy as np
import os

DEFAULT_PINAC_PAGE = "https://people.cs.kuleuven.be/~sebastijan.dumancic/pinacs/"


def parse_table_row(table):
    content = [t.text_content() for t in table]

    def interesting_row(row):
        if "pinac" in row[1]:
            return True
        elif "himec" in row[1]:
            return True
        elif "cudos" in row[1]:
            return True
        else:
            return False

    result = dict()
    if interesting_row(content):
        result["MACHINE"] = content[1]
        result["CPU"] = float(content[2])
        result["MEM"] = float(content[3])
        result["LOAD"] = float(content[4])

    return result


def parse_pinac_page(page_url=None):
    if page_url is None:
        page_url = DEFAULT_PINAC_PAGE

    page = requests.get(page_url)
    tree = html.fromstring(page.content)
    tr_elements = tree.xpath("//tr")

    df = pd.DataFrame()
    entries = [parse_table_row(table) for table in tr_elements[:35]]
    entries = [e for e in entries if len(e) > 1]

    df = df.from_records(entries)

    # Add metadata
    df["kind"] = df.apply(machine_kind, axis=1)
    df[["threads", "memory"]] = df.from_records(
        [pinac_parameters(m) for m in df.MACHINE.tolist()]
    )

    return df


def machine_kind(row):
    fake_ids = dict(a=17, b=18, c=19, d=20)
    fake_ids = {"-{}".format(k): v for k, v in fake_ids.items()}

    if row.MACHINE.startswith("pinac"):
        return "pinac"
    elif row.MACHINE.startswith("himec"):
        return "himec"
    elif row.MACHINE.startswith("cudos"):
        return "cudos"


def machine_split(machine):
    fake_ids = dict(a=17, b=18, c=19, d=20)
    fake_ids = {"-{}".format(k): v for k, v in fake_ids.items()}

    if machine.startswith("pinac"):
        try:
            return "pinac", int(machine.split("pinac")[1])
        except:
            # Convert to fake ids
            return "pinac", fake_ids[machine.split("pinac")[1]]
    elif machine.startswith("himec"):
        return "himec", int(machine.split("himec")[1])
    elif machine.startswith("cudos"):
        return "cudos", int(machine.split("cudos")[1])


def pinac_parameters(machine):

    name, idx = machine_split(machine)

    if name == "pinac":
        if 10 < idx < 31:
            return dict(threads=4, memory=16)
        elif 30 < idx < 41:
            return dict(threads=8, memory=32)
    elif name == "himec":
        if idx in {1, 2}:
            return dict(threads=24, memory=128)
        elif idx in {3, 4}:
            return dict(threads=32, memory=128)
    elif name == "cudos":
        return dict(threads=40, memory=128)
    else:
        raise ValueError("I do not know this pinac.")


def available_threads(row, desired_memory_per_thread=8):
    threads_based_on_load = row.threads - int(row.LOAD)
    threads_based_on_mem = int(
        (row.memory - row.MEM * 0.01 * row.memory) / desired_memory_per_thread
    )
    threads_based_on_CPU = int(row.threads - row.CPU * 0.01 * row.threads)

    avl_threads = min(threads_based_on_load, threads_based_on_mem, threads_based_on_CPU)
    return max(0, avl_threads)


def determine_nb_of_threads_to_claim(
    avl_threads, max_percentage_thread_claim=50, desired_nb_threads=None
):
    if desired_nb_threads is None:
        desired_nb_threads = 10 ** 3

    max_avl_thread_count = avl_threads.sum()
    availab_thread_count = int(max_percentage_thread_claim / 100 * max_avl_thread_count)
    threads_to_claim = min(availab_thread_count, desired_nb_threads)
    return threads_to_claim


def greedy_claim(avl_threads, nb_of_threads_to_claim):
    threads_left_to_claim = nb_of_threads_to_claim
    claim = np.zeros(len(avl_threads), dtype=int)
    assert np.sum(avl_threads) >= nb_of_threads_to_claim

    for idx, x in enumerate(avl_threads):
        claim_here = min(x, threads_left_to_claim)
        claim[idx] = claim_here
        threads_left_to_claim = threads_left_to_claim - claim_here
        if threads_left_to_claim < 1:
            break
    return claim


def uniform_claim(avl_threads, nb_of_threads_to_claim):
    threads_left_to_claim = nb_of_threads_to_claim
    claim = np.zeros(len(avl_threads), dtype=int)
    assert np.sum(avl_threads) >= nb_of_threads_to_claim

    avl_indices = []
    for idx, x in enumerate(avl_threads):
        avl_indices.extend([idx] * x)
    avl_indices = np.array(avl_indices)
    np.random.shuffle(avl_indices)

    for idx in avl_indices:
        claim[idx] += 1
        threads_left_to_claim -= 1

        if threads_left_to_claim < 1:
            break
    return claim


def nodefile_df_to_string(df, username="user"):
    nodefile_str = ""
    for t in df[["MACHINE", "claim"]].itertuples():
        nodefile_str += "{0}/{1}@{2}.cs.kuleuven.be\n".format(t[2], username, t[1])
    return nodefile_str


def generate_nodefile(
    df=None,
    desired_memory_per_thread=8,
    desired_nb_threads=None,
    max_percentage_thread_claim=50,
    kinds={"pinac", "himec", "cudos"},
    claim_policy="greedy",
    username="user",
):

    claim_functions = dict(greedy=greedy_claim, uniform=uniform_claim)

    if df is None:
        df = parse_pinac_page()

    max_percentage_thread_claim = _convert_max_percentage_thread_claim(
        max_percentage_thread_claim
    )

    df["avl"] = df.apply(
        available_threads, axis=1, desired_memory_per_thread=desired_memory_per_thread
    )
    df["claim"] = 0

    # Kind-filter
    if kinds is not None:
        df = df[df["kind"].isin(kinds)].copy()

    nb_of_threads_to_claim = determine_nb_of_threads_to_claim(
        df.avl.values,
        max_percentage_thread_claim=max_percentage_thread_claim,
        desired_nb_threads=desired_nb_threads,
    )

    df["claim"] = claim_functions[claim_policy](df.avl.values, nb_of_threads_to_claim)

    # To string
    nf_string = nodefile_df_to_string(df, username=username)
    return nf_string


def _convert_max_percentage_thread_claim(max_percentage_thread_claim):
    if isinstance(max_percentage_thread_claim, str):
        if max_percentage_thread_claim in {"asshole"}:
            max_percentage_thread_claim = 90
        elif max_percentage_thread_claim in {"deadline"}:
            max_percentage_thread_claim = 80
        elif max_percentage_thread_claim in {"high"}:
            max_percentage_thread_claim = 70
        elif max_percentage_thread_claim in {"medium"}:
            max_percentage_thread_claim = 50
        elif max_percentage_thread_claim in {"low"}:
            max_percentage_thread_claim = 30
    else:
        assert isinstance(max_percentage_thread_claim, int)
    return max_percentage_thread_claim
