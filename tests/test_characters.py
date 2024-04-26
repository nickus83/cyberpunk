import sys
sys.path.append('../')
from character_create import *
# from ..character_create import Fixer, Media, Exec, Rockerboy, Solo
# from ..character_create import Netrunner, Tech, Medtech, Lawmen, Nomad

# import pytest
import yaml
from pathlib import Path

def test_character():
    tables_path = Path(Path(__file__).parent, '../data/tables.yaml').resolve()
    with open(tables_path) as fo:
        tables = yaml.safe_load(fo)

    for role in tables['roles']:
        role_class = globals()[role.capitalize()]
        name = None
        char = role_class(name, role, 'male', tables)

        print(char)

if __name__ == '__main__':
    test_character()