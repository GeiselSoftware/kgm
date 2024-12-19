#import ipdb
import click
import kgm
from .ksd import ksd_parser as mod_ksd_parser

class CustomHelp(click.Command):
    def format_help(self, ctx, formatter):
        # Add your custom message
        formatter.write(f"kgm version: {importlib.metadata.version('kgm')}\n")
        super().format_help(ctx, formatter)
        
@click.command(cls = CustomHelp)
@click.argument('ksd-file', required = True)
@click.argument('kgm-path', required = True)
def run_app(ksd_file, kgm_path):
    ksd_parser = mod_ksd_parser.KSDParser()
    ksd_parser.do_it(kgm_path, ksd_file)
    
def main():
    run_app()
