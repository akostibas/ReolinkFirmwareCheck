# Reolink Firmware Checker

A Python script to check for new firmware versions for your Reolink NVR.

## Usage

```bash
# Install dependencies
poetry install

# Run automatic check (tries to scrape website)
poetry run python reolink_firmware_check.py

# Run manual check (opens browser for manual verification)
poetry run python reolink_firmware_check.py --manual
```

## Configuration

The first time you run the script, it will prompt you to enter your device information:
- Device model (e.g., RLN8-410)
- Hardware version (e.g., N2MB02)  
- Current firmware version (e.g., v3.5.1.368_25010326)

This information is saved to a local `config` file. You can:
- View current config: `poetry run python reolink_firmware_check.py --config`
- Update version: `poetry run python reolink_firmware_check.py --update-version v3.5.1.368_25010326`
- Edit the `config` file directly

## Exit Codes

- 0: No updates available
- 1: Update available

## Testing

Run the test suite to ensure everything works correctly:

```bash
# Install dev dependencies first
poetry install

# Run all tests (includes real API calls)
poetry run pytest

# Run only unit tests (skip API integration tests - faster)
poetry run pytest -m "not integration"

# Run with verbose output
poetry run pytest -v

# Run specific test categories
poetry run pytest test_reolink_firmware_check.py::TestVersionComparison -v  # Just version tests
poetry run pytest test_reolink_firmware_check.py::TestAPIEndpoint -v        # Just API tests
```

### Test Coverage
- **Version comparison logic** - Ensures build numbers are properly compared (prevents regression of the `_25010324` vs `_25010326` bug)
- **API endpoint validation** - Verifies the Reolink API is still working 
- **Response parsing** - Tests handling of API responses and edge cases
- **Model mappings** - Validates device model to API ID mappings

## Notes

Since Reolink's download center uses dynamic JavaScript content, the automatic scraping may not always work. Use `--manual` mode to open the download center in your browser and manually enter the latest version for comparison.