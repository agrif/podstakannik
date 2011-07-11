import re
from django import template
from ..models import Page, File
from fnmatch import fnmatch

try:
    import markdown
except ImportError:
    markdown = None

def markdown_page_tree(p, indent=0):
    ret = "    " * indent
    
    if p.subtitle:
        ret += " * [%s](%s) - %s\n" % (p.title, p.get_absolute_url(), p.subtitle)
    else:
         ret += " * [%s](%s)\n" % (p.title, p.get_absolute_url())       
         
    for child in p.get_children():
        ret += markdown_page_tree(child, indent + 1)
    
    return ret

def page_list(p, fmt):
    s = ""
    for child in p.get_children():
        data = {}
        data['title'] = child.title
        data['subtitle'] = child.subtitle
        data['url'] = child.get_absolute_url()
        s += fmt.format(**data) + "\n"
    return s

def file_list(p, glob, fmt):
    s = ""
    for f in p.file_set.all():
        if glob and not fnmatch(f.name, glob):
            continue
        data = {}
        data['url'] = f.get_absolute_url()
        data['name'] = f.name
        data['md5'] = f.md5
        data['size'] = f.nice_size
        data['user'] = f.owner
        s += fmt.format(**data) + "\n"
    return s

# match rules used in psk
# format: (compiled_re, typelist, functiondict)
#
# typelist is a list of strings, which are indexes into convert (see below)
#
# functiondict is a mapping of fmt names into functions, which should
# accept the same number of arguments as there are match groups, and should
# return a string used to replace the whole match
rules = [
    (re.compile(r"\[\[PAGETREE:? *(.*)\]\]"),
     ('page',), {
            'markdown' : markdown_page_tree,
    }),
    (re.compile(r"\[\[PAGELIST:? *(?:page:([^ ]*) +)?(.*)\]\]"),
     ('page', 'string'), {'all' : page_list}),
    (re.compile(r"\[\[FILELIST:? *(?:page:([^ ]*) +)?(?:glob:([^ ]*) +)?(.*)\]\]"),
     ('page', 'string', 'string'), {'all' : file_list}),
    
    (re.compile(r"\[\[FILEMD5:? *(.*)\]\]"),
     ('file',), {'all' : lambda f: f.md5}),
    (re.compile(r"\[\[FILESIZE:? *(.*)\]\]"),
     ('file',), {'all' : lambda f: f.nice_size}),
    (re.compile(r"\[\[FILE:? *(.*)\]\]"),
     ('file',), {'all' : lambda f: f.get_absolute_url()}),
]

# functions for turning a regex match into a useful object
# given the page and the match string
def convert_page(p, s):
    if s:
        return Page.objects.get(url=s)
    return p
def convert_file(p, s):
    if " " in s:
        url, name = s.split(" ", 1)
    else:
        url = p.url
        name = s
    return File.objects.get(parent__url=url, name=name)
convert = {
    'string' : lambda p, s: s if (not s is None) else '',
    'page' : convert_page,
    'file' : convert_file,
}

# functions for doing the final conversion, by fmt name
final = {
    # FIXME make extensions configurable
    'markdown' : lambda s: markdown.markdown(s, ['extra', 'toc', 'codehilite']),
}

register = template.Library()

@register.filter
def psk_text(value, p):
    fmt = p.markup
    s = str(value)
    
    for regex, types, fnmap in rules:
        def sub_repl(m):
            args = []
            for i, typ in enumerate(types):
                typ = convert.get(typ, lambda s: str(s))
                val = m.group(i + 1)
                try:
                    args.append(typ(p, val))
                except:
                    return ''
            rule = fnmap.get(fmt, fnmap.get('all', None))
            if rule is None:
                return ''
            try:
                return rule(*args)
            except:
                return ''
        s = regex.sub(sub_repl, s)
    
    return s

@register.filter
def psk(value, p):
    fmt = p.markup
    value = psk_text(value, p)
    if fmt in final:
        try:
            return final[fmt](value)
        except:
            pass
    return value
