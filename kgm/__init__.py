import importlib.metadata

__version__ = importlib.metadata.version('kgm')

from .config_utils import get_config
from .database import Database
from .rdf_utils import URI, xsd
from .kgm_graph import KGMGraph



