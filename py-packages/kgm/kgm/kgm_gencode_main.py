import click
from .config_utils import load_config

from .gencode import gencode_cs as mod_gencode_cs

class CustomGroup(click.Group):
    def parse_args(self, ctx, args):
        # If '-h' is in the arguments, replace it with '--help'
        if '-h' in args:
            args[args.index('-h')] = '--help'
        return super().parse_args(ctx, args)
    
@click.group(cls = CustomGroup)
@click.option("--version", "-V", is_flag = True)
@click.option("--config", "-c")
@click.pass_context
def cli(ctx, version, config):
    print("cli pre-subcommand:", version, config)
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    print(ctx.obj['config'])

@cli.command("cs", help = "C# generation")
@click.argument("user-class-uri", required = True)
@click.pass_context
def gencode_cs(ctx, user_class_uri):
    print("gencode_cs:", ctx.obj)
    _, w_config = ctx.obj["config"]
    mod_gencode_cs.gencode_cs(w_config, user_class_uri)

def main():
    cli(max_content_width = 120)
