# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name="annotate_raw_image_module",
    ext_modules=cythonize("annotate_cy.pyx", compiler_directives={'language_level': "3"}),
    include_dirs=[numpy.get_include()],
)