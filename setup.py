from setuptools import setup, find_packages

setup(
    name='communator-idfm-line-reports',
    version='0.5.0',
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    install_requires=[
        'dbus-python',
        'requests',
        'sdnotify'
    ],
    entry_points={
        'console_scripts': [
            'commutator-idfm-line-reports=commutator_idfm_line_reports.main:main',
        ],
    },
    author='Guillaume Scigala',
    author_email='guillaume@scigala.fr',
    description='IDFM line reports dameon',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gscigala/commutator-idfm-line-reports',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
