#!/usr/bin/env python3
"""
Tests for Reolink Firmware Checker
"""

import pytest
import requests_mock
from packaging import version
from reolink_firmware_check import ReolinkFirmwareChecker
from config import ReolinkConfig


class TestVersionComparison:
    """Test version parsing and comparison logic"""
    
    def setup_method(self):
        self.checker = ReolinkFirmwareChecker()
    
    def test_parse_version_with_build_number(self):
        """Test parsing versions with build numbers like v3.5.1.368_25010326"""
        # Test with 'v' prefix
        parsed = self.checker.parse_version_string("v3.5.1.368_25010326")
        assert isinstance(parsed, version.Version)
        
        # Test without 'v' prefix  
        parsed_no_v = self.checker.parse_version_string("3.5.1.368_25010326")
        assert isinstance(parsed_no_v, version.Version)
        
        # They should be equal
        assert parsed == parsed_no_v
    
    def test_parse_version_without_build_number(self):
        """Test parsing simple versions like v3.5.1"""
        parsed = self.checker.parse_version_string("v3.5.1")
        assert isinstance(parsed, version.Version)
        assert str(parsed) == "3.5.1"
    
    def test_version_comparison_build_numbers(self):
        """Test that build numbers are properly compared"""
        # These should be different - the bug we fixed
        current = "v3.5.1.368_25010324"
        latest = "v3.5.1.368_25010326"
        
        has_update, message = self.checker.compare_versions(current, latest)
        assert has_update == True
        assert "New version available" in message
        assert "25010326" in message and "25010324" in message
    
    def test_version_comparison_same_versions(self):
        """Test that identical versions are detected as same"""
        current = "v3.5.1.368_25010326"
        latest = "v3.5.1.368_25010326"
        
        has_update, message = self.checker.compare_versions(current, latest)
        assert has_update == False
        assert "latest version" in message.lower()
    
    def test_version_comparison_major_difference(self):
        """Test comparison with different major versions"""
        current = "v3.4.0.293_24010832"
        latest = "v3.5.1.368_25010326"
        
        has_update, message = self.checker.compare_versions(current, latest)
        assert has_update == True
        assert "New version available" in message
    
    def test_version_comparison_newer_current(self):
        """Test when current version is newer than 'latest'"""
        current = "v3.6.0.400_26010101"
        latest = "v3.5.1.368_25010326"
        
        has_update, message = self.checker.compare_versions(current, latest)
        assert has_update == False
        assert "newer than listed" in message


class TestAPIEndpoint:
    """Test the actual Reolink API endpoint"""
    
    def setup_method(self):
        self.checker = ReolinkFirmwareChecker()
    
    @pytest.mark.integration  # Mark as integration test
    def test_api_endpoint_validity(self):
        """Test that the API endpoint is still valid and returns expected data"""
        # Use default config values for testing
        model = "RLN8-410"
        hardware_version = "N2MB02"
        
        product_id, hardware_id = self.checker.get_product_and_hardware_ids(model, hardware_version)
        
        # Should find mapping for our known model
        assert product_id == 33
        assert hardware_id == 231
        
        # Test actual API call
        latest_version = self.checker.get_reolink_firmware_api(product_id, hardware_id)
        
        # Should get a version back
        assert latest_version is not None
        assert isinstance(latest_version, str)
        assert "v3." in latest_version  # Should be a v3.x version
        assert "_" in latest_version    # Should have build number
    
    def test_api_response_parsing(self):
        """Test parsing of API response with mock data"""
        # Mock response based on real API response structure
        mock_response = {
            'result': {'code': 0, 'msg': 'ok'},
            'data': [{
                'title': 'RLN8-410 (NVR)',
                'firmwares': [
                    {
                        'id': 484,
                        'version': 'v3.4.0.293_24010832',
                        'updated_at': 1708309607000
                    },
                    {
                        'id': 712,
                        'version': 'v3.5.1.368_25010326',
                        'updated_at': 1736325210000  # Higher timestamp = newer
                    }
                ]
            }]
        }
        
        version = self.checker.extract_version_from_api_response(mock_response)
        assert version == 'v3.5.1.368_25010326'  # Should pick the newer one
    
    def test_api_response_parsing_empty(self):
        """Test parsing with empty/invalid responses"""
        assert self.checker.extract_version_from_api_response(None) is None
        assert self.checker.extract_version_from_api_response({}) is None
        assert self.checker.extract_version_from_api_response({'data': []}) is None


class TestEndToEnd:
    """End-to-end tests with mocked API"""
    
    def setup_method(self):
        self.checker = ReolinkFirmwareChecker()
    
    def test_update_detection_with_mock(self):
        """Test full update detection flow with mocked API"""
        # Mock the API response
        mock_response = {
            'result': {'code': 0, 'msg': 'ok'},
            'data': [{
                'title': 'RLN8-410 (NVR)',
                'firmwares': [{
                    'id': 712,
                    'version': 'v3.5.1.368_25010326',
                    'updated_at': 1736325210000
                }]
            }]
        }
        
        with requests_mock.Mocker() as m:
            m.get(
                'https://reolink.com/wp-json/reo-v2/download/firmware/',
                json=mock_response
            )
            
            # Test with older version - should detect update
            model = "RLN8-410"
            hardware_version = "N2MB02"
            
            has_update = self.checker.check_for_updates(
                model, 
                hardware_version, 
                "v3.5.1.368_25010324"  # Older build
            )
            assert has_update == True
            
            # Test with same version - should not detect update  
            has_update = self.checker.check_for_updates(
                model,
                hardware_version, 
                "v3.5.1.368_25010326"  # Same version
            )
            assert has_update == False


class TestModelMappings:
    """Test model to API ID mappings"""
    
    def setup_method(self):
        self.checker = ReolinkFirmwareChecker()
    
    def test_known_model_mapping(self):
        """Test that known models map to correct IDs"""
        product_id, hardware_id = self.checker.get_product_and_hardware_ids("RLN8-410", "N2MB02")
        assert product_id == 33
        assert hardware_id == 231
    
    def test_unknown_model_mapping(self):
        """Test that unknown models return None"""
        product_id, hardware_id = self.checker.get_product_and_hardware_ids("UNKNOWN_MODEL", "UNKNOWN_HW")
        assert product_id is None
        assert hardware_id is None


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])