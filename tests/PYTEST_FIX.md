# Pytest Import Conflict Fix

## Problem
The original test structure had naming conflicts that caused pytest to fail with "import file mismatch" errors:

```
ERROR collecting unit/plugins/module_utils/test_dme.py
import file mismatch:
imported module 'test_dme' has this __file__ attribute:
  .../httpapi/test_dme.py
which is not the same as the test file we want to collect:
  .../module_utils/test_dme.py
```

## Root Cause
Multiple test files had the same basename (`test_dme.py`) in different directories, causing Python's import system to cache the first imported module and reject subsequent imports with the same name.

## Solution
Renamed all test files to have unique basenames that clearly indicate their purpose:

### Before (Conflicting Names)
```
tests/unit/plugins/
├── action/
│   ├── test_dme_command.py    # ❌ Conflicts with modules/
│   ├── test_dme_config.py     # ❌ Conflicts with modules/
│   └── test_dme_validate.py   # ❌ Conflicts with modules/
├── httpapi/
│   └── test_dme.py           # ❌ Conflicts with module_utils/
├── module_utils/
│   └── test_dme.py           # ❌ Conflicts with httpapi/
└── modules/
    ├── test_dme_command.py    # ❌ Conflicts with action/
    ├── test_dme_config.py     # ❌ Conflicts with action/
    └── test_dme_validate.py   # ❌ Conflicts with action/
```

### After (Unique Names)
```
tests/unit/plugins/
├── action/
│   ├── test_dme_command_action.py    # ✅ Unique
│   ├── test_dme_config_action.py     # ✅ Unique
│   └── test_dme_validate_action.py   # ✅ Unique
├── httpapi/
│   └── test_dme_httpapi.py           # ✅ Unique
├── module_utils/
│   └── test_dme_module_utils.py      # ✅ Unique
└── modules/
    ├── test_dme_command_module.py    # ✅ Unique
    ├── test_dme_config_module.py     # ✅ Unique
    └── test_dme_validate_module.py   # ✅ Unique
```

## Verification
Created `tests/verify_test_structure.py` script to automatically check for naming conflicts:

```bash
$ python3 tests/verify_test_structure.py
✅ All 8 test files have unique names
✅ Test structure verification PASSED
```

## Prevention
1. **Unique Naming Convention**: All test files now follow the pattern `test_{component}_{type}.py`
2. **Verification Script**: Automated check prevents future conflicts
3. **Updated Documentation**: README and scripts updated with new file names
4. **Cache Cleanup**: Added instructions to clean `__pycache__` directories

## Commands to Fix Similar Issues

If you encounter similar import conflicts:

```bash
# Clean cached files
find tests/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find tests/ -name "*.pyc" -delete 2>/dev/null || true

# Verify structure
python3 tests/verify_test_structure.py

# Run tests
pytest tests/unit/ -v
```

## Benefits
- ✅ No more import conflicts
- ✅ Clear test file organization
- ✅ Automated verification
- ✅ Better maintainability
- ✅ Clearer test purpose from filename
