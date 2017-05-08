import os
import yaml
from yaml import Loader, Dumper
from clique_tree import *

path = "Results/SHET"
files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
for f in files:
    with open(f, 'r') as stream:
        data_loaded = yaml.load(stream, Loader=Loader)
    print(data_loaded)


# with open("test.yml", 'w') as stream:
#     yaml.dump(Run(), stream, Dumper=Dumper)


