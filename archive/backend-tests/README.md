# Backend Test Files Archive

This directory contains backend test files that are not part of the main test suite in `backend/tests/`.

## Files

These test files were moved here as they appear to be:
- Manual testing scripts
- One-time verification scripts
- Not integrated into the main pytest test suite

## Files Archived

- `test_api_functionality.py` - API functionality tests
- `test_data_extraction_config.py` - Data extraction configuration tests
- `test_data_extraction_real_api.py` - Real API tests for data extraction
- `test_env_config.py` - Environment configuration tests
- `test_env_security.py` - Environment security tests
- `test_jailbreak_evaluation.py` - Jailbreak evaluation tests
- `test_jailbreak_real_api.py` - Real API tests for jailbreak
- `test_jailbreak_structure.py` - Jailbreak structure tests
- `test_real_api_sample.py` - Real API sample tests

## Note

If you need to run these tests, you can execute them from this directory or move them back to the `backend/` directory.

The main test suite is located in `backend/tests/` and should be run using:
```bash
pytest backend/tests/
```

