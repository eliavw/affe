import time

from sklearn.model_selection import train_test_split

from ..flow import Flow
from ..io import (
    FN_TEMPLATE_CLASSIC_FLOW,
    abspath,
    check_existence_of_directory,
    dump_object,
    get_flow_directory,
    get_subdirectory_paths,
    get_template_filenames,
    insert_subdirectory,
    mimic_fs,
)


# Boilerplate superclass
class GenericBenchmark(Flow):
    """Generic example of a benchmark experiment.

    N.b.:This is an abstract class, will fail if used directly
    """

    flow_identifier = "GenericBenchmark"
    algorithms = dict(default=None)
    analysis = dict(default=None)

    def __init__(self, timeout_s=60, **kwargs):

        # Fix config
        io_config = self.get_io_config(**kwargs)
        rest_config = self.get_rest_config(**kwargs)
        algo_config = self.get_algo_config(**kwargs)
        config = dict(io=io_config, algo=algo_config, **rest_config)

        # Extract filepaths relevant for own initialization already.
        super().__init__(
            config=config,
            log_filepath=config.get("io").get("flow_filenames_paths").get("logs"),
            flow_filepath=config.get("io").get("flow_filenames_paths").get("flows"),
            timeout_s=timeout_s,
        )
        return

    @staticmethod
    def imports():
        import sys
        import os
        import affe

        return

    # Config-zone starts here.
    @staticmethod
    def get_rest_config(dataset_id="iris", **kwargs):

        cfg_data = dict(
            dataset_id=dataset_id,
        )

        cfg_analysis = dict(analysis_id="default")

        cfg_visuals = dict()

        config = dict(
            data=cfg_data,
            analysis=cfg_analysis,
            visuals=cfg_visuals,
        )

        return config

    def get_io_config(
        self,
        flow_id=0,
        flow_identifier=None,
        root_levels_up=1,
        fs_depth=2,
        out_directory="out",
        out_parent="root",
        exclude_in_scan=None,  # Just use the defaults, they're fine.
        **kwargs
    ):
        if flow_identifier is None:
            flow_identifier = self.flow_identifier
        # Perform duties
        fs = mimic_fs(
            root_levels_up=root_levels_up,
            depth=fs_depth,
            exclude=frozenset(exclude_in_scan)
            if exclude_in_scan is not None
            else exclude_in_scan,
        )

        ## Build the filesystem we desire
        fs, out_key = insert_subdirectory(
            fs, parent=out_parent, child=out_directory, return_key=True
        )

        flow_directory = get_flow_directory(keyword=flow_identifier)
        fs, flow_key = insert_subdirectory(
            fs, parent=out_key, child=flow_directory, return_key=True
        )

        check_existence_of_directory(fs)

        ## Collect relevant paths for later actions in the workflow
        flow_directory_paths = get_subdirectory_paths(fs, flow_key)
        flow_filenames_paths = get_template_filenames(
            flow_directory_paths, idx=flow_id, template=FN_TEMPLATE_CLASSIC_FLOW
        )

        # collect outgoing information
        io_config = dict(
            flow_id=flow_id,
            fs=fs,
            flow_key=flow_key,
            flow_directory_paths=flow_directory_paths,
            flow_filenames_paths=flow_filenames_paths,
        )

        return io_config

    # Flow-zone starts here.
    def flow(self, config):
        io = config.get("io")
        data = self.get_data(io, **config.get("data"))

        m_algo = self.get_algo(data, **config.get("algo"))
        a_algo = self.ask_algo(data, m_algo)

        # Process results
        analysis = self.get_analysis(m_algo, a_algo, **config.get("analysis"))
        retention_ok = self.get_retention(io, data, analysis, config)

        return analysis

    ## Data
    def get_data(self, io, dataset_id=None, add_internal_metadata=True, **kwargs):
        # collect ingoing information

        # perform duties
        dataset = self.get_dataset(io, dataset_id=dataset_id, **kwargs)

        metadata = self.get_metadata(
            dataset, add_internal_metadata=add_internal_metadata
        )
        preprocessing = self.get_preprocessing(dataset, **kwargs)

        # collect outgoing information
        data = dict(metadata=metadata, pp=preprocessing)
        return data

    @staticmethod
    def get_metadata(dataset, add_internal_metadata=True):

        # perform duties
        dataset_name = dataset.get("name")

        n_features = dataset.get("X").shape[1] + 1
        n_instances = dataset.get("X").shape[0]

        # collect outgoing information
        metadata = dict(
            dataset=dataset_name,
            n_features=n_features,
            n_instances=n_instances,
        )

        if add_internal_metadata:
            internal_metadata = dataset.get("metadata")
            metadata = {**metadata, **internal_metadata}
        return metadata

    @staticmethod
    def get_preprocessing(dataset, random_state=42):
        """Put the data in the actionable format required by the subsequent algorithms.

        Typically, this involves going to actual matrix form.
        """
        # collect ingoing information
        X = dataset.get("X")
        y = dataset.get("y")

        # perform duties
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, random_state=random_state
        )

        # collect outgoing information
        preprocessing = dict(
            X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
        )
        return preprocessing

    ## Retention
    def get_retention(self, io, data, analysis, config):
        # collect ingoing information
        metadata = data.get("metadata")
        fn_results = io.get("flow_filenames_paths").get("results")
        fn_config = io.get("flow_filenames_paths").get("config")

        # perform duties
        results = dict(analysis=analysis, metadata=metadata)

        config_ok = dump_object(config, fn_config)
        results_ok = dump_object(results, fn_results)

        # collect outgoing information
        oks = [results_ok, config_ok]

        return all(oks)

    @staticmethod
    def get_dataset(io, **kwargs):
        raise NotImplementedError
        return

    def get_analysis(self, model, answers, **analysis_config):
        raise NotImplementedError
        return

    # Algorithm-Specific Implementation
    @staticmethod
    def get_algo_config(algorithm_id="default", **kwargs):
        raise NotImplementedError
        return

    def get_algo(self, data, **algo_config):
        raise NotImplementedError
        return

    @staticmethod
    def ask_algo(data, m_algo):
        raise NotImplementedError
        return


