# Legacy Files Archive

This directory contains legacy files that have been replaced by the modular backend structure.

## Files

- **`simple_api_server.py`** - Original simple API server (replaced by `backend/api/main.py`)
- **`unified_api_server.py`** - Original monolithic API server (refactored into `backend/api/main.py`)
- **`verify_flow.py`** - Original verification script (updated version in `backend/scripts/verify_flow.py`)

## Migration

These files were migrated during the backend restructure. The current active backend is:
- **Entry Point**: `backend/run.py`
- **Main API**: `backend/api/main.py`
- **Scripts**: `backend/scripts/`

See `backend/BACKEND_RESTRUCTURE.md` for details on the migration.

## Note

These files are kept for reference only and are not actively used. The updated versions with proper paths and modular structure are in the `backend/` directory.

