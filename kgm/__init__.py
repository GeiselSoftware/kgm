import importlib.metadata

__version__ = importlib.metadata.version('kgm')

import nanoid

def gen_nanoid():
    return nanoid.generate("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 20)

from .config_utils import get_config
from .database import Database
from .rdf_terms import URI
from .kgm_graph import KGMGraph



