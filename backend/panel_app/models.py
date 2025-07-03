from django.db import models
from django.contrib.auth.models import AbstractUser
# import uuid # Not used in the current model structure, can be removed or kept for future use

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_support_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Server(models.Model):
    PANEL_TYPES = [
        ('alireza', 'Alireza X-UI'),
        ('3xui', '3X-UI (Sanai)'),
    ]
    name = models.CharField(max_length=100)
    url = models.URLField()
    panel_type = models.CharField(max_length=10, choices=PANEL_TYPES)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100) # TODO: Encrypt this field or use a secure way to store credentials
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Config(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='configs')
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='configs')
    client_identifier = models.CharField(max_length=255) # This is the 'email' field in x-ui
    remark = models.CharField(max_length=255, null=True, blank=True) # Optional: a remark for the config
    protocol = models.CharField(max_length=50, null=True, blank=True) # e.g., vmess, vless
    port = models.PositiveIntegerField(null=True, blank=True)
    qr_code_link = models.TextField(null=True, blank=True) # QR code data or link to image
    subscription_link = models.TextField(null=True, blank=True)
    raw_config_link = models.TextField(null=True, blank=True) # For individual config link
    # Store other relevant details from x-ui panel if needed
    # Example: total_traffic, up_traffic, down_traffic, expiry_time (as timestamp or datetime)
    total_gb = models.BigIntegerField(default=0) # Total traffic in GB (or bytes, then convert)
    up_gb = models.BigIntegerField(default=0) # Upload in GB (or bytes)
    down_gb = models.BigIntegerField(default=0) # Download in GB (or bytes)
    expiry_time = models.DateTimeField(null=True, blank=True) # Expiry date/time
    enable = models.BooleanField(default=True) # Status of the config in x-ui

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.server.name} - {self.client_identifier}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    is_faq = models.BooleanField(default=False)
    # created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_created')

    def __str__(self):
        return self.title

class Tutorial(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField() # Can be Markdown, HTML, or plain text
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    # category = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., Android, iOS, Windows")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
