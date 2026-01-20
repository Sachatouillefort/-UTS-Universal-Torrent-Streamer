from setuptools import setup, find_packages

setup(
    name="torrent-search-cli",
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
            'torrent-search-cli=cli.pirate-cli:main',
        ],
    },
    author="Sacha",
    description="CLI for torrent search and management",
    python_requires='>=3.8',
    license="MIT",
)
