import glob

import yaml


def parse_config(config_dir) -> dict:
    main_config_files = list()
    main_config_files += glob.glob(f"{config_dir}/*[!override].yaml")
    main_config_files += glob.glob(f"{config_dir}/*.override.yaml")
    config = parse_yaml(*main_config_files)

    config["Roles"] = [
        parse_yaml(role_file) for role_file in glob.glob(f"{config_dir}/roles/**/*.yaml", recursive=True)
    ]

    config["Secrets"] = [
        parse_yaml(secret_file) for secret_file in glob.glob(f"{config_dir}/secrets/**/*.yaml", recursive=True)
    ]

    return config


def parse_yaml(*paths) -> dict:
    parsed_dict = {}
    for path in paths:
        with open(path, "r") as file:
            parsed_dict.update(yaml.safe_load(file))
    return parsed_dict


if __name__ == "__main__":
    from os.path import abspath, dirname

    config_dir = f"{dirname(abspath(__file__))}/../config"
    config = parse_config(config_dir)
    print("Loaded configuration", config)
