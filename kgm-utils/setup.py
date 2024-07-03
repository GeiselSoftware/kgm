from setuptools import setup, find_packages

setup(
        name='kgm-utils',
        version='0.0.0',
        author='Andrei Smirnov',
        author_email='asmirnov@geisel-software.com',
        description='Knowledge Graph Management - utility commands and library',
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        url='https://github.com/GeiselSoftware/KGM',  # Replace with your repository URL
        packages=find_packages(),
        include_package_data=True,
        package_data={
                    'kgm_utils': ['examples/*/*.ttl'],  # Adjust the pattern to match your data files
                },
        scripts=['bin/kgm'],
        classifiers=[
                    'Programming Language :: Python :: 3.10',
                    'License :: MIT License',
                    'Operating System :: OS Independent',
                ],
        python_requires='>=3.10',
        install_requires = [
            'scripts',
            'rdflib',
            'sparqlwrapper',
            'pandas'
        ],
    )
