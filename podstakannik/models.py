from django.core.urlresolvers import reverse
from django.db import models
from django import forms
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
from reversion.models import Version
import reversion

from hashlib import md5

# get a list of supported markups
markups = []
def try_markup(mod_name, choice_name=None, human_readable=None):
    global markups
    if choice_name is None:
        choice_name = mod_name
    if human_readable is None:
        human_readable = choice_name.capitalize()
    try:
        __import__(mod_name)
        markups.append((choice_name, human_readable))
    except ImportError:
        pass

try_markup('markdown')

# useful decorator to turn a 'string/with///bad/form//' into a canonical url
# ('/string/with/bad/form')
def canonical_url(fn):
    def canonicalize_url(*args, **kwargs):
        url = fn(*args, **kwargs)
        url = filter(lambda s: s != '', url.split('/'))
        return '/' + '/'.join(url)
    return canonicalize_url

# model mixin for figuring out what fields have changed
class DirtyFieldsMixin(models.Model):
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name)) for f in self._meta.local_fields if not f.rel])

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])
    
    def save(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).save(*args, **kwargs)
        self._original_state = self._as_dict()

# a field for storing copyright types
class License(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    image = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name

# the biggie -- the page class
class Page(MPTTModel, DirtyFieldsMixin):
    shortname = models.CharField(max_length=40)
    forceurl = models.CharField(max_length=512, blank=True)
    # calculated!
    url = models.CharField(max_length=512, blank=True, editable=False, unique=True, db_index=True)
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    markup = models.CharField(max_length=40, choices=markups)
    license = models.ForeignKey(License)
    
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    
    body = models.TextField(blank=True)

    locationfields = ['shortname', 'forceurl', 'parent']
    contentfields = ['title', 'subtitle', 'markup', 'license', 'body']
    userfields = locationfields + contentfields
    
    def __unicode__(self):
        return self.url
    
    @property
    def created(self):
        try:
            first = Version.objects.get_for_object(self)[0]
            return first.revision.date_created
        except:
            return None
    
    @property
    def modified(self):
        try:
            latest = Version.objects.get_for_object(self).reverse()[0]
            return latest.revision.date_created
        except:
            return None
    
    @canonical_url
    def get_calculated_url(self, parent_url=None):
        if self.forceurl:
            return self.forceurl
        
        if self.parent:
            if parent_url is None:
                parent_url = self.parent.calculated_url
            return parent_url + '/' + self.shortname
        
        return self.shortname
    calculated_url = property(get_calculated_url)
    
    # used to make view urls prettier, but you should avoid it!
    @property
    def _view_url(self):
        if self.url == '/':
            return 'root'
        else:
            return self.url[1:]
    
    def get_absolute_url(self):
        best_url = self.url[1:]
        if best_url != '' and not self.is_leaf_node():
            best_url += '/'
        return reverse('podstakannik.views.page', args=(best_url,))
    
    @property
    def history_url(self):
        return reverse('podstakannik.views.history', args=(self._view_url,))
    @property
    def files_url(self):
        return reverse('podstakannik.views.list_files', args=(self._view_url,))
    @property
    def add_url(self):
        return reverse('podstakannik.views.add', args=(self._view_url,))
    @property
    def edit_url(self):
        return reverse('podstakannik.views.edit', args=(self._view_url,))
    @property
    def move_url(self):
        return reverse('podstakannik.views.move', args=(self._view_url,))
    @property
    def delete_url(self):
        return reverse('podstakannik.views.delete', args=(self._view_url,))
    
    # recalculate current url, and update recursively
    def recalculate_urls(self, parent_url=None):
        new_url = self.get_calculated_url(parent_url=parent_url)
        if new_url == self.url:
            return
        
        self.url = new_url
        
        # do recursive stuff
        for child in self.get_children():
            child.recalculate_urls(parent_url=self.url)
            child.save()
    
    def save(self, *args, **kwargs):
        # recalculate url if shortname or forceurl changes
        dirty_fields = self.get_dirty_fields()
        if 'shortname' in dirty_fields or 'forceurl' in dirty_fields:
            self.recalculate_urls()
        
        super(Page, self).save(*args, **kwargs)    
reversion.register(Page, fields=Page.userfields)

class File(DirtyFieldsMixin):
    owner = models.ForeignKey(User)
    parent = models.ForeignKey(Page)
    
    name = models.CharField(max_length=50, blank=True)
    file = models.FileField(upload_to='psk/%Y/%m/%d')
    md5 = models.CharField(max_length=32, blank=True)
    size = models.IntegerField(blank=True)
    
    userfields = ['owner', 'parent', 'name', 'file']
    
    class Meta:
        ordering = ['parent', 'name']
    
    @property
    def nice_size(self):
        # might as well be future-proof
        # binary prefixes, also!
        oom = ['bytes', 'kiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
        size = self.size
        for i, mag in enumerate(oom):
            if int(size / 1024) == 0:
                return "%i %s" % (round(size), mag)
            size /= 1024
        return "(unknown; > 1024 YiB)"
    
    def get_absolute_url(self):
        return reverse('podstakannik.views.file', args=(self.parent._view_url, self.name))
    @property
    def delete_url(self):
        return reverse('podstakannik.views.delete_file', args=(self.parent._view_url, self.name))
    
    def calculate_file_data(self):
        f = self.file
        f.open('rb')
        m = md5()
        while True:
            d = f.read(8096)
            if not d:
                break
            m.update(d)
        self.md5 = m.hexdigest()
        
        self.size = self.file.size
        if not self.name:
            self.name = self.file.name
    
    def save(self, *args, **kwargs):
        dirty_fields = self.get_dirty_fields()
        if 'file' in dirty_fields:
            self.calculate_file_data()
        super(File, self).save(*args, **kwargs)

class PageAddForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = Page.userfields
    
class PageEditForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = Page.contentfields + ['message']
        
    message = forms.CharField(max_length=200, required=False)

class PageMoveForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = filter(lambda s: s != 'parent', Page.locationfields)

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = filter(lambda s: s != 'owner' and s != 'parent', File.userfields)
