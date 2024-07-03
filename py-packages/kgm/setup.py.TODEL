from setuptools import setup, find_packages

setup(name='kgm',
      version='0.0.0',
      author='Andrei Smirnov',
      author_email='asmirnov@geisel-software.com',
      license='MIT',
      description='Knowledge Graph Management',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/GeiselSoftware/KGM/py-packages/kgm',
      packages=find_packages(),
      include_package_data=True,
      package_data={'': ['examples/alice-bob/ab.ttl']},
      scripts=['bin/kgm'],
      classifiers=[
          'Programming Language :: Python :: 3.10',
          'License :: MIT License',
          'Operating System :: OS Independent',
      ],
      python_requires='>=3.10',
      install_requires = [
          'rdflib',
          'sparqlwrapper',
          'pandas'
      ],
      )
