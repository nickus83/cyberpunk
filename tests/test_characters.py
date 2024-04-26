from ..character_create import Fixer, Media, Exec, Rockerboy, Solo
from ..character_create import Netrunner, Tech, Medtech, Lawmen, Nomad

import pytest
import yaml
from pathlib import Path

def test_character():
    tables = yaml.safe_load(Path(__file__).parent.resolve() / 'data/tables.yaml')
    for role in tables['roles']:
        print(role)

if __name__ == '__main__':
    test_character()