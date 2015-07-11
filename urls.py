from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='frontpage.html'), name='home'),

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),

    # Django web-based auth views (login, logout, password change/reset)
    url('^', include('django.contrib.auth.urls')),

    # REST Auth
    # http://django-rest-auth.readthedocs.org/en/latest/api_endpoints.html
    url(r'^api/rest-auth/', include('rest_auth.urls')),

    # Django REST Framework API browser auth views, for dev/test only
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Swagger API docs for REST Framework
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # Django REST Framework API views
    url(r'^api/v1', include('backend.urls', namespace='auth')),
]
