from django.conf.urls import include, url

from .views import router


urlpatterns = [
    # Django REST Framework API views
    url(r'^/', include(router.urls)),
]
