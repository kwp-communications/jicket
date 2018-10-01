from distutils.core import setup

with open("VERSION", "r") as f:
    VERSION = f.read()

setup(
    name='Jicket',
    version=VERSION,
    package_dir={'': 'jicket'},
    packages=['jicket'],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires=[
        "hashids>=1,<2",
        "jira>=2",
        "html2text"
    ],
    scripts=[
        "jicket/bin/jicket"
    ]
)
