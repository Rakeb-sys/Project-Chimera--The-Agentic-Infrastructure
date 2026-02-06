import argparse

from specify.runner import run_specs
from specify.spec_finder import get_spec

parser = argparse.ArgumentParser()
parser.add_argument('paths', help='The files where the specs are located', nargs='+')
paths = parser.parse_args().paths

specs = [get_spec(path) for path in paths]
specs = [class_obj for class_obj in specs if class_obj is not None]

run_specs(specs)
