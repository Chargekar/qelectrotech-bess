"""Review-only agent modifications to *proposed* equipment.

Never mutate an input project or released model in-place.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import yaml

from .schema import Project

COLLECTIONS = {'buses', 'feeders', 'loads', 'pv', 'batteries', 'wind'}


def propose_changes(project: Project, operations: list[dict]) -> tuple[Project, list[dict]]:
    doc = project.model_dump(mode='json')
    audit = []
    for index, op in enumerate(operations):
        action, collection = op.get('op'), op.get('collection')
        if action not in ('add', 'update', 'remove') or collection not in COLLECTIONS:
            raise ValueError(f'Patch {index}: op/collection not supported')
        objects = doc[collection]
        oid = op.get('id')
        if not isinstance(oid, str):
            raise ValueError(f'Patch {index}: id required')
        found = next((i for i, item in enumerate(objects) if item['id'] == oid), None)
        if action == 'add':
            value = op.get('value')
            if not isinstance(value, dict) or value.get('id') != oid:
                raise ValueError(f'Patch {index}: value.id must match id')
            if found is not None:
                raise ValueError(f'Patch {index}: duplicate id {oid}')
            if value.get('status') != 'proposed':
                raise ValueError(f'Patch {index}: added equipment must have status=proposed')
            objects.append(value)
            before, after = None, value
        else:
            if found is None:
                raise ValueError(f'Patch {index}: unknown {collection}/{oid}')
            old = dict(objects[found])
            if old['status'] != 'proposed':
                raise ValueError(f'Patch {index}: existing as-built equipment is immutable')
            if action == 'remove':
                objects.pop(found)
                before, after = old, None
            else:
                changes = op.get('changes')
                if not isinstance(changes, dict) or not changes:
                    raise ValueError(f'Patch {index}: nonempty changes required')
                if any(k in ('id', 'status', 'verified', 'evidence') for k in changes):
                    raise ValueError(f'Patch {index}: identifier, status, and evidence are protected')
                objects[found].update(changes)
                before, after = old, dict(objects[found])
        audit.append({'index': index, 'action': action, 'collection': collection,
                      'id': oid, 'before': before, 'after': after})
    # Model rejects dangling edges, invalid quantities, duplicates, and cycles.
    candidate = Project.model_validate(doc)
    return candidate, audit


def load_operations(path: Path) -> list[dict]:
    operations = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if not isinstance(operations, list):
        raise ValueError('Patch must be a YAML/JSON list of operations')
    return operations
