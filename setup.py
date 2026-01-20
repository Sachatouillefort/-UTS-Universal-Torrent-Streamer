from setuptools import setup, find_packages

setup(
    name="pirate-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rich",
        "questionary",
        "ddgs",
        "subliminal",
        "cinemagoer",
    ],
    entry_points={
        'console_scripts': [
            'pirate-cli=cli.pirate-cli:main',
        ],
    },
    author="Sacha",
    description="Une CLI pour rechercher et télécharger des torrents",
    python_requires='>=3.8',
)
