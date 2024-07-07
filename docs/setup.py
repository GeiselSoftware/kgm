from setuptools import setup, find_packages

setup(
    name="mkdocs-hello-world-plugin",
    version="0.1",
    description="A simple hello world plugin for MkDocs",
    py_modules=["hello_extension"],
    install_requires=["mkdocs"],
    entry_points={
        "mkdocs.plugins": [
            "hello-world = hello_extension:HelloWorldPlugin",
        ]
    },
)
