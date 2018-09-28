from distutils.core import setup

setup(
    name='Jicket',
    version='0.1.0',
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
