import click
import importlib
from .config_utils import load_config
from .gencode import gencode_cs as mod_gencode_cs

class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        # Add your custom message
        formatter.write(f"kgm version: {importlib.metadata.version('kgm')}\n")
        super().format_help(ctx, formatter)    
    
    def parse_args(self, ctx, args):
        # If '-h' is in the arguments, replace it with '--help'
        if '-h' in args:
            args[args.index('-h')] = '--help'
        return super().parse_args(ctx, args)
    
@click.group(cls = CustomGroup)
@click.option("--config", "-c")
@click.pass_context
def cli(ctx, config):
    #print("cli pre-subcommand:", version, config)
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    #print(ctx.obj['config'])

@cli.command("cs", help = "C# generation")
@click.argument("kgm-path", required = True)
@click.argument("user-class-uri", required = True)
@click.argument("cs-namespace", required = True)
@click.pass_context
def gencode_cs(ctx, kgm_path, user_class_uri, cs_namespace):
    #print("gencode_cs:", ctx.obj)
    _, w_config = ctx.obj["config"]
    if 0:
        print("kgm_path:", kgm_path)
        print("user_class_uri:", user_class_uri)
        print("cs_namespace:", cs_namespace)
        
    mod_gencode_cs.gencode_cs(w_config, kgm_path, user_class_uri, cs_namespace)

def main():
    cli(max_content_width = 120)
