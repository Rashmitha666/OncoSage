"""
Configuration loader for the Oncology AI Assistant System.
Provides functionality to load and validate configuration files.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConfigLoader:
    """Configuration loader for the Oncology AI Assistant System."""
    
    def __init__(self, config_dir: str = None):
        """Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir:
            self.config_dir = config_dir
        else:
            # Default to config directory in project root
            self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            
        # Ensure config directory exists
        if not os.path.exists(self.config_dir):
            logger.warning(f"Config directory not found: {self.config_dir}")
            os.makedirs(self.config_dir, exist_ok=True)
            
        # Load default configuration
        self.default_config = self._load_default_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration.
        
        Returns:
            Default configuration dictionary
        """
        default_config_path = os.path.join(self.config_dir, 'default_config.json')
        
        try:
            with open(default_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Default config file not found: {default_config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in default config file: {default_config_path}")
            return {}
            
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration for a specific component.
        
        Args:
            config_name: Name of the configuration to load
            
        Returns:
            Configuration dictionary
        """
        # Check if config_name is a section in default_config
        if config_name in self.default_config:
            default_section = self.default_config.get(config_name, {})
        else:
            default_section = {}
            
        # Check for component-specific config file
        config_path = os.path.join(self.config_dir, f"{config_name}_config.json")
        
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                
                # Merge with default config
                merged_config = {**default_section, **custom_config}
                logger.info(f"Loaded configuration for {config_name}")
                return merged_config
                
        except FileNotFoundError:
            logger.info(f"No custom config file found for {config_name}, using default")
            return default_section
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {config_path}")
            return default_section
            
    def save_config(self, config_name: str, config: Dict[str, Any]) -> bool:
        """Save configuration for a specific component.
        
        Args:
            config_name: Name of the configuration to save
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        config_path = os.path.join(self.config_dir, f"{config_name}_config.json")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Saved configuration for {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration for {config_name}: {e}")
            return False
            
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            API key or None if not found
        """
        # Check for API key in environment variable
        env_var_name = f"{service_name.upper()}_API_KEY"
        api_key = os.environ.get(env_var_name)
        
        if api_key:
            return api_key
            
        # Check for API key in default config
        for section_name, section in self.default_config.items():
            if isinstance(section, dict):
                # Check if section contains API key for service
                if service_name in section and isinstance(section[service_name], dict):
                    api_key = section[service_name].get('api_key')
                    if api_key:
                        return api_key
                        
                # Check if section is the service
                if section_name == service_name and isinstance(section, dict):
                    api_key = section.get('api_key')
                    if api_key:
                        return api_key
                        
        # Check for API key in service-specific config
        service_config = self.load_config(service_name)
        api_key = service_config.get('api_key')
        
        return api_key
        
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration.
        
        Returns:
            System configuration dictionary
        """
        return self.load_config('system')
        
    def get_enabled_agents(self) -> Dict[str, bool]:
        """Get enabled agents configuration.
        
        Returns:
            Dictionary mapping agent names to enabled status
        """
        system_config = self.get_system_config()
        return system_config.get('enable_agents', {})
        
    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if an agent is enabled.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if enabled, False otherwise
        """
        enabled_agents = self.get_enabled_agents()
        return enabled_agents.get(agent_name, False)
