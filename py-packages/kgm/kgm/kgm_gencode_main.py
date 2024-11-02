from .kgm_utils import *
from .gencode import gencode_cs

def main():
    print("Hello, world!", get_kgm_graph_class_uri())
    gencode_cs.gencode_cs()

