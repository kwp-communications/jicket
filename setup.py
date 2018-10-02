from setuptools import setup

with open("VERSION", "r") as f:
    VERSION = f.read()

setup(
    name='jicket',
    version=VERSION,
    package_dir={'': 'jicket'},
    packages=['jicket'],
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "hashids>=1,<2",
        "jira>=2",
        "html2text"
    ],
    scripts=[
        "jicket/bin/jicket"
    ]
)
