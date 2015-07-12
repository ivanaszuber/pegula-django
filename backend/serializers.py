import logging
from backend.models import Employee

log = logging.getLogger(__name__)

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.authtoken.models import Token

from .models import *

__all__ = 'ClientSerializer', 'UserFullSerializer', 'UserRestrictedSerializer', 'EmployeeFullSerializer'


#
# Authentication
#

class AuthTokenSerializer(serializers.ModelSerializer):
    """
    Custom serializer for Django REST Auth's Token model.

    Uses `token` response attribute rather than the default `key`.
    """

    token = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('token',)

    def get_token(self, o):
        return o.key


class RestAuthLoginSerializer(serializers.Serializer):
    """
    Login submission de-serializer and validator for Django REST Auth.

    Requires `email` and `password` POST params.
    """
    # Custom implementation since the default uses hardcoded `username`
    #
    # See: rest_auth.serializers.TokenSerializer and rest_framework.authtoken.serializers.AuthTokenSerializer

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        read_only_fields = ('created', 'modified')
        # depth = 1


#
# Users
#


class UserFullSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects)
    roles = serializers.SlugRelatedField(source='groups', slug_field='name', queryset=Group.objects,
                                         many=True, required=False,
                                         help_text='List of potential roles:  ' + ', '.join(UserRoles.valid_types))

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'password', 'client', 'phone', 'roles', 'status', 'first_name', 'last_name', 'created', 'modified')
        read_only_fields = ('created', 'modified')
        write_only_fields = ('password',)

    @transaction.atomic
    def create(self, validated_data):
        # we must call Django's special `set_password()` method so we persist the hashed
        # version rather than plaintext password
        groups = validated_data.pop('groups', None)
        try:
            user = User(**validated_data)
        except TypeError as e:
            raise serializers.ValidationError(e)
        user.set_password(validated_data['password'])
        user.save()
        if groups:
            [user.groups.add(group) for group in groups]
        return user


class UserRestrictedSerializer(UserFullSerializer):
    """Restricted serializer for updates, since some fields are untouchable"""

    class Meta(UserFullSerializer.Meta):
        fields = ('email', 'client', 'phone', 'roles', 'status', 'first_name', 'last_name', 'created',
                  'modified')  # excludes: password
        read_only_fields = ('email', 'client', 'created', 'modified')


class EmployeeFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        read_only_fields = ('created', 'modified')
