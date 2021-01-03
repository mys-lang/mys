from setuptools import setup


with open('README.rst', 'r') as f:
    readme = f.read()


setup(
    name='${name}',
    version='${version}',
    description='${description}',
    long_description=readme,
    author=${author},
    author_email=${author_email},
    install_requires=${dependencies}
)
