"""
APISIX service for rate limiting and API gateway integration
"""
import requests
import json
from typing import Dict, Any
from app.config.config import Config
from app.utils.exceptions import APISIXError

class APISIXService:
    """Service for APISIX operations"""
    
    @staticmethod
    def send_request(provider, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request through APISIX gateway"""
        try:
            # For now, only support OpenAI through APISIX
            if provider.provider_type == 'openai':
                apisix_endpoint = f"{Config.APISIX_GATEWAY_URL}/v1/chat/completions/openai"
            else:
                # For other providers, we'll implement direct API calls later
                raise APISIXError(f"Provider {provider.provider_type} not yet supported through APISIX")
            
            # Prepare headers with API key
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {provider.config_dict.get('api_key')}"
            }
            
            # Send request to APISIX gateway
            response = requests.post(
                apisix_endpoint,
                json=request_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                raise APISIXError(f"APISIX request failed: {response.status_code} - {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise APISIXError(f"Request to APISIX failed: {str(e)}")
        except Exception as e:
            raise APISIXError(f"APISIX service error: {str(e)}")
    
    @staticmethod
    def create_route(route_data: Dict[str, Any]) -> bool:
        """Create a route in APISIX"""
        try:
            response = requests.put(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_data['id']}",
                json=route_data,
                headers={'X-API-KEY': 'edd1c9f034335f136f87ad84b625c8f1'},
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                raise APISIXError(f"Failed to create route: {response.status_code} - {response.text}")
            
            return True
            
        except Exception as e:
            raise APISIXError(f"Failed to create APISIX route: {str(e)}")
    
    @staticmethod
    def delete_route(route_id: str) -> bool:
        """Delete a route from APISIX"""
        try:
            response = requests.delete(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
                headers={'X-API-KEY': 'edd1c9f034335f136f87ad84b625c8f1'},
                timeout=30
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            raise APISIXError(f"Failed to delete APISIX route: {str(e)}")
    
    @staticmethod
    def get_route(route_id: str) -> Dict[str, Any]:
        """Get route information from APISIX"""
        try:
            response = requests.get(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
                headers={'X-API-KEY': 'edd1c9f034335f136f87ad84b625c8f1'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise APISIXError(f"Failed to get route: {response.status_code}")
                
        except Exception as e:
            raise APISIXError(f"Failed to get APISIX route: {str(e)}") 