from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView # For custom actions like test connection

from .serializers import (
    UserSerializer, AdminCreateUserSerializer, SupportUserSerializer,
    ConfigSerializer, TutorialSerializer, AnnouncementSerializer,
    ServerSerializer, ConfigManualCreateSerializer,
)
from .models import Config, Server, Tutorial, Announcement
from .xui_clients import get_xui_client, PanelType
from thefuzz import process as fuzzy_process
from thefuzz import fuzz

User = get_user_model()

# Basic view to check API is up
def home(request):
    from django.http import HttpResponse
    return HttpResponse("Welcome to the X-UI Panel Manager API. All sections active.")

# --- Authentication & Basic User Profile ---
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

# --- Permissions ---
class IsSuperAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# --- Admin: User Management ---
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdminUser]

class AdminUserCreateView(generics.CreateAPIView):
    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsSuperAdminUser]
    def perform_create(self, serializer):
        serializer.save()

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdminUser]

class SupportUserCreateView(generics.CreateAPIView):
    serializer_class = SupportUserSerializer
    permission_classes = [IsSuperAdminUser]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = UserSerializer(user, context=self.get_serializer_context()).data
        response_data['generated_password'] = user.generated_password
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

# --- Customer Profile Section Views ---
class UserConfigListView(generics.ListAPIView):
    serializer_class = ConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Config.objects.filter(user=self.request.user).select_related('server')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_data = []
        for config_instance in queryset:
            server_instance = config_instance.server
            s_config = self.get_serializer(config_instance).data # Start with DB data
            s_config.update({'live_total_gb': None, 'live_up_gb': None, 'live_down_gb': None,
                             'live_expiry_time': None, 'live_enable_status': None}) # Default live fields

            if server_instance and server_instance.is_active:
                xui_client = get_xui_client(server_instance)
                live_config_data = None
                if xui_client:
                    try:
                        if xui_client.login():
                            live_config_data = xui_client.get_client_details_from_inbounds(config_instance.client_identifier)
                            if not live_config_data:
                                traffic_info = xui_client.get_client_traffics(config_instance.client_identifier)
                                if traffic_info:
                                    live_config_data = {
                                        'email': config_instance.client_identifier,
                                        'enable': traffic_info.get('enable', True),
                                        'total_gb': traffic_info.get('total', 0) / (1024**3) if traffic_info.get('total') else 0,
                                        'up_gb': traffic_info.get('up', 0) / (1024**3) if traffic_info.get('up') else 0,
                                        'down_gb': traffic_info.get('down', 0) / (1024**3) if traffic_info.get('down') else 0,
                                        'expiry_time': traffic_info.get('expiryTime', 0),
                                    }
                        else: print(f"XUI Login failed for server: {server_instance.name}")
                    except Exception as e: print(f"Error XUI {server_instance.name} for {config_instance.client_identifier}: {e}")

                if live_config_data:
                    s_config['live_total_gb'] = live_config_data.get('total_gb')
                    s_config['live_up_gb'] = live_config_data.get('up_gb')
                    s_config['live_down_gb'] = live_config_data.get('down_gb')
                    expiry_timestamp = live_config_data.get('expiry_time', 0)
                    if expiry_timestamp and expiry_timestamp > 0:
                        s_config['live_expiry_time'] = datetime.fromtimestamp(expiry_timestamp / 1000, tz=timezone.utc).isoformat()
                    s_config['live_enable_status'] = live_config_data.get('enable')
                    if live_config_data.get('qr_code_link'): s_config['qr_code_link'] = live_config_data['qr_code_link']
                    if live_config_data.get('subscription_link'): s_config['subscription_link'] = live_config_data['subscription_link']
                    if live_config_data.get('raw_config_link'): s_config['raw_config_link'] = live_config_data['raw_config_link']
                    if live_config_data.get('protocol'): s_config['protocol'] = live_config_data['protocol']
                    if live_config_data.get('port'): s_config['port'] = live_config_data['port']
                    if live_config_data.get('remark') and not config_instance.remark: s_config['remark'] = live_config_data.get('remark')
            serialized_data.append(s_config)
        return Response(serialized_data)

