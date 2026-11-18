from pathlib import Path
import pytest
from opengrid.io import load_project

EXAMPLE = Path(__file__).parents[1] / 'examples' / 'sample-building.yaml'

@pytest.fixture
def example():
    return load_project(EXAMPLE)
