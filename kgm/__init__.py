import importlib.metadata

__version__ = importlib.metadata.version('kgm')

from .config_utils import get_config
from .database import Database
from .known_prefixes import xsd
from .rdf_terms import URI
#from .kgm_utils import get_kgm_graph
from .kgm_graph import KGMGraph



