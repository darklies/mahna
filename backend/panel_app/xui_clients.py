import requests
import json
from enum import Enum

# For storing session cookies or tokens after login
xui_sessions = {} # In a real app, this should be managed more robustly (e.g. Redis, DB)

class PanelType(Enum):
    ALIREZA = "alireza"
    SANAEI = "3xui"

class BaseXUIClient:
    def __init__(self, server_url, username, password, panel_type: PanelType):
        self.base_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.panel_type = panel_type
        self.session_cookie = None
        self._load_session()

    def _get_session_key(self):
        return f"{self.panel_type.value}_{self.base_url}_{self.username}"

    def _save_session(self):
        if self.session_cookie:
            xui_sessions[self._get_session_key()] = self.session_cookie
            # print(f"Session saved for {self._get_session_key()}: {self.session_cookie}")

    def _load_session(self):
        key = self._get_session_key()
        if key in xui_sessions:
            self.session_cookie = xui_sessions[key]
            # print(f"Session loaded for {key}: {self.session_cookie}")
            # TODO: Add session validation logic here (e.g. make a test request)
            # For now, we assume if a cookie exists, it's valid.
            # This is a simplification. A real client would check if the session is still active.
            # If not active, it should re-login.
            if not self._is_session_valid():
                # print(f"Session for {key} is invalid. Clearing and re-login will be needed.")
                self.session_cookie = None
                xui_sessions.pop(key, None)


    def _is_session_valid(self):
        """
        Placeholder for session validation.
        A simple way could be to make a lightweight request (e.g., get server status or a small list).
        """
        if not self.session_cookie:
            return False
        # This is a placeholder. Actual validation would involve an API call.
        # For example, try to get a list of inbounds or server status.
        # print(f"Skipping actual session validation for {self._get_session_key()} in this example.")
        return True


    def _request(self, method, path, data=None, params=None, attempts=2):
        url = f"{self.base_url}{path}"
        headers = {}
        if self.session_cookie:
            headers['Cookie'] = self.session_cookie

        for attempt in range(attempts):
            try:
                # print(f"Requesting ({attempt+1}/{attempts}): {method} {url} Cookie: {self.session_cookie}")
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # print(f"Response status: {response.status_code}")
                # print(f"Response content: {response.text[:200]}")


                if response.status_code == 401 and attempt < attempts -1: # Unauthorized, try to re-login
                    # print("Unauthorized. Attempting to re-login...")
                    self.session_cookie = None # Clear old cookie
                    xui_sessions.pop(self._get_session_key(), None)
                    if self.login():
                        headers['Cookie'] = self.session_cookie # Update header with new cookie
                        # print("Re-login successful. Retrying original request.")
                        continue # Retry the request
                    else:
                        # print("Re-login failed.")
                        return None # Or raise an exception

                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text # Or handle non-JSON responses appropriately

            except requests.exceptions.RequestException as e:
                # print(f"Request failed: {e}")
                if attempt == attempts - 1: # Last attempt
                    # print(f"Final attempt failed for {method} {url}. Error: {e}")
                    raise # Re-raise the last exception
        return None # Should not be reached if raise_for_status is effective

    def login(self):
        """Abstract method for login, must be implemented by subclasses."""
        raise NotImplementedError

    def get_client_traffics(self, client_email_identifier: str):
        """Abstract method for getting client traffics."""
        raise NotImplementedError

    def get_inbounds(self):
        """Abstract method for getting all inbounds."""
        raise NotImplementedError

    def get_inbound_by_id(self, inbound_id: int):
        """Abstract method for getting a specific inbound by its ID."""
        raise NotImplementedError

    def add_client_to_inbound(self, inbound_id: int, client_settings: dict):
        """Abstract method for adding a client to an inbound."""
        raise NotImplementedError

    def get_client_details_from_inbounds(self, client_email_identifier: str):
        """
        Fetches all inbounds, then iterates through them to find the client
        and extract their full settings (like QR code link, subscription link etc.).
        This is a common pattern if there isn't a direct API to get full client details by email.
        """
        all_inbounds_data = self.get_inbounds()
        if not all_inbounds_data or not isinstance(all_inbounds_data, list):
            # print(f"Failed to fetch inbounds or empty/invalid data for {self.base_url}")
            return None

        for inbound in all_inbounds_data:
            if not isinstance(inbound, dict): continue
            clients = []
            # Structure might vary between panel types
            if 'clientStats' in inbound and isinstance(inbound['clientStats'], list): # Alireza-style (often)
                 clients = inbound['clientStats']
            elif 'settings' in inbound and isinstance(inbound.get('settings'), str): # Sanaei-style (often)
                try:
                    settings = json.loads(inbound['settings'])
                    if 'clients' in settings and isinstance(settings['clients'], list):
                        clients = settings['clients']
                except json.JSONDecodeError:
                    # print(f"Error decoding settings JSON for inbound ID {inbound.get('id')}")
                    continue

            # Fallback if client data is directly in `clients` field (less common for top-level inbound list)
            elif 'clients' in inbound and isinstance(inbound['clients'], list):
                 clients = inbound['clients']


            for client in clients:
                if isinstance(client, dict) and client.get('email') == client_email_identifier:
                    # Found the client. Now we need to construct the full config details.
                    # This part is highly dependent on the panel's API response structure for inbounds.
                    # We need: QR code, subscription link, protocol, port, etc.
                    # These details are often part of the inbound's main settings, not per-client stats.

                    client_detail = {
                        'email': client.get('email'),
                        'id': client.get('id'), # This might be client's specific ID within the inbound
                        'enable': client.get('enable', True),
                        'total_gb': client.get('totalGB', client.get('total', 0)) / (1024**3) if client.get('totalGB', client.get('total', 0)) else 0,
                        'up_gb': client.get('up', 0) / (1024**3) if client.get('up') else 0,
                        'down_gb': client.get('down', 0) / (1024**3) if client.get('down') else 0,
                        'expiry_time': client.get('expiryTime', 0), # timestamp, convert as needed
                        # --- Details usually from the parent inbound ---
                        'inbound_id': inbound.get('id'),
                        'remark': inbound.get('remark', f"Inbound {inbound.get('id')}"),
                        'protocol': inbound.get('protocol'),
                        'port': inbound.get('port'),
                        # TODO: Construct subscription_link and qr_code_link
                        # This requires knowing the specific format for each panel type and protocol
                        # Example placeholder:
                        'subscription_link': f"{self.base_url}/sub/{client.get('id','clientid')}", # Highly dependent
                        'qr_code_link': f"qr://{self.base_url}/qr/{client.get('id','clientid')}", # Highly dependent
                        'raw_config_link': f"raw://{self.base_url}/raw/{client.get('id','clientid')}" # Highly dependent
                    }
                    return client_detail
        return None

    def get_all_client_identifiers(self) -> list[dict]:
        """
        Fetches all inbounds and extracts all client identifiers (emails) along with some basic info.
        Returns a list of dictionaries, e.g., [{'email': 'user@example.com', 'inbound_id': 1, 'remark': 'inbound_remark'}].
        """
        all_identifiers = []
        all_inbounds_data = self.get_inbounds()
        if not all_inbounds_data or not isinstance(all_inbounds_data, list):
            return all_identifiers

        for inbound in all_inbounds_data:
            if not isinstance(inbound, dict): continue

            inbound_id = inbound.get('id')
            inbound_remark = inbound.get('remark', f"Inbound {inbound_id}")
            clients_data_list = []

            if self.panel_type == PanelType.ALIREZA:
                # Alireza panels often have clientStats directly in the inbound object for full list
                # or sometimes in settings.clients if clientStats is not exhaustive.
                # get_inbounds for Alireza returns list of inbounds, each might have clientStats
                if 'clientStats' in inbound and isinstance(inbound['clientStats'], list):
                    clients_data_list = inbound['clientStats']
                # Fallback or alternative structure for Alireza
                elif 'settings' in inbound and isinstance(inbound.get('settings'), str):
                     try:
                        settings = json.loads(inbound['settings'])
                        if 'clients' in settings and isinstance(settings['clients'], list):
                            clients_data_list = settings['clients']
                     except json.JSONDecodeError:
                        pass


            elif self.panel_type == PanelType.SANAEI:
                # Sanaei panels usually have clients within a JSON string in 'settings'
                if 'settings' in inbound and isinstance(inbound.get('settings'), str):
                    try:
                        settings = json.loads(inbound['settings'])
                        if 'clients' in settings and isinstance(settings['clients'], list):
                            clients_data_list = settings['clients']
                    except json.JSONDecodeError:
                        # print(f"Error decoding settings JSON for inbound ID {inbound_id} on Sanaei panel")
                        pass

            for client_data in clients_data_list:
                if isinstance(client_data, dict) and 'email' in client_data:
                    all_identifiers.append({
                        'email': client_data['email'],
                        'client_id_xui': client_data.get('id'), # Actual ID in XUI (UUID for vmess/vless, email for SS, pass for trojan)
                        'inbound_id': inbound_id,
                        'inbound_remark': inbound_remark,
                        'protocol': inbound.get('protocol'),
                    })
        return all_identifiers


