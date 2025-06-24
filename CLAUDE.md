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
```bash
# Install dependencies
poetry install

# Run firmware check
poetry run python reolink_firmware_check.py

# Manual check mode
poetry run python reolink_firmware_check.py --manual
```

## Architecture Notes
- Uses Poetry for dependency management (not pip)
- Script has both automatic API checking and manual fallback modes
- Proper version comparison using `packaging` library - **includes build numbers** (e.g., `_25010326`)
- Exit codes: 0 = no updates, 1 = update available

## Testing
- Comprehensive test suite using pytest
- Integration tests for API validation
- Unit tests for version comparison logic (prevents regression of build number bug)
- Mock tests for API response parsing
- Run with: `poetry run pytest` or `poetry run pytest -m "not integration"` to skip API calls

## Session Tracking
**IMPORTANT**: At the end of each coding session, update the cost tracking table in README.md with:
- Date of session
- Approximate duration  
- Claude Code API costs (get from user)
- Brief notes about what was accomplished

This helps track the true cost of AI-assisted development for this project.