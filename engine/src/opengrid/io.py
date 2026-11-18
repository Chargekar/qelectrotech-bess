"""Safe load/save for canonical project documents."""
from pathlib import Path
import json
import yaml

from .schema import Project


def load_project(path: Path | str) -> Project:
    path = Path(path)
    data = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return Project.model_validate_json(data)
    if path.suffix.lower() in (".yaml", ".yml"):
        return Project.model_validate(yaml.safe_load(data))
    raise ValueError("Expected a JSON or YAML project")


def save_project(project: Project, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = project.model_dump(mode="json")
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    elif path.suffix.lower() in (".yaml", ".yml"):
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    else:
        raise ValueError("Expected a JSON or YAML output path")
