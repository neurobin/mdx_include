# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import codecs
from setuptools import setup
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('mdx_include/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

def get_readme(filename):
    if not os.path.exists(filename):
        return ""

    with codecs.open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as readme:
        content = readme.read()
    return content

setup(name="mdx_include",
      version=main_ns['__version__'],
      author="Md. Jahidul Hamid",
      author_email="jahidulhamid@yahoo.com",
      description="Python Markdown extension to include local or remote files",
      license="BSD",
      keywords="markdown include local remote file",
      url="https://github.com/neurobin/mdx_include",
      packages=["mdx_include"],
      long_description=get_readme("README.md"),
      long_description_content_type="text/markdown",
      classifiers=[
        # See: https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
      ],
      install_requires=["Markdown>=2.6",],
test_suite="mdx_include.test.test")
