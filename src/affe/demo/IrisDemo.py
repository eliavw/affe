from ..flow import Flow

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from time import sleep


class IrisDemo(Flow):
    def __init__(self, max_depth=None, sleep_seconds=0, **kwargs):
        """
        All the information you want to pass inside the flow function,
        you can embed in the config dictionary.
        """
        self.config = dict(max_depth=max_depth, sleep_seconds=sleep_seconds)
        super().__init__(config=self.config, **kwargs)
        return

    @staticmethod
    def imports():
        """For remote executions, you better specify your imports explicitly.

        Depending on the use-case, this is not necessary, but it will never hurt.
        """
        from sklearn import datasets
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        from time import sleep

        return

    def flow(self, config):
        """
        This function is basically a verbatim copy of your workflow above.

        Prerequisites:
            - This function has to be called flow
            - It expects one input: config

        The only design pattern to take into account is that you can assume one
        input only, which then by definition constitutes your "configuration" for your workflow.
        Whatever parameters you need, you can extract from this. This pattern is somewhat restricitive,
        but if you are implementing experiments, you probably should be this strict anyway; you're welcome.

        The other thing is the name of this function: it has to be "flow", in order for some of the
        executioners to properly find it. Obviously, if your only usecase is to run the flow function
        yourself, this does not matter at all. But in most cases it does, and again: adhering to this pattern
        will never hurt you, deviation could.
        """
        # Obtain configuration
        max_depth = config.get("max_depth", None)
        sleep_seconds = config.get("sleep_seconds", 0)

        print("I am about to execute the IRIS FLOW")
        print("BUT FIRST: I shall sleep {} seconds".format(sleep_seconds))
        sleep(sleep_seconds)
        print("I WOKE UP, gonna do my stuff now.")

        # Load data
        X, y = datasets.load_iris(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        # Fit classifier
        clf = DecisionTreeClassifier(max_depth=max_depth)
        clf.fit(X_train, y_train)

        # Predict and Evaluate
        y_pred = clf.predict(X_test)

        score = accuracy_score(y_test, y_pred, normalize=True)

        msg = """
        I am DONE executing the IRIS FLOW
        """
        print(msg)
        return score
