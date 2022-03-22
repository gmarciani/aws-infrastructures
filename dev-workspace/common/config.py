import yaml


def parse_config(path_base, path_override) -> dict:
    with open(path_base, "r") as file:
        config = yaml.safe_load(file)
    with open(path_override, "r") as file:
        config.update(yaml.safe_load(file))
    return config