class TutorialListView(generics.ListAPIView):
    queryset = Tutorial.objects.all().order_by('order', 'title')
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticated]

class PublicAnnouncementListView(generics.ListAPIView): # For customers
    queryset = Announcement.objects.filter(is_faq=False).order_by('-publish_date')
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated] # Or AllowAny

class FAQAnnouncementListView(generics.ListAPIView): # For login page
    queryset = Announcement.objects.filter(is_faq=True).order_by('-publish_date')
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.AllowAny] # Publicly accessible

# --- Admin: Management Section Views ---

# Admin: Announcement Management
class AdminAnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.all().order_by('-publish_date')
    serializer_class = AnnouncementSerializer
    permission_classes = [IsSuperAdminUser]

class AdminAnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsSuperAdminUser]

# Admin: Server Management
class AdminServerListCreateView(generics.ListCreateAPIView):
    queryset = Server.objects.all().order_by('name')
    serializer_class = ServerSerializer
    permission_classes = [IsSuperAdminUser]

    def perform_create(self, serializer):
        # Attempt to test connection before saving or setting is_active
        # For simplicity, we'll save first, then test, then update is_active.
        # A more robust approach might test before the initial save.
        server = serializer.save() # Save with default is_active=False
        xui_client = get_xui_client(server)
        is_connected = False
        if xui_client:
            try:
                is_connected = xui_client.login() # Test login
            except Exception as e:
                print(f"Connection test failed for new server {server.name}: {e}")

        if is_connected:
            server.is_active = True
            server.save(update_fields=['is_active'])
        else:
            # Optionally, provide feedback that connection failed but server was saved.
            # For now, it's saved with is_active=False.
            pass


class AdminServerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [IsSuperAdminUser]

    def perform_update(self, serializer):
        # Save the instance first to get updated credentials if changed
        server = serializer.save()
        xui_client = get_xui_client(server)
        is_connected = False
        if xui_client:
            try:
                # Force re-login with potentially new credentials by clearing old session
                xui_client.session_cookie = None
                is_connected = xui_client.login()
            except Exception as e:
                print(f"Connection test failed for updated server {server.name}: {e}")

        server.is_active = is_connected
        serializer.save(is_active=is_connected) # Save again with updated is_active status

class AdminServerTestConnectionView(APIView):
    """
    An explicit endpoint for an admin to test connection to a server.
    """
    permission_classes = [IsSuperAdminUser]

    def post(self, request, pk, format=None):
        try:
            server = Server.objects.get(pk=pk)
        except Server.DoesNotExist:
            return Response({"error": "Server not found."}, status=status.HTTP_404_NOT_FOUND)

        xui_client = get_xui_client(server)
        if not xui_client:
            return Response({"error": "Invalid server panel type."}, status=status.HTTP_400_BAD_REQUEST)

        is_connected = False
        error_message = None
        try:
            xui_client.session_cookie = None # Force re-login for test
            is_connected = xui_client.login()
            if not is_connected:
                error_message = "Login to X-UI panel failed. Check credentials or panel status."
        except Exception as e:
            error_message = f"Connection test failed: {str(e)}"
            print(f"AdminServerTestConnectionView error for server {server.name}: {e}")

        server.is_active = is_connected
        server.save(update_fields=['is_active'])

        if is_connected:
            return Response({"message": "Connection successful.", "is_active": True}, status=status.HTTP_200_OK)
        else:
            return Response({"message": error_message or "Connection failed.", "is_active": False}, status=status.HTTP_400_BAD_REQUEST)


# Admin: Manual Config Creation
class AdminConfigManualCreateView(generics.CreateAPIView):
    serializer_class = ConfigManualCreateSerializer
    permission_classes = [IsSuperAdminUser]

    def perform_create(self, serializer):
        # The serializer already handles associating user and server.
        # client_identifier and subscription_link are directly saved.
        # Other details (QR, traffic, etc.) can be populated when user views their configs.
        serializer.save()

