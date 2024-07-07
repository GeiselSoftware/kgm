from mkdocs.plugins import BasePlugin

class HelloWorldPlugin(BasePlugin):
    def on_serve(self, server, config, builder):
        print("Hello, world!")
