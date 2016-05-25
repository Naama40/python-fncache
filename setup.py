import os
import codecs
from setuptools import setup


__version__ = '0.1'


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


install_requirements = [
    'python3-memcached'
]

test_requirements = [
    'py==1.4.31',
    'pyflakes==1.1.0',
    'pytest==2.9.1',
    'pytest-flakes==1.0.1',
    'pytest-pep8==1.0.6',
    'mock==1.0.1',
    'pep8==1.7.0',
]

setup(
    name='python-fncache',
    version=__version__,
    description='',
    long_description=read('README.md'),
    author='Carlo Smouter',
    author_email='lockwooddev@gmail.com',
    url='https://github.com/lockwooddev/python-fncache',
    install_requires=install_requirements,
    extras_require={
        'tests': test_requirements,
    },
    license='MIT',
    keywords=['celery', 'django', 'task', 'lock'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=[
        'fncache',
        'fncache.tests',
    ],
)