# Admin: Fuzzy Search for XUI Clients
class AdminXUIClientsSearchView(APIView):
    """
    Admin API view to search for client identifiers (emails) across all active X-UI panels
    using fuzzy matching.
    """
    permission_classes = [IsSuperAdminUser]
    MIN_QUERY_LENGTH = 3
    SIMILARITY_THRESHOLD = 75 # Adjust as needed (0-100)
    RESULT_LIMIT_PER_SERVER = 10 # Max results per server for a query
    OVERALL_RESULT_LIMIT = 50 # Max results overall

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        if len(query) < self.MIN_QUERY_LENGTH:
            return Response(
                {"error": f"Query must be at least {self.MIN_QUERY_LENGTH} characters long."},
                status=status.HTTP_400_BAD_REQUEST
            )

        active_servers = Server.objects.filter(is_active=True)
        if not active_servers.exists():
            return Response({"message": "No active servers found to search."}, status=status.HTTP_200_OK)

        all_found_clients = []

        for server_instance in active_servers:
            xui_client = get_xui_client(server_instance)
            if not xui_client:
                print(f"Could not get XUI client for server: {server_instance.name}")
                continue

            try:
                if not xui_client.login():
                    print(f"Login failed for XUI server: {server_instance.name}")
                    continue

                # This method should return a list of dicts: [{'email': str, 'inbound_id': int, ...}, ...]
                client_identifiers_data = xui_client.get_all_client_identifiers()

                if not client_identifiers_data:
                    continue

                # Extract just the 'email' field for fuzzy matching for this server
                emails_on_server = [client_data['email'] for client_data in client_identifiers_data if client_data.get('email')]

                # Perform fuzzy search on this server's emails
                # Using WRatio for better handling of partial matches and word order
                # extractWithoutOrder might be too broad, extractBests is good
                # Limit results per server to avoid one server dominating results
                # scorer=fuzz.WRatio or fuzz.QRatio or fuzz.token_set_ratio
                # process.extract returns list of (choice, score, key_if_provided_else_choice)
                # We pass client_identifiers_data to map back results easily if needed, but here we match on emails_on_server

                # We need to match the query against the list of emails
                # and then map the matched email back to its full client_data dict.
                # To do this efficiently, create a mapping from email to its original dict.
                email_to_client_data_map = {cd['email']: cd for cd in client_identifiers_data if cd.get('email')}

                # Fuzzy match against the list of unique emails from this server
                # limit here is how many matches to consider from THIS server's list
                # score_cutoff filters directly in extract
                server_matches = fuzzy_process.extractBests(
                    query,
                    email_to_client_data_map.keys(), # Search against the list of email strings
                    scorer=fuzz.WRatio,
                    score_cutoff=self.SIMILARITY_THRESHOLD,
                    limit=self.RESULT_LIMIT_PER_SERVER
                )

                for matched_email, score in server_matches:
                    original_client_data = email_to_client_data_map.get(matched_email)
                    if original_client_data:
                        all_found_clients.append({
                            'server_id': server_instance.id,
                            'server_name': server_instance.name,
                            'client_email': matched_email, # The matched email
                            'client_id_xui': original_client_data.get('client_id_xui'),
                            'inbound_id': original_client_data.get('inbound_id'),
                            'inbound_remark': original_client_data.get('inbound_remark'),
                            'protocol': original_client_data.get('protocol'),
                            'score': score
                        })

            except Exception as e:
                print(f"Error processing server {server_instance.name} for fuzzy search: {e}")
                # Optionally, add a message to response indicating this server had issues
                continue

        # Sort all found clients by score (descending) and take top N overall results
        all_found_clients.sort(key=lambda x: x['score'], reverse=True)
        final_results = all_found_clients[:self.OVERALL_RESULT_LIMIT]

        if not final_results:
            return Response({"message": f"No clients found matching '{query}' with similarity >= {self.SIMILARITY_THRESHOLD}%."}, status=status.HTTP_200_OK)

        return Response(final_results, status=status.HTTP_200_OK)
