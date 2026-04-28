import requests
from jose import jwt

class KeycloakClient:
    def __init__(self, server_url, realm, client_id, client_secret):
        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = f"{self.server_url}/realms/{self.realm}"
        self.admin_url = f"{self.server_url}/admin/realms/{self.realm}"

    def get_admin_token(self):
        url = f"{self.base_url}/protocol/openid-connect/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        # If no client_secret is provided, we might be using public client. 
        # But for admin operations we typically need a confidential client.
        if not self.client_secret:
            # Fallback for dev: use admin/admin with password grant if no client_secret
            payload = {
                'grant_type': 'password',
                'client_id': 'admin-cli',
                'username': 'admin',
                'password': 'admin'
            }
            url = f"{self.server_url}/realms/master/protocol/openid-connect/token"

        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']

    def create_user(self, email, password, first_name, last_name, role):
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        user_data = {
            "username": email,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}]
        }
        
        response = requests.post(f"{self.admin_url}/users", json=user_data, headers=headers)
        # 201 Created or 409 Conflict
        if response.status_code == 409:
            raise Exception("El usuario ya existe en Keycloak")
        response.raise_for_status()
        
        # Get user ID to assign role
        users = requests.get(f"{self.admin_url}/users?username={email}", headers=headers).json()
        user_id = users[0]['id']
        
        if role:
            self.assign_role(user_id, role)
            
        return user_id

    def assign_role(self, user_id, role_name):
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Get role ID
        role_resp = requests.get(f"{self.admin_url}/roles/{role_name}", headers=headers)
        if role_resp.status_code == 404:
            # Create role if it doesn't exist (helpful for dev)
            requests.post(f"{self.admin_url}/roles", json={"name": role_name}, headers=headers)
            role_resp = requests.get(f"{self.admin_url}/roles/{role_name}", headers=headers)
            
        role_data = role_resp.json()
        
        # Assign role
        requests.post(f"{self.admin_url}/users/{user_id}/role-mappings/realm", json=[role_data], headers=headers)

    def login(self, email, password):
        url = f"{self.base_url}/protocol/openid-connect/token"
        payload = {
            'grant_type': 'password',
            'client_id': self.client_id,
            'username': email,
            'password': password
        }
        if self.client_secret:
            payload['client_secret'] = self.client_secret
            
        response = requests.post(url, data=payload)
        if response.status_code == 401:
            raise Exception("Credenciales inválidas en Keycloak")
        response.raise_for_status()
        return response.json()

    def logout(self, refresh_token):
        url = f"{self.base_url}/protocol/openid-connect/logout"
        payload = {
            'client_id': self.client_id,
            'refresh_token': refresh_token
        }
        if self.client_secret:
            payload['client_secret'] = self.client_secret
            
        requests.post(url, data=payload)

    def verify_token(self, token):
        # We will use the userinfo endpoint for simplicity and robustness instead of local signature validation
        # since we don't fetch public keys dynamically here.
        user_info = self.get_user_info(token)
        return user_info
        
    def get_user_info(self, token):
        url = f"{self.base_url}/protocol/openid-connect/userinfo"
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("Token inválido o expirado")
        return response.json()

keycloak_client = None

def init_keycloak(app):
    global keycloak_client
    keycloak_client = KeycloakClient(
        app.config['KEYCLOAK_SERVER_URL'],
        app.config['KEYCLOAK_REALM'],
        app.config['KEYCLOAK_CLIENT_ID'],
        app.config['KEYCLOAK_CLIENT_SECRET']
    )

def get_keycloak_client() -> KeycloakClient:
    return keycloak_client

