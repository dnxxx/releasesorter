from distutils.core import setup

setup(
    name='releasesorter',
    version='0.1.0',
    description='Release sorter',

    packages=['releasesorter'],
    scripts=['bin/releasesorter'],

    author='dnxxx',
    author_email='dnx@fbi-security.net',
    license='BSD',

    install_requires=[
        'ago',
        'unipath',
        'argh',
    ]
)
