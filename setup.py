from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='rproxyi',
      version=version,
      description="Reverse proxy Invalidation",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/PrimarySite/rproxyi',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'requests',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