class AlirezaXUIClient(BaseXUIClient):
    def __init__(self, server_url, username, password):
        super().__init__(server_url, username, password, PanelType.ALIREZA)
        self.api_base_path = "/xui/API/inbounds" # Default, can be different

    def login(self):
        if self.session_cookie and self._is_session_valid():
            # print(f"Alireza: Already logged in or session valid for {self.base_url}")
            return True

        login_path = "/login" # Common login path
        try:
            # print(f"Alireza: Attempting login to {self.base_url}{login_path}")
            response = requests.post(
                f"{self.base_url}{login_path}",
                data={'username': self.username, 'password': self.password},
                timeout=10
            )
            response.raise_for_status()

            if response.status_code == 200:
                 # Try to get 'session' cookie, common for Alireza panels
                self.session_cookie = response.cookies.get('session')
                if not self.session_cookie:
                    # Some panels might use a different cookie name or return it in body
                    # print(f"Alireza: 'session' cookie not found. Available cookies: {response.cookies.items()}")
                    # Fallback: check common alternative cookie names if necessary
                    # This is a basic implementation; more robust cookie handling might be needed
                    pass

                if self.session_cookie:
                    self._save_session()
                    # print(f"Alireza: Login successful for {self.base_url}. Cookie: {self.session_cookie}")
                    return True
                else:
                    # print(f"Alireza: Login response OK, but no session cookie captured. Response: {response.text[:200]}")
                    return False
            # print(f"Alireza: Login failed for {self.base_url}. Status: {response.status_code}, Response: {response.text[:200]}")
            return False
        except requests.exceptions.RequestException as e:
            # print(f"Alireza: Login request exception for {self.base_url}: {e}")
            return False

    def get_client_traffics(self, client_email_identifier: str):
        # Path: /getClientTraffics/:email
        path = f"{self.api_base_path}/getClientTraffics/{client_email_identifier}"
        try:
            return self._request('GET', path)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404: # Client not found
                return None
            raise

    def get_inbounds(self):
        # Path: "/" relative to api_base_path
        path = f"{self.api_base_path}/"
        data = self._request('GET', path)
        if data and data.get('success') and isinstance(data.get('obj'), list):
            return data['obj']
        # print(f"Alireza: get_inbounds failed or unexpected response: {data}")
        return None

    def get_inbound_by_id(self, inbound_id: int):
        # Path: "/get/:id"
        path = f"{self.api_base_path}/get/{inbound_id}"
        data = self._request('GET', path)
        if data and data.get('success') and isinstance(data.get('obj'), dict):
            return data['obj']
        return None

    def add_client_to_inbound(self, inbound_id: int, client_settings: dict):
        # Path: "/addClient/" - Note: Alireza's API might expect inbound_id in the client_settings payload
        # The client_settings should conform to what `clients` array elements look like for that inbound.
        # It typically requires at least `id`, `email`, `protocol-specific-fields`.
        # This is a simplified call, actual payload might be more complex.
        path = f"{self.api_base_path}/addClient/"

        # Example client_settings structure (highly dependent on protocol):
        # {
        #   "id": "uuid-here", // for vmess/vless
        #   "email": "client@example.com",
        #   "idInbound": inbound_id, // Often needed
        #   "totalGB": 0, "expiryTime": 0, "enable": true,
        #   // ... other protocol specific fields like "alterId", "security" for vmess
        # }
        payload = client_settings.copy()
        if 'idInbound' not in payload and 'inboundId' not in payload : # Common requirement
             payload['idInbound'] = inbound_id # Make sure this is the correct field name

        data = self._request('POST', path, data=payload)
        if data and data.get('success'):
            return data.get('obj') # Or True if no specific object is returned
        return False


