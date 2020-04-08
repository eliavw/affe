from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

from .GenericBenchmark import GenericAlgorithmDemo


class DTDemo(GenericAlgorithmDemo):
    """This demo shows how to setup a very simple sklearn flow
    """

    algorithms = dict(default=DecisionTreeClassifier)
    analysis = dict(default=accuracy_score)

    @staticmethod
    def get_dataset(io, dataset_id="iris", **kwargs):
        # collect ingoing information

        # perform duties
        if dataset_id == "iris":  # This demo only works with iris
            X, y = load_iris(return_X_y=True)

        # collect outgoing information
        dataset = dict(X=X, y=y, name=dataset_id, metadata=dict(),)

        return dataset
