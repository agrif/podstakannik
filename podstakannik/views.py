from models import Page, PageAddForm, PageEditForm, PageMoveForm, File, FileForm
from reversion.models import Version
import reversion
from mptt.forms import MoveNodeForm
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.conf import settings

# map from ext to (name, mime)
default_extensions = {
    'html' : ('html', 'text/html'),
    'txt' : ('txt', 'text/plain'),
}
default_extension = 'html'

def canonicalize_url(url, def_ext=''):
    url = url.split('/')
    ext = def_ext
    for i, part in enumerate(url):
        if '.' in part:
            part, ext = part.rsplit('.', 1)
            url[i] = part
    url = filter(lambda s: s != '', url)
    url = '/' + '/'.join(url)
    
    # special case
    if url == '/root':
        url = '/'
    
    return url, ext

def page(request, url):
    def_ext = getattr(settings, 'PODSTAKANNIK_DEFAULT_EXTENSION', default_extension)
    extensions = getattr(settings, 'PODSTAKANNIK_EXTENSIONS', default_extensions)
    old_url = url
    url, ext = canonicalize_url(url, def_ext)
    if not ext in extensions:
        raise Http404
    
    if 'revision' in request.GET:
        try:
            revision = int(request.GET['revision'])
        except:
            raise Http404
        
        ver = get_object_or_404(Version, revision=revision)
        p = ver.get_object_version().object
    else:
        p = get_object_or_404(Page, url=url)
    
    if ext == def_ext:
        best_url = p.get_absolute_url()
    else:
        best_url = p.get_absolute_url(ext=ext)
    if 'revision' in request.GET:
        best_url += "?revision=%s" % (str(request.GET['revision']),)
    
    if p.is_leaf_node():
        if old_url.endswith('/'):
            return HttpResponseRedirect(best_url)
    else:
        if old_url != '' and not old_url.endswith('/'):
            return HttpResponseRedirect(best_url)
    
    extmap = []
    for other_ext in extensions:
        element = {}
        element['current'] = (other_ext == ext)
        element['name'] = extensions[other_ext][0]
        if other_ext == def_ext:
            element['url'] = p.get_absolute_url()
        else:
            element['url'] = p.get_absolute_url(ext=other_ext)
        extmap.append(element)
    
    mime = extensions[ext][1]
    
    return render(request, 'podstakannik/page.' + ext, {'page' : p, 'alternates' : extmap}, content_type=mime)

@reversion.create_revision
def edit_or_add(request, url, add=False):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    verb = 'add' if add else 'edit'
    preview = None
    
    if request.method == 'POST':
        if add:
            form = PageAddForm(request.POST)
        else:
            form = PageEditForm(request.POST, instance=p)
        if form.is_valid():
            if 'preview' in request.POST:
                preview = form.cleaned_data['body']
            else:
                # save the valid data
                reversion.revision.comment = 'Initial version.' if add else form.cleaned_data['message']
                reversion.revision.user = request.user
                p = form.save()
                return HttpResponseRedirect(p.get_absolute_url())
    else:
        if add:
            form = PageAddForm(initial={'markup' : p.markup, 'license' : p.license.id, 'parent' : p.id})
        else:
            form = PageEditForm(instance=p)
    
    return render(request, 'podstakannik/edit.html', {'form' : form, 'page' : p, 'preview' : preview, 'verb' : verb})

@permission_required('podstakannik.change_page')
def edit(request, url):
    return edit_or_add(request, url, False)

@permission_required('podstakannik.add_page')
def add(request, url):
    return edit_or_add(request, url, True)

@permission_required('podstakannik.add_page')
@permission_required('podstakannik.delete_page')
@reversion.create_revision
def move(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    
    if request.method == 'POST':
        node_form = MoveNodeForm(p, request.POST)
        if node_form.is_valid():
            old_url = p.url
            p = node_form.save()
            url_form = PageMoveForm(request.POST, instance=p)
            if url_form.is_valid():
                p = url_form.save()
                new_url = p.calculated_url
                if old_url != new_url:
                    message = "Moved from '%s' to '%s'." % (old_url, p.calculated_url)
                else:
                    message = "Moved without changing url."
                reversion.revision.comment = message
                reversion.revision.user = request.user
                
                return HttpResponseRedirect(p.get_absolute_url())
        else:
            url_form = PageMoveForm(request.POST, instance=p)
    else:
        url_form = PageMoveForm(instance=p)
        node_form = MoveNodeForm(p)
    
    return render(request, 'podstakannik/move.html', {'url_form' : url_form, 'node_form' : node_form, 'page' : p})

@permission_required('podstakannik.delete_page')
def delete(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    
    if request.method == 'POST':
        parent = p.parent
        p.delete()
        if parent:
            return HttpResponseRedirect(parent.get_absolute_url())
        return HttpResponseRedirect('/')

    return render(request, 'podstakannik/delete.html', {'page' : p})

def history(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    
    history = Version.objects.get_for_object(p).reverse()
    
    return render(request, 'podstakannik/history.html', {'page' : p, 'history' : history})

###################

def list_files(request, url):
    url, _ = canonicalize_url(url)
    p = get_object_or_404(Page, url=url)
    
    if request.method == 'POST' and request.user.has_perm('podstakannik.add_file'):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            m = form.save(commit=False)
            m.owner = request.user
            m.parent = p
            m.save()
            return HttpResponseRedirect(p.files_url)
    else:
        form = FileForm()
    
    files = p.file_set.all()
    return render(request, 'podstakannik/list_files.html', {'page' : p, 'files' : files, 'form' : form})

def file(request, url, name):
    url, _ = canonicalize_url(url)
    f = get_object_or_404(File, name=name, parent__url=url)
    
    return HttpResponseRedirect(f.file.url)

@permission_required('podstakannik.delete_file')
def delete_file(request, url, name):
    url, _ = canonicalize_url(url)
    f = get_object_or_404(File, name=name, parent__url=url)
    
    if request.method == 'POST':
        parent = f.parent
        f.delete()
        return HttpResponseRedirect(parent.files_url)

    return render(request, 'podstakannik/delete.html', {'page' : f.parent, 'file' : f})