class GenericAlgorithmDemo(GenericBenchmark):
    """Demo that shows how a specific algorithm extends the generic"""

    algorithms = dict(default=None)
    analysis = dict(default=None)

    @staticmethod
    def get_dataset(io, dataset_id="iris", **kwargs):
        # collect ingoing information

        # perform duties

        # collect outgoing information
        dataset = dict(
            X=None,
            y=None,
            name=dataset_id,
            metadata=dict(),
        )

        return dataset

    def get_analysis(self, model, answers, **analysis_config):
        # collect ingoing information
        y_test = answers.get("y_test")
        y_pred = answers.get("y_pred")
        fit_time_s = model.get("fit_time_s")
        predict_time_s = answers.get("predict_time_s")
        analysis_id = analysis_config.get("analysis_id")

        reduced_analysis_config = analysis_config.copy()

        # perform duties
        reduced_analysis_config.pop(
            "analysis_id"
        )  # Obviously, the id is not an internal parameter

        metric = self.analysis.get(analysis_id)
        score = metric(y_test, y_pred, **reduced_analysis_config)

        # collect outgoing information
        analysis = dict(
            fit_time_s=fit_time_s, predict_time_s=predict_time_s, score=score
        )

        return analysis

    # Algorithm-Specific Implementation

    @staticmethod
    def get_algo_config(algorithm_id="default", **kwargs):
        algo_config = dict(algorithm_id=algorithm_id, **kwargs)
        return algo_config

    def get_algo(self, data, **algo_config):
        # collect ingoing information
        X_train = data.get("pp").get("X_train")
        y_train = data.get("pp").get("y_train")
        algorithm_id = algo_config.get("algorithm_id")

        reduced_algo_config = algo_config.copy()

        # perform duties
        reduced_algo_config.pop(
            "algorithm_id"
        )  # Obviously, the id is not an internal parameter

        ModelAlgorithm = self.algorithms.get(algorithm_id)
        model = ModelAlgorithm(**reduced_algo_config)

        tick = time.time()
        model.fit(X_train, y_train)
        tock = time.time()

        fit_time_s = tock - tick

        # collect outgoing information
        m_algo = dict(model=model, fit_time_s=fit_time_s)
        return m_algo

    @staticmethod
    def ask_algo(data, m_algo):
        # collect ingoing information
        model = m_algo.get("model")
        X_test = data.get("pp").get("X_test")
        y_test = data.get("pp").get("y_test")

        # perform duties
        tick = time.time()
        y_pred = model.predict(X_test)
        tock = time.time()
        predict_time_s = tock - tick

        # collect outgoing information
        a_algo = dict(y_test=y_test, y_pred=y_pred, predict_time_s=predict_time_s)

        return a_algo
