from distutils.core import setup

setup(name="podstakannik",
      version="0.0.1",
      description="a hierarchical, pseudo-wiki flatpages replacement for django",
      author="Aaron Griffith",
      author_email="aargri@gmail.com",
      
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
