from distutils.core import setup

import podstakannik

setup(name="podstakannik",
      version=podstakannik.__version__,
      description="a hierarchical, pseudo-wiki flatpages replacement for django",
      author=podstakannik.__author__,
      author_email=podstakannik.__contact__,
      
      packages=['podstakannik', 'podstakannik.templatetags'],
      package_data = {'podstakannik' : ['fixtures/*.json', 'templates/podstakannik/*']},
      
      classifiers=["Development Status :: 3 - Alpha",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django",
      ])
