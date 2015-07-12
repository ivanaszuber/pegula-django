import logging

from django.http.response import Http404

from rest_framework import viewsets
from rest_framework import routers
from rest_framework.decorators import detail_route
from rest_framework.response import Response as RestResponse
from rest_framework.filters import SearchFilter
from backend.models import Employee
from backend.serializers import EmployeeFullSerializer

from .models import *
from .serializers import *


__all__ = 'frontpage', 'router'

log = logging.getLogger(__name__)


# RESTful Web Service Endpoints

class ClientView(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'org_id'

    @detail_route(permission_classes=[])
    def users(self, req, org_id):
        """Retrieve a list of Users which belong to the specified Organization"""
        org_users = User.org_users.for_org(org_id).order_by('email')
        serializer = UserFullSerializer(org_users, many=True)
        return RestResponse(serializer.data)


class UserView(viewsets.ModelViewSet):
    """Basic service for creating and updating Users

    ---
    list:
      parameters:
        - name: search
          paramType: query
          description: Optional search query, performs substring match on `email`, `first_name`, and `last_name`
        - name: status
          paramType: query
          description: Optional filter, value must be `active` or `deactivated`
    """
    queryset = User.objects.all()
    serializer_class = UserFullSerializer
    lookup_field = 'email'
    lookup_value_regex = '[^@]+@[^@]+\.[^@]+'  # DRF DefaultRouter regex splits on '.' character, so we must supply custom URL regex for email

    filter_backends = (SearchFilter,)
    search_fields = ('email', 'first_name', 'last_name')

    def get_serializer_class(self):
        # We route between serializers to ensure that "updates" can't change username, org, password
        if self.request.method in ('GET', 'POST'):
            return UserFullSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return UserRestrictedSerializer
        return self.serializer_class

    def get_queryset(self):
        # We use this strategy for rather than `rest_framework.filters.DjangoFilterBackend` so
        # that we can _also_ use `SearchFilter`. There may be some better way to use them in tandem.
        queryset = self.queryset
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_destroy(self, user):
        # hook into HTTP DELETE verb such that we mark status=deactivated
        # override the `destroy()` method if we need full control over HTTP response, etc.
        user.deactivate()
        user.save()


class EmployeeView(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeFullSerializer
    lookup_field = 'email'
    lookup_value_regex = '[^@]+@[^@]+\.[^@]+'  # DRF DefaultRouter regex splits on '.' character, so we must supply custom URL regex for email

    filter_backends = (SearchFilter,)
    search_fields = ('email', 'first_name', 'last_name')

    def get_serializer_class(self):
        # We route between serializers to ensure that "updates" can't change username, org, password
        if self.request.method in ('GET', 'POST', 'PUT', 'PATCH'):
            return EmployeeFullSerializer
        return self.serializer_class

    def get_queryset(self):
        # We use this strategy for rather than `rest_framework.filters.DjangoFilterBackend` so
        # that we can _also_ use `SearchFilter`. There may be some better way to use them in tandem.
        queryset = self.queryset
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_destroy(self, user):
        # hook into HTTP DELETE verb such that we mark status=deactivated
        # override the `destroy()` method if we need full control over HTTP response, etc.
        user.deactivate()
        user.save()


class RolesViewSet(viewsets.ViewSet):
    lookup_field = 'org_type'

    def list(self, req):
        """Retrieve a mapping of org_type->role_choices"""
        return RestResponse(UserRoles.by_org)

    def retrieve(self, req, org_type):
        """Retrive a list of Role choices for a specified `org_type`"""
        if not org_type or org_type not in UserRoles.by_org:
            raise Http404()
        return RestResponse(UserRoles.by_org[org_type])


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'clients', ClientView, 'clients')
router.register(r'users', UserView, 'users')
router.register(r'roles', RolesViewSet, 'roles')
router.register(r'employees', EmployeeView, 'employees')
