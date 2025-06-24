# Reolink Firmware Checker Project

## Project Overview
Python script to check for firmware updates on Reolink NVR devices using their official API.

## Key Technical Learnings

### Web Scraping Strategy for Modern JavaScript Sites
- **Don't rely on static HTML analysis** for JavaScript-heavy sites like Reolink
- When initial web scraping fails, immediately pivot to dynamic analysis
- **Ask users to inspect network traffic**: "Open browser dev tools (F12), go to Network tab, perform the action, and share what API calls are made"
- Modern web apps hide functionality behind JavaScript - static `WebFetch` won't reveal dynamic API endpoints

### Reolink API Discovery
- Found working endpoint: `https://reolink.com/wp-json/reo-v2/download/firmware/`
- Requires specific product and hardware version IDs (not model names)
- Example mapping: RLN8-410 + N2MB02 = dlProductId=33, hardwareVersion=231

## Commands to Remember

### Raspberry Pi / Headless Linux
```bash
# Install dependencies (REQUIRED for Raspberry Pi/headless systems)
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry install

# Run firmware check (recommended entry point)
poetry run python reolink_check.py

# Manual check mode  
poetry run python reolink_check.py --manual

# Configuration setup
poetry run python reolink_check.py --config
```

### macOS / Desktop Linux
```bash
# Install dependencies (standard installation)
poetry install

# Run firmware check
poetry run python reolink_check.py
```

## Architecture Notes
- Uses Poetry for dependency management (not pip)
- Script has both automatic API checking and manual fallback modes
- Proper version comparison using `packaging` library - **includes build numbers** (e.g., `_25010326`)
- Exit codes: 0 = no updates, 1 = update available
- **Raspberry Pi compatibility**: Uses `reolink_check.py` wrapper to handle keyring authentication issues

## Testing
- Comprehensive test suite using pytest
- Integration tests for API validation
- Unit tests for version comparison logic (prevents regression of build number bug)
- Mock tests for API response parsing
- Run with: `poetry run pytest` or `poetry run pytest -m "not integration"` to skip API calls

## Troubleshooting

### Raspberry Pi KeyRing Errors
If you see errors like `DBusErrorResponse` or `PromptDismissedException` during `poetry install`, this is because:
- Poetry tries to use the system keyring for credential storage
- Raspberry Pi headless systems lack the necessary desktop components
- **Solution**: Use `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry install`
- This disables keyring and has no security impact since we only use public packages

### Interactive Setup Issues
If the script hangs asking for device input:
- Create a `config` file in the project directory
- Use `poetry run python reolink_check.py --config` to set up interactively
- Or copy the default config from CLAUDE.md

## Session Tracking
**IMPORTANT**: At the end of each coding session, update the cost tracking table in README.md with:
- Date of session
- Approximate duration  
- Claude Code API costs (get from user)
- Brief notes about what was accomplished

This helps track the true cost of AI-assisted development for this project.