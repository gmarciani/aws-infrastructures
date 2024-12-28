import yaml
import os


def parse_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def remove_special_characters(string: str) -> str:
    return "".join(e for e in string if e.isalnum())


def list_directories(source_path: str, prefix: str = None) -> list[str]:
    return [
        name
        for name in os.listdir(source_path)
        if os.path.isdir(os.path.join(source_path, name)) and (prefix is None or name.startswith(prefix))
    ]


def render_template(path: str, params: dict[str, str]) -> str:
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    for key, value in params.items():
        if value is not None:
            content = content.replace(f"<% {key} %>", value)

    return content
