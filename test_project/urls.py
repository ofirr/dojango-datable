from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'index.html'}
        ),

    url(r'^authors/$',
        'test_app.views.authors_demo',
        name='authors_demo'),

    url(r'^books/$',
        'test_app.views.books_demo',
        name='books_demo'),

    url(r'^images/$',
        'test_app.views.images_demo'),

    url(r'^images/(?P<num>\d+)/$',
        'test_app.views.images_server',
        name='images_server'),

    url(r'^dojango/',
        include('dojango.urls')),

)
