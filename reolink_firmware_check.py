#!/usr/bin/env python3
"""
Reolink Firmware Checker
Checks for new firmware versions for Reolink NVR devices
"""

import requests
import json
import re
from packaging import version
import sys
from config import ReolinkConfig

class ReolinkFirmwareChecker:
    def __init__(self):
        self.base_url = "https://reolink.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://reolink.com/download-center/',
        })

    def get_reolink_firmware_api(self, product_id, hardware_version_id):
        """Use the actual Reolink API endpoint"""
        api_url = f"{self.base_url}/wp-json/reo-v2/download/firmware/"

        params = {
            'dlProductId': product_id,
            'hardwareVersion': hardware_version_id,
            'lang': 'en'
        }

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Pragma': 'no-cache',
            'Sec-Fetch-Site': 'same-origin',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://reolink.com/download-center/',
            'Sec-Fetch-Dest': 'empty',
            'Priority': 'u=3, i'
        }

        try:
            print(f"Calling Reolink API: dlProductId={product_id}, hardwareVersion={hardware_version_id}")
            response = self.session.get(api_url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # print(f"API Response: {data}")  # Commented out - too verbose
                return self.extract_version_from_api_response(data)
            else:
                print(f"API returned status: {response.status_code}")

        except Exception as e:
            print(f"API call failed: {e}")

        return None

    def extract_version_from_api_response(self, data):
        """Extract firmware version from API response"""
        if not data or 'data' not in data:
            return None

        firmware_list = data['data']
        if not firmware_list:
            return None

        # Get the first product (should be our model)
        product_data = firmware_list[0]
        if 'firmwares' not in product_data:
            return None

        firmwares = product_data['firmwares']
        if not firmwares:
            return None

        # Find the latest firmware version by sorting by updated_at timestamp
        latest_firmware = max(firmwares, key=lambda x: x.get('updated_at', 0))

        if 'version' in latest_firmware:
            version = latest_firmware['version']
            print(f"Found latest version: {version}")
            # Return the version as-is since it's already in the right format
            return version

        return None

    def get_product_and_hardware_ids(self, model, hardware_version):
        """Map model and hardware version to the IDs used by Reolink API"""
        # This mapping would need to be built up over time or discovered
        # For now, let's try the known values from your hint
        model_mappings = {
            'RLN8-410': {
                'product_id': 33,
                'hardware_versions': {
                    'N2MB02': 231,
                    # Add more hardware versions as discovered
                }
            }
            # Add more models as discovered
        }

        if model in model_mappings:
            product_id = model_mappings[model]['product_id']
            hardware_id = model_mappings[model]['hardware_versions'].get(hardware_version)
            if hardware_id:
                return product_id, hardware_id

        return None, None

    def extract_version_from_json(self, data):
        """Extract version from JSON response"""
        data_str = json.dumps(data).lower()

        # Look for version patterns
        version_patterns = [
            r'v?(\d+\.\d+\.\d+\.\d+_\d+)',
            r'"version":\s*"([^"]+)"',
            r'"firmware":\s*"([^"]+)"',
        ]

        for pattern in version_patterns:
            matches = re.findall(pattern, data_str)
            if matches:
                return matches[0]

        return None

    def try_direct_download_page(self, model):
        """Try to access model-specific download page"""
        urls = [
            f"{self.base_url}/download-center/{model.lower()}/",
            f"{self.base_url}/download/{model.lower()}/",
            f"{self.base_url}/support/download/{model.lower()}/",
        ]

        for url in urls:
            try:
                print(f"Trying direct page: {url}")
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Look for version patterns in the HTML
                    version_patterns = [
                        r'v?(\d+\.\d+\.\d+\.\d+_\d+)',
                        r'Version[:\s]+([v]?\d+\.\d+\.\d+)',
                        r'Firmware[:\s]+([v]?\d+\.\d+\.\d+)',
                    ]

                    for pattern in version_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            return matches[0]

            except Exception as e:
                print(f"  Failed: {e}")
                continue

        return None

    def simulate_form_search(self, model, hardware_version):
        """Simulate the download center form search"""
        print(f"Simulating form search for {model} with HW {hardware_version}")

        try:
            # First, get the download center page to extract any form tokens or session info
            response = self.session.get(f"{self.base_url}/download-center/")
            if response.status_code != 200:
                return None

            # Look for form action or search endpoints in the page
            import re

            # Try to find form action URLs
            form_actions = re.findall(r'action=["\']([^"\']+)["\']', response.text)
            search_urls = re.findall(r'["\']([^"\']*search[^"\']*)["\']', response.text)

            # Try different search approaches
            search_data = {
                'model': model,
                'hardware': hardware_version,
                'hw_version': hardware_version,
                'product': model,
                'query': model,
                'search': model,
                'type': 'firmware'
            }

            # Try POST to download center
            try:
                response = self.session.post(f"{self.base_url}/download-center/", data=search_data)
                if response.status_code == 200:
                    version = self.extract_version_from_html(response.text)
                    if version:
                        return version
            except:
                pass

            # Try sitesearch endpoint
            try:
                response = self.session.get(f"{self.base_url}/sitesearch/", params={'q': model})
                if response.status_code == 200:
                    version = self.extract_version_from_html(response.text)
                    if version:
                        return version
            except:
                pass

        except Exception as e:
            print(f"Form search failed: {e}")

        return None

    def extract_version_from_html(self, html_content):
        """Extract version from HTML content"""
        version_patterns = [
            r'v?(\d+\.\d+\.\d+\.\d+_\d+)',
            r'Version[:\s]+v?(\d+\.\d+\.\d+\.\d+)',
            r'Firmware[:\s]+v?(\d+\.\d+\.\d+\.\d+)',
            r'Download[:\s]+v?(\d+\.\d+\.\d+\.\d+)',
        ]

        for pattern in version_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                # Return the most recent looking version
                versions = [m for m in matches if len(m) > 5]  # Filter out short matches
                if versions:
                    return max(versions, key=lambda x: x.replace('_', '').replace('.', ''))

        return None

    def search_firmware(self, model, hardware_version):
        """Search for firmware using multiple approaches"""
        print(f"Searching for firmware for {model} (HW: {hardware_version})...")

        # Try the official API first
        product_id, hardware_id = self.get_product_and_hardware_ids(model, hardware_version)
        if product_id and hardware_id:
            version = self.get_reolink_firmware_api(product_id, hardware_id)
            if version:
                return version
        else:
            print(f"No known API mapping for {model} with hardware {hardware_version}")

        # Try form simulation
        version = self.simulate_form_search(model, hardware_version)
        if version:
            return version

        # Try direct download pages
        version = self.try_direct_download_page(model)
        if version:
            return version

        print("Could not find firmware through automated methods")
        return None

    def parse_version_string(self, version_str):
        """Parse version string for comparison"""
        clean_version = version_str.lower().replace('v', '')
        
        # For Reolink versions like "3.5.1.368_25010326", we need to compare the full string
        # Convert to a format that can be compared: "3.5.1.368.25010326"
        if '_' in clean_version:
            base_part, build_part = clean_version.split('_', 1)
            # Combine base version with build number for proper comparison
            comparable_version = f"{base_part}.{build_part}"
        else:
            comparable_version = clean_version
            
        try:
            return version.parse(comparable_version)
        except:
            # Fallback to string comparison if version parsing fails
            return clean_version

    def compare_versions(self, current_version, latest_version):
        """Compare current version with latest version"""
        if not latest_version:
            return False, "Could not determine latest version"

        try:
            current_parsed = self.parse_version_string(current_version)
            latest_parsed = self.parse_version_string(latest_version)

            if isinstance(current_parsed, str) or isinstance(latest_parsed, str):
                return current_version != latest_version, f"Current: {current_version}, Latest: {latest_version}"

            if latest_parsed > current_parsed:
                return True, f"🔔 New version available: {latest_version} (current: {current_version})"
            elif latest_parsed == current_parsed:
                return False, f"✅ You have the latest version: {current_version}"
            else:
                return False, f"Your version {current_version} is newer than listed {latest_version}"

        except Exception as e:
            return False, f"Error comparing versions: {e}"

    def check_for_updates(self, model, hardware_version, current_version):
        """Main method to check for firmware updates"""
        print(f"Checking firmware for {model} (HW: {hardware_version})")
        print(f"Current version: {current_version}")
        print("-" * 50)

        latest_version = self.search_firmware(model, hardware_version)

        if latest_version:
            has_update, message = self.compare_versions(current_version, latest_version)
            print(message)
            return has_update
        else:
            print("❌ Could not find firmware information automatically")
            print("💡 Try checking manually at: https://reolink.com/download-center/")
            print(f"   Search for model: {model}")
            print(f"   Hardware version: {hardware_version}")
            return False

def manual_check(config):
    """Open the download center in browser for manual checking"""
    import webbrowser

    device_config = config.get_device_config()
    model = device_config.get('model', 'UNKNOWN')
    hardware_version = device_config.get('hardware_version', 'UNKNOWN')

    print(f"Opening download center for manual check...")
    print(f"Look for model: {model}")
    print(f"Hardware version: {hardware_version}")

    if config.get_setting('auto_open_browser_on_manual', True):
        webbrowser.open("https://reolink.com/download-center/")

    while True:
        response = input("\nDid you find a newer version? (y/n/version): ").strip().lower()
        if response == 'y':
            version = input("Enter the version you found: ").strip()
            if version:
                return version
        elif response == 'n':
            return None
        elif response.startswith('v') or any(c.isdigit() for c in response):
            return response
        else:
            print("Please enter 'y', 'n', or the version number")

def main():
    import sys
    
    # Load configuration
    config = ReolinkConfig()
    device_config = config.get_device_config()
    
    model = device_config.get('model')
    hardware_version = device_config.get('hardware_version')
    current_version = device_config.get('current_firmware_version')
    
    if not all([model, hardware_version, current_version]):
        print("❌ Configuration incomplete!")
        print(f"Config file: {config.get_config_file_path()}")
        print("Please ensure model, hardware_version, and current_firmware_version are set.")
        sys.exit(1)

    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--manual':
            latest_version = manual_check(config)
            if latest_version:
                checker = ReolinkFirmwareChecker()
                has_update, message = checker.compare_versions(current_version, latest_version)
                print(f"\n{message}")
                if has_update:
                    # Ask if user wants to update config
                    update_config = input("\nUpdate config with this version? (y/n): ").strip().lower()
                    if update_config == 'y':
                        config.update_firmware_version(latest_version)
                    print("\n🔔 Update available!")
                    sys.exit(1)
                else:
                    print("\n✅ No updates needed")
                    sys.exit(0)
            else:
                print("\n✅ No updates found")
                sys.exit(0)
        elif sys.argv[1] == '--config':
            config.show_config()
            sys.exit(0)
        elif sys.argv[1] == '--update-version':
            if len(sys.argv) > 2:
                new_version = sys.argv[2]
                config.update_firmware_version(new_version)
                sys.exit(0)
            else:
                print("Usage: --update-version <version>")
                sys.exit(1)
        else:
            print("Usage: reolink_firmware_check.py [--manual|--config|--update-version <version>]")
            sys.exit(1)

    # Automatic check
    checker = ReolinkFirmwareChecker()
    has_update = checker.check_for_updates(model, hardware_version, current_version)

    if has_update:
        print("\n🔔 Update available!")
        sys.exit(1)
    else:
        print("\n✅ No updates needed")
        print(f"\n💡 Try: poetry run python reolink_firmware_check.py --manual")
        print(f"💡 Config: poetry run python reolink_firmware_check.py --config")
        sys.exit(0)

if __name__ == "__main__":
    main()
