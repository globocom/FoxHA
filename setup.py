from setuptools import setup, find_packages
import foxha

REQUIREMENTS_FILE = 'requirements.txt'


def parse_requirements():
    return [req[:-1] for req in open(REQUIREMENTS_FILE, 'r').readlines()]


setup(
    name="foxha",
    version=foxha.__version__,
    packages=find_packages(),
    author="Rafael Dantas Silva",
    author_email="rafael.dantas@corp.globo.com",
    description="A MySQL High Availability tool to replace flipper",
    license="GPL",
    keywords="tool mysql",
    url="https://github.com/globocom/foxha/",
    long_description="A MySQL High Availability tool to replace flipper",
    install_requires=parse_requirements(),

    extras_require={
        'dev': [],
        'test': [],
    },

    entry_points={
        'console_scripts': [
            'fox = foxha.fox:main',
            'fox_crypt = foxha.crypt:main',
        ],
    },

)
