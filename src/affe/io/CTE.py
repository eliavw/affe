
# Suggested Defaults
SEPARATOR = "-"
KEYCHAIN_SEPARATOR = "."
LABELS = dict(query="q", exp="e", fold="f", experiment="e")
DEFAULT_CHILDREN = dict(
    root=["cli", "data", "out", "scripts"],
    out=["manual", "preprocessing", "fit", "predict"],
    model=["models", "logs", "timings"],
    flow=["config", "logs", "results", "models", "timings", "tmp", "flows"],
)