class SanaeiXUIClient(BaseXUIClient):
    def __init__(self, server_url, username, password):
        super().__init__(server_url, username, password, PanelType.SANAEI)
        self.api_base_path = "/panel/api/inbounds"

    def login(self):
        if self.session_cookie and self._is_session_valid():
            # print(f"Sanaei: Already logged in or session valid for {self.base_url}")
            return True

        login_path = "/login" # Common login path
        try:
            # print(f"Sanaei: Attempting login to {self.base_url}{login_path}")
            response = requests.post(
                f"{self.base_url}{login_path}",
                data={'username': self.username, 'password': self.password}, # POST data, not json
                timeout=10
            )
            response.raise_for_status()
            if response.status_code == 200:
                # Sanaei panels often use 'session' or 'sess' cookie
                self.session_cookie = response.cookies.get('session') or response.cookies.get('sess')
                if not self.session_cookie:
                    # print(f"Sanaei: 'session' or 'sess' cookie not found. Available cookies: {response.cookies.items()}")
                    pass # Similar to Alireza, more robust handling might be needed

                if self.session_cookie:
                    self._save_session()
                    # print(f"Sanaei: Login successful for {self.base_url}. Cookie: {self.session_cookie}")
                    return True
                else:
                    # print(f"Sanaei: Login response OK, but no session cookie captured. Response: {response.text[:200]}")
                    return False
            # print(f"Sanaei: Login failed for {self.base_url}. Status: {response.status_code}, Response: {response.text[:200]}")
            return False
        except requests.requests.exceptions.RequestException as e:
            # print(f"Sanaei: Login request exception for {self.base_url}: {e}")
            return False

    def get_client_traffics(self, client_email_identifier: str):
        # Path: /getClientTraffics/:email
        path = f"{self.api_base_path}/getClientTraffics/{client_email_identifier}"
        try:
            data = self._request('GET', path)
            if data and data.get('success') and isinstance(data.get('obj'), list): # Often returns a list
                return data['obj'][0] if data['obj'] else None # Return the first client traffic object
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_inbounds(self):
        # Path: "/list"
        path = f"{self.api_base_path}/list"
        data = self._request('GET', path)
        if data and data.get('success') and isinstance(data.get('obj'), list):
            return data['obj']
        # print(f"Sanaei: get_inbounds failed or unexpected response: {data}")
        return None

    def get_inbound_by_id(self, inbound_id: int):
        # Path: "/get/:id"
        path = f"{self.api_base_path}/get/{inbound_id}"
        data = self._request('GET', path)
        if data and data.get('success') and isinstance(data.get('obj'), dict):
            return data['obj']
        return None

    def add_client_to_inbound(self, inbound_id: int, client_settings: dict):
        # Path: "/addClient" - Sanaei's API usually expects client settings in a specific format.
        # The inbound_id is often part of the client_settings payload itself.
        # client_settings should be a JSON string for the 'settings' field of the request.
        path = f"{self.api_base_path}/addClient"

        # Example client_settings for Sanaei (highly dependent on protocol):
        # This usually goes into a "settings" field which is a JSON string.
        # {
        #   "clients": [
        #     {
        #       "id": "uuid-here", // for vmess/vless
        #       "email": "client@example.com",
        #       "totalGB": 0, "expiryTime": 0, "enable": true, "flow": ""
        #       // ... other protocol specific fields
        #     }
        #   ]
        # }
        # The request to "/addClient" often takes `id` (inbound_id) and `settings` (json string of client list)
        payload = {
            "id": inbound_id, # Inbound ID
            "settings": json.dumps({"clients": [client_settings]}) # Client settings as a JSON string
        }

        data = self._request('POST', path, data=payload) # This should be form data, not json
        if data and data.get('success'):
            return data.get('obj') # Or True
        return False


