"""Setup script for data_toolchest package."""

import sys

from setuptools import setup, find_packages


if sys.version_info[:2] < (3, 8):
    sys.exit('Sorry, Python 3.8 or newer is required.')


install_requires = [
    'setuptools_scm'
]


tests_require = [
    'coverage',
    'flake8',
    'flake8-bugbear',
    'flake8-builtins',
    'flake8-comprehensions',
    'flake8-blind-except',
    'flake8-docstrings',
    'flake8-mutable',
    'flake8-rst-docstrings',
    'mypy',
    'pyflakes',
    'pytest',
    'pytest-cache',
    'pytest-cov',
    'pytest-flake8',
    'pytest-html',
    'pytest-mypy',
    'pytest-xdist',
    'Sphinx',
    'sphinx-argparse',
    'sphinx-rtd-theme',
]


if __name__ == '__main__':
    setup(
        name='data_toolchest-Larry_Clos',
        version='0.1.0',
        description='Package with some simple tools for retrieving/parsing/handling data.',
        author='Larry Clos',
        author_email='drlclos@gmail.com',
        license='Open',
        classifiers=[
            'License :: Other/Proprietary License',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent'
        ],
        # zip_safe=False,
        packages=find_packages(),
        # include_package_data=True,
        # use_scm_version=True,
        install_requires=install_requires,
        tests_require=tests_require,
        entry_points={},
        python_requires='>=3.8'
    )
