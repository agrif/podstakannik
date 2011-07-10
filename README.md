Podsatkannik!
=============

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

To run podstakannik, you will need to install the following:

 * [django-mptt](https://github.com/django-mptt/django-mptt/)
 * [django-reversion](https://github.com/etianen/django-reversion)
 * [python-markdown](http://www.freewisdom.org/projects/python-markdown/)

I also tend to run all my output through [typogrify][] to give my
pages some fancier typographical rules.
 
 [typogrify]: http://code.google.com/p/typogrify/

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
  
