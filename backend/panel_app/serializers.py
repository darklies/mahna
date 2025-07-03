from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
import random
import string

from .models import Config, Server, Tutorial, Announcement
from .xui_clients import PanelType # For panel_type choices in ServerSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_support_staff', 'password')
        read_only_fields = ('id', 'is_staff')

    def create(self, validated_data):
        if not validated_data.get('username'):
            raise serializers.ValidationError({"username": "This field is required."})
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True, style={'input_type': 'password'}, min_length=8)
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_support_staff', 'password', 'generated_password')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_phone_number(self, value):
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with that phone number already exists.")
        return value

    def create(self, validated_data):
        generated_password_plain = None
        if validated_data.get('password'):
            generated_password_plain = validated_data.get('password')
            validated_data['password'] = make_password(validated_data.pop('password'))
        else:
            generated_password_plain = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            validated_data['password'] = make_password(generated_password_plain)

        validated_data.pop('generated_password', None)
        user = User.objects.create(**validated_data)
        user.generated_password = generated_password_plain
        return user


class SupportUserSerializer(serializers.ModelSerializer):
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'generated_password')

    def create(self, validated_data):
        password_plain = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        if not validated_data.get('username'):
            raise serializers.ValidationError({"username": "Username is required."})

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            is_support_staff=True,
            password=make_password(password_plain)
        )
        user.generated_password = password_plain
        return user

# --- Serializers for Profile Section ---

class ServerLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'name', 'panel_type')


class ConfigSerializer(serializers.ModelSerializer):
    server = ServerLiteSerializer(read_only=True)
    live_total_gb = serializers.FloatField(read_only=True, allow_null=True)
    live_up_gb = serializers.FloatField(read_only=True, allow_null=True)
    live_down_gb = serializers.FloatField(read_only=True, allow_null=True)
    live_expiry_time = serializers.DateTimeField(read_only=True, allow_null=True)
    live_enable_status = serializers.BooleanField(read_only=True, allow_null=True)

    class Meta:
        model = Config
        fields = [
            'id', 'user', 'server', 'client_identifier', 'remark', 'protocol', 'port',
            'qr_code_link', 'subscription_link', 'raw_config_link',
            'total_gb', 'up_gb', 'down_gb', 'expiry_time', 'enable',
            'created_at', 'updated_at',
            'live_total_gb', 'live_up_gb', 'live_down_gb', 'live_expiry_time', 'live_enable_status',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class TutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = ('id', 'title', 'content', 'order', 'created_at', 'updated_at')

# --- Serializers for Admin Section ---

class ServerSerializer(serializers.ModelSerializer):
    """
    Serializer for Server model, used by admin for CRUD operations.
    Password is write-only.
    """
    # To make panel_type human-readable in GET, but accept valid choices in POST/PUT
    panel_type_display = serializers.CharField(source='get_panel_type_display', read_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, help_text="Password for X-UI panel access.")

    class Meta:
        model = Server
        fields = ('id', 'name', 'url', 'panel_type', 'panel_type_display', 'username', 'password', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_active', 'created_at', 'updated_at') # is_active is set by connection test

    def validate_panel_type(self, value):
        valid_types = [pt.value for pt in PanelType]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid panel_type. Must be one of {valid_types}.")
        return value

class AnnouncementSerializer(serializers.ModelSerializer): # Re-using this, can be renamed to AdminAnnouncementSerializer if it diverges
    class Meta:
        model = Announcement
        fields = ('id', 'title', 'content', 'publish_date', 'is_faq')
        read_only_fields = ('publish_date',) # Publish date is auto_now_add for new, but could be made editable

class ConfigManualCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to manually create a Config entry for a user.
    Admin provides user, server, client_identifier, and subscription_link.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) # Admin selects user
    server = serializers.PrimaryKeyRelatedField(queryset=Server.objects.filter(is_active=True)) # Admin selects an active server

    class Meta:
        model = Config
        fields = (
            'user',
            'server',
            'client_identifier', # email in x-ui
            'subscription_link',
            'remark', # Optional remark by admin
            # Other fields like protocol, port, qr_code_link, total_gb, expiry_time, enable
            # will be either left blank, set to defaults, or fetched later by UserConfigListView.
            # Admin is primarily concerned with linking a user to a client_id on a server with a sub link.
        )

    def validate(self, data):
        # Check for uniqueness: a user should not have the same client_identifier on the same server.
        if Config.objects.filter(
            user=data['user'],
            server=data['server'],
            client_identifier=data['client_identifier']
        ).exists():
            raise serializers.ValidationError(
                "This client identifier is already assigned to this user on this server."
            )
        return data
```
