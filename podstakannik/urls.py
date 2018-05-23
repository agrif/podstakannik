from django.conf.urls import url
from views import list_files, delete_file, file, add, edit, move, delete, history, page

urlpatterns = [
                       url(r'^(?P<url>.*).files$', list_files, name='podstakannik.views.list_files'),
                       url(r'^(?P<url>.*)/files/(?P<name>.*)/delete$', delete_file, name='podstakannik.views.delete_file'),
                       url(r'^(?P<url>.*)/files/(?P<name>.*)$', file, name='podstakannik.views.file'),
                       
                       url(r'^(?P<url>.*)/add$', add, name='podstakannik.views.add'),
                       url(r'^(?P<url>.*)/edit$', edit, name='podstakannik.views.edit'),
                       url(r'^(?P<url>.*)/move$', move, name='podstakannik.views.move'),
                       url(r'^(?P<url>.*)/delete$', delete, name='podstakannik.views.delete'),
                       url(r'^(?P<url>.*).history$', history, name='podstakannik.views.history'),
                       
                       url(r'^(?P<url>.*)$', page, name='podstakannik.views.page'),
]
