#!/usr/bin/env python3
"""
Configuration management for Reolink Firmware Checker
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional


class ReolinkConfig:
    """Manages configuration for Reolink firmware checker"""
    
    def __init__(self):
        self.config_file = Path("./config")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return toml.load(f)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self._get_default_config()
        else:
            # Config doesn't exist - run interactive setup
            return self._interactive_setup()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'device': {
                'model': 'RLN8-410',
                'hardware_version': 'N2MB02',
                'current_firmware_version': 'v3.5.1.368_25010326'
            },
            'settings': {
                'check_on_startup': True,
                'verbose_output': False,
                'auto_open_browser_on_manual': True
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                toml.dump(config, f)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_device_config(self) -> Dict[str, str]:
        """Get device configuration"""
        return self.config.get('device', {})
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.config.get('settings', {}).get(key, default)
    
    def update_firmware_version(self, new_version: str) -> None:
        """Update the current firmware version"""
        if 'device' not in self.config:
            self.config['device'] = {}
        
        self.config['device']['current_firmware_version'] = new_version
        self._save_config(self.config)
        print(f"Updated firmware version to: {new_version}")
    
    def update_device_info(self, model: str, hardware_version: str, firmware_version: str) -> None:
        """Update device information"""
        self.config['device'] = {
            'model': model,
            'hardware_version': hardware_version,
            'current_firmware_version': firmware_version
        }
        self._save_config(self.config)
        print(f"Updated device config: {model} ({hardware_version}) running {firmware_version}")
    
    def get_config_file_path(self) -> str:
        """Get the path to the config file"""
        return str(self.config_file)
    
    def _interactive_setup(self) -> Dict[str, Any]:
        """Interactive setup for first-time configuration"""
        print("🔧 Welcome to Reolink Firmware Checker!")
        print("Let's set up your device configuration.\n")
        
        # Get device information
        print("Device Information:")
        model = input("Enter your device model (e.g., RLN8-410): ").strip() or "RLN8-410"
        hardware_version = input("Enter your hardware version (e.g., N2MB02): ").strip() or "N2MB02"
        
        print("\nCurrent Firmware Version:")
        print("You can find this in your device's web interface under System > Device Info")
        current_version = input("Enter your current firmware version (e.g., v3.5.1.368_25010326): ").strip()
        
        if not current_version:
            current_version = "v3.5.1.368_25010326"
            print(f"Using default version: {current_version}")
        
        # Create configuration
        config = {
            'device': {
                'model': model,
                'hardware_version': hardware_version,
                'current_firmware_version': current_version
            },
            'settings': {
                'check_on_startup': True,
                'verbose_output': False,
                'auto_open_browser_on_manual': True
            }
        }
        
        # Save configuration
        self._save_config(config)
        
        print(f"\n✅ Configuration saved to: {self.config_file}")
        print(f"   Model: {model}")
        print(f"   Hardware: {hardware_version}")
        print(f"   Current firmware: {current_version}")
        print("\nYou can modify this later by editing the config file or using --update-version")
        
        return config

    def show_config(self) -> None:
        """Display current configuration"""
        print(f"Configuration file: {self.config_file}")
        print("Current configuration:")
        print(toml.dumps(self.config))