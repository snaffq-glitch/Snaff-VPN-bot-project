import requests
import hashlib
import time


class WireGuardAPI:
    def __init__(self, base_url: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = ("admin", password)
    
    def create_client(self, device_name: str = "user") -> dict:
        unique_id = hashlib.md5(f"{device_name}{time.time()}".encode()).hexdigest()[:8]
        client_data = {
            "name": f"{device_name}_{unique_id}",
            "address": "10.0.0.2/24",
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/wireguard/client",
                json=client_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def delete_client(self, client_id: str) -> bool:
        try:
            response = self.session.delete(
                f"{self.base_url}/wireguard/client/{client_id}",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_clients(self) -> list:
        try:
            response = self.session.get(
                f"{self.base_url}/wireguard/client",
                timeout=10
            )
            return response.json()
        except:
            return []