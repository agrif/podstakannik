Podsatkannik!
=============

<https://github.com/agrif/podstakannik>

Podstakannik is replacement for the default Django flatpages, in that
it is designed to serve static content at specific urls.

Unlike flatpages, however, podstakannik is hierarchical. Each page has
a well-defined parent, as well as next and previous siblings.
Podstakannik is also wiki-like: it stores a complete edit
history. Also unlike flatpages, podstakannik has a mechanism for
attatching uploaded files to a particular page.

Each page is written in [markdown][], though there is stub code for
other languages and this may be extended in the future. Additionally,
page sources can use special tags that expand into a hierarchical list
of pages, or a list of files attatched to that page that match a
certain pattern, and a few others.

 [markdown]: http://daringfireball.net/projects/markdown/

**Right now this is extremely untested and undocumented code. I use it
on my own sites, but YMMV.**

Install
-------

To run podstakannik, you will need to install the following:

 * [django-mptt](https://github.com/django-mptt/django-mptt/)
 * [django-reversion](https://github.com/etianen/django-reversion)
 * [python-markdown](http://www.freewisdom.org/projects/python-markdown/)

For django-mptt, you will need at least version 0.5.x, which at the
time of this writing means checking out and installing the version
from github. For the others, anything recent should work.

I also tend to run all my output through [typogrify][] to give my
pages some fancier typographical rules. This is completely optional!
 
 [typogrify]: http://code.google.com/p/typogrify/

You can install podstakannik on your system by running

    python setup.py install

as root. You can also use podstakannik in-place by messing with your
python path! Once installed, you can add podstakannik to your Django
site by adding the following lines to `INSTALLED_APPS`:

~~~~{.py}
# in settings.py
INSTALLED_APPS = (
    ...
	
	'mptt',
    'reversion',
	'typogrify',  # again, COMPLETELY OPTIONAL
    'podstakannik',
)
~~~~

Podstakannik uses slashes in URLs to indicate that a page also has child pages. In order to control slashes this way, you must set `APPEND_SLASH` to `False`:

~~~~{.py}
# in settings.py
APPEND_SLASH = False
~~~~

To allow access to podstakannik pages, add the following to your `urls.py`:

~~~~{.py}
# in urls.py
urlpatterns = patterns('',
    ...
	
	url(r'^', include('podstakannik.urls')),
	# if you want to serve pages in a subdirectory instead, use:
	# url(r'^some/path/', include('podstakannik.urls')),
)
~~~~

Finally, to add tables to your database and add a root page, run

    python manage.py syncdb
	python manage.py loaddata psk_install
	python manage.py createinitialrevisions

Podstakannik is now installed! It will use default templates for now,
but you can use the templates in `podstakannik/templates/` as a
reference for writing your own.

Special Markup
--------------

In addition to the default Markdown, podstakannk has extra markup for
adding dynamic information about files and pages.

 * `[[PAGETREE: (path)]]` -- prints out a sitemap-like tree of pages,
   with the given url as the root. If `path` is omitted, uses the
   current page.
   
 * `[[PAGELIST: page:(path) (fmt)]]` -- prints out the `fmt` string
   once for every child `path` has. In the format string, `{title}`,
   `{subtitle}`, and `{url}` are replaced. If `path` is omitted, the
   current page is used.
   
 * `[[FILELIST: page:(path) glob:(glob) (fmt)]]` -- prints out the
   `fmt` string once for every file `path` has. In the format string,
   `{url}`, `{name}`, `{md5}`, `{size}`, and `{user}` are replaced. If
   `path` is omitted, the current page is used. If `glob` is present,
   only files matching this are printed.
   
 * `[[FILE: (name)]]`, `[[FILESIZE: (name)]]`, and
   `[[FILEMD5: (name)]]` -- replaces with the url, size, and hex md5
   hash of the named file, respectively.

Customizing Alternate Formats
-----------------------------

Podstakannik is able to serve the same page in different formats based
on the file extension used in the URL. If the url ends in `.txt`, for
example, podstakannik will use the `podstakannik/page.txt` template to
format the output. By default, only the `.html` and `.txt` extensions
are recognized, but you can change this with a few settings.

Here's the default settings:

~~~~{.py}
# in settings.py

# map from url extension to (human_readable_name, mime_type)
PODSTAKANNIK_EXTENSIONS = {
    'html' : ('xhtml', 'application/xhtml+xml'),
    'txt' : ('txt', 'text/plain'),
}
PODSTAKANNIK_DEFAULT_EXTENSION = 'html'
~~~~

About the Name
--------------

A [podstakannik][] is a tea glass holder used for very hot tea; this
is very much like a [zarf][], which is instead used to hold a coffee
cup.

 [podstakannik]: http://en.wikipedia.org/wiki/Podstakannik
 [zarf]: http://en.wikipedia.org/wiki/Zarf

"Zarf" is also the nickname of [an important figure][plotkin] in the
interactive fiction community with a
[simple but interesting website][zarfhome]. It's a collection of flat
pages, arranged ([almost][DAG]) hierarchically. Each page has a link
to its parent, its children, and occasionally related pages. Spending
time on that site is like browsing Wikipedia, because you always end
up somewhere unexpected.

 [plotkin]: http://en.wikipedia.org/wiki/Andrew_Plotkin
 [zarfhome]: http://www.eblong.com/zarf/home.html
 [DAG]: http://en.wikipedia.org/wiki/Directed_acyclic_graph
 
 Podstakannik started life as an offline website compiler for
 generating all the relationship links needed for such a site, and I
 used it to maintain [my website][]. This worked well, but it was
 pretty inflexible and not very portable. When I started needing
 something like it for other sites, I decided to re-implement it as a
 django app.
 
  [my website]: http://gamma-level.com/
  
