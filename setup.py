from setuptools import setup

try:
    with open("README.md") as rfile:
        long_description = rfile.read()
except:
    long_description = "https://github.com/dragdev-studios/postbin (description failed to load)"

setup(
    name='PostBin',
    version='1.2.0',
    packages=['postbin', "postbin.v2"],
    url='https://github.com/dragdev-studios/postbin',
    python_requires=">=3.6",
    license='MIT',
    author='EEKIM10',
    author_email='eek@clicksminuteper.net',
    description='A simple two-function program that POSTs to hastebin',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    extras_require={"cli": "webbrowser"}
)
#
