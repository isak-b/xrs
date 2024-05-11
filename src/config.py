import yaml


def load_cfg(path: str = "config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)
