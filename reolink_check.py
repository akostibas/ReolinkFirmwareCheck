#!/usr/bin/env python3
"""
Wrapper script to set environment variables for Raspberry Pi compatibility
"""
import os
import sys

def main():
    # Set keyring backend to null for Raspberry Pi compatibility
    os.environ['PYTHON_KEYRING_BACKEND'] = 'keyring.backends.null.Keyring'
    
    # Import and run the actual script
    from reolink_firmware_check import main as reolink_main
    reolink_main()

if __name__ == "__main__":
    main()