def get_xui_client(server_model_instance) -> BaseXUIClient | None:
    """Factory function to get the appropriate XUI client."""
    if server_model_instance.panel_type == PanelType.ALIREZA.value:
        return AlirezaXUIClient(server_model_instance.url, server_model_instance.username, server_model_instance.password)
    elif server_model_instance.panel_type == PanelType.SANAEI.value:
        return SanaeiXUIClient(server_model_instance.url, server_model_instance.username, server_model_instance.password)
    return None

# Example Usage (for testing purposes, remove later):
if __name__ == '__main__':
    # Mock Server Model Instance
    class MockServer:
        def __init__(self, url, username, password, panel_type):
            self.url = url
            self.username = username
            self.password = password
            self.panel_type = panel_type

    # Replace with your actual test server details if you want to run this directly
    # server_info_ali = MockServer("YOUR_ALIREZA_URL", "YOUR_USERNAME", "YOUR_PASSWORD", "alireza")
    # server_info_sanaei = MockServer("YOUR_SANAEI_URL", "YOUR_USERNAME", "YOUR_PASSWORD", "3xui")

    # client_email_to_test = "test@example.com"

    # def test_client(server_info, client_email):
    #     print(f"\n--- Testing Panel: {server_info.panel_type} at {server_info.url} ---")
    #     client = get_xui_client(server_info)
    #     if not client:
    #         print("Failed to get client.")
    #         return

    #     if client.login():
    #         print("Login successful.")

    #         print(f"\nFetching traffics for {client_email}:")
    #         traffics = client.get_client_traffics(client_email)
    #         if traffics:
    #             print(f"Traffics for {client_email}: {traffics}")
    #         else:
    #             print(f"Could not fetch traffics for {client_email} or client not found.")

    #         print("\nFetching all inbounds...")
    #         inbounds = client.get_inbounds()
    #         if inbounds:
    #             print(f"Found {len(inbounds)} inbounds.")
    #             # print(json.dumps(inbounds[0] if inbounds else {}, indent=2)) # Print first inbound

    #             print(f"\nAttempting to get full client details for {client_email} from inbounds data...")
    #             client_details = client.get_client_details_from_inbounds(client_email)
    #             if client_details:
    #                 print(f"Full details for {client_email}: {json.dumps(client_details, indent=2)}")
    #             else:
    #                 print(f"Could not find full details for {client_email} in inbounds.")

    #         else:
    #             print("Failed to fetch inbounds.")
    #     else:
    #         print("Login failed.")

    # if 'server_info_ali' in locals():
    #    test_client(server_info_ali, client_email_to_test)
    # if 'server_info_sanaei' in locals():
    #    test_client(server_info_sanaei, client_email_to_test)

    print("XUI Client module loaded. Run with actual server details for testing.")
