from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.in') as f:
    install_requires = f.read().split()

version = {}
with open("mic/version.py") as fp:
    exec(fp.read(), version)
__version__ = version['__version__']
setup(
    name='mic',
    version=__version__,
    description='MIC (Microscopy Illumination Correction) is a Python tool for correcting the illumination of 3D '
                'microscopy image stacks based on pre-computed flat and dark field models, '
                'e.g. obtained via CIDRE\'s retrospective method (Smith et al., 2014). ',
    long_description_content_type="text/markdown",
    author='Michele Sorelli',
    author_email='sorelli@lens.unifi.it',
    url='https://github.com/lens-biophotonics/mic',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    # What does your project relate to?
    keywords='illumination correction, 3D microscopy',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_requires,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [
            'pip-tools',
        ],
        'doc': [
            'm2r2==0.3.2',
            'sphinx',
            'sphinx_rtd_theme',
        ],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'mic = mic.__main__:main',
        ],

    },
)
