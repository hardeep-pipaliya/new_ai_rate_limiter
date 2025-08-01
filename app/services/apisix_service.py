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
    
    @classmethod
    def send_request(cls, provider, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request through APISIX gateway"""
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {provider.api_key}'
            }
            
            # Add provider-specific headers
            if provider.provider_type == 'azure':
                headers['api-version'] = provider.config_dict.get('azure_api_version', '2024-05-01-preview')
            
            # Send request to APISIX gateway
            response = requests.post(
                f"{Config.APISIX_GATEWAY_URL}/v1/chat/completions",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'content': result.get('choices', [{}])[0].get('message', {}).get('content', ''),
                    'usage': result.get('usage', {}),
                    'model': result.get('model', ''),
                    'provider': provider.provider_type
                }
            else:
                raise APISIXError(f"APISIX request failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise APISIXError(f"Request to APISIX failed: {str(e)}")
        except Exception as e:
            raise APISIXError(f"APISIX service error: {str(e)}")
    
    @classmethod
    def create_route(cls, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a route in APISIX"""
        try:
            response = requests.put(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_data['id']}",
                headers={'Content-Type': 'application/json'},
                json=route_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise APISIXError(f"Failed to create route: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise APISIXError(f"Failed to create APISIX route: {str(e)}")
    
    @classmethod
    def delete_route(cls, route_id: str) -> bool:
        """Delete a route from APISIX"""
        try:
            response = requests.delete(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
                timeout=30
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            raise APISIXError(f"Failed to delete APISIX route: {str(e)}")
    
    @classmethod
    def get_route(cls, route_id: str) -> Dict[str, Any]:
        """Get route information from APISIX"""
        try:
            response = requests.get(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise APISIXError(f"Failed to get route: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise APISIXError(f"Failed to get APISIX route: {str(e)}")
    
    @classmethod
    def list_routes(cls) -> Dict[str, Any]:
        """List all routes in APISIX"""
        try:
            response = requests.get(
                f"{Config.APISIX_ADMIN_URL}/apisix/admin/routes",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise APISIXError(f"Failed to list routes: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise APISIXError(f"Failed to list APISIX routes: {str(e)}") 