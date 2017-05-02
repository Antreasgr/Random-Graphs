import os
import yaml
from yaml import Loader, Dumper


path = "Results"
files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
with open(files[0], 'r') as stream:
    data_loaded = yaml.load(stream, Loader=Loader)
print(data_loaded)