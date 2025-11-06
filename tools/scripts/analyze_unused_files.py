#!/usr/bin/env python3
"""
Analyze unused files in the project.
Identifies files that are not imported, referenced, or used anywhere.
"""
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Set, List, Dict

# Directories to ignore
IGNORE_DIRS = {
    '__pycache__', 'node_modules', '.git', '.next', 'venv', 'env',
    'dist', 'build', '.pytest_cache', 'coverage', '.mypy_cache',
    'archive', 'results', 'data'  # Data files are used but not imported
}

# File patterns to ignore
IGNORE_PATTERNS = {
    r'\.pyc$', r'\.pyo$', r'\.log$', r'\.json$', r'\.csv$', r'\.jsonl$',
    r'\.md$', r'\.txt$', r'\.toml$', r'\.lock$', r'\.example$',
    r'\.env$', r'\.gitignore$', r'\.dockerignore$', r'\.DS_Store$',
    r'package\.json$', r'requirements.*\.txt$', r'pytest\.ini$',
    r'tsconfig\.json$', r'next\.config\.mjs$', r'postcss\.config\.mjs$',
    r'tailwind\.config\.ts$', r'components\.json$', r'vercel\.json$',
    r'\.ipynb$', r'\.png$', r'\.jpg$', r'\.svg$', r'\.ico$'
}

# Entry points - files that are definitely used
ENTRY_POINTS = {
    'backend/run.py',
    'backend/api/main.py',
    'frontend/app/layout.tsx',
    'frontend/app/page.tsx',
    'frontend/next.config.mjs',
}

def should_ignore_file(filepath: str) -> bool:
    """Check if file should be ignored."""
    # Check ignore patterns
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, filepath):
            return True
    
    # Check ignore dirs
    parts = Path(filepath).parts
    if any(part in IGNORE_DIRS for part in parts):
        return True
    
    return False

def get_all_python_files(root: Path) -> Set[str]:
    """Get all Python files in the project."""
    files = set()
    for py_file in root.rglob('*.py'):
        rel_path = str(py_file.relative_to(root))
        if not should_ignore_file(rel_path):
            files.add(rel_path)
    return files

def get_all_tsx_files(root: Path) -> Set[str]:
    """Get all TypeScript/TSX files in the project."""
    files = set()
    for ext in ['*.tsx', '*.ts']:
        for ts_file in root.rglob(ext):
            rel_path = str(ts_file.relative_to(root))
            if not should_ignore_file(rel_path):
                files.add(rel_path)
    return files

def extract_imports_from_python(content: str) -> Set[str]:
    """Extract import statements from Python code."""
    imports = set()
    
    # Standard imports: import module, from module import ...
    patterns = [
        r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
        r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
    ]
    
    for line in content.split('\n'):
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                imports.add(module)
    
    return imports

def extract_imports_from_tsx(content: str) -> Set[str]:
    """Extract import statements from TypeScript/TSX code."""
    imports = set()
    
    # ES6 imports: import ... from '...'
    pattern = r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, content)
    for match in matches:
        # Remove file extensions and resolve relative paths
        if match.startswith('.'):
            imports.add(match)
        else:
            imports.add(match.split('/')[0])  # Package name
    
    return imports

def normalize_module_path(module: str, current_file: str) -> str:
    """Normalize module path to file path."""
    # Convert Python module path to file path
    if module.startswith('backend.'):
        path = module.replace('.', '/') + '.py'
        return path
    elif module.startswith('platform.'):
        path = module.replace('.', '/') + '.py'
        return path
    elif module.startswith('tests.'):
        path = module.replace('.', '/') + '.py'
        return path
    
    # Relative imports
    if '.' in module and not module.startswith('.'):
        # Try to resolve relative to current file
        current_dir = os.path.dirname(current_file)
        potential_path = os.path.join(current_dir, module.replace('.', '/') + '.py')
        if os.path.exists(potential_path):
            return potential_path
    
    return module

def find_file_references(root: Path) -> Dict[str, Set[str]]:
    """Find all file references in the codebase."""
    references = defaultdict(set)
    all_files = get_all_python_files(root) | get_all_tsx_files(root)
    
    for file_path in all_files:
        full_path = root / file_path
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if file_path.endswith('.py'):
                imports = extract_imports_from_python(content)
            else:
                imports = extract_imports_from_tsx(content)
            
            for imp in imports:
                # Try to resolve to actual file
                normalized = normalize_module_path(imp, file_path)
                if normalized in all_files:
                    references[normalized].add(file_path)
        except Exception as e:
            pass  # Skip files that can't be read
    
    return references

def find_unused_files(root: Path) -> List[Dict]:
    """Find unused files in the project."""
    all_py_files = get_all_python_files(root)
    all_tsx_files = get_all_tsx_files(root)
    all_files = all_py_files | all_tsx_files
    
    # Get references
    references = find_file_references(root)
    
    # Files that are definitely used
    used_files = set(ENTRY_POINTS)
    used_files.update(references.keys())
    
    # Also check for files that reference other files
    for ref_file in references.values():
        used_files.update(ref_file)
    
    # Find unused files
    unused = []
    for file_path in sorted(all_files):
        if file_path not in used_files:
            # Check if it's a test file (might be run separately)
            is_test = 'test' in file_path.lower() or 'spec' in file_path.lower()
            
            unused.append({
                'path': file_path,
                'type': 'test' if is_test else 'code',
                'size': (root / file_path).stat().st_size if (root / file_path).exists() else 0
            })
    
    return unused

def find_unused_directories(root: Path) -> List[str]:
    """Find potentially unused directories."""
    unused_dirs = []
    
    for dir_path in root.rglob('*'):
        if not dir_path.is_dir():
            continue
        
        rel_path = str(dir_path.relative_to(root))
        
        # Skip ignored directories
        if any(part in IGNORE_DIRS for part in dir_path.parts):
            continue
        
        # Check if directory has any Python/TSX files
        has_code = False
        for ext in ['*.py', '*.tsx', '*.ts']:
            if list(dir_path.rglob(ext)):
                has_code = True
                break
        
        if not has_code:
            # Check if it's empty or only has ignored files
            files = list(dir_path.iterdir())
            if not files or all(f.name.startswith('.') for f in files):
                unused_dirs.append(rel_path)
    
    return sorted(unused_dirs)

if __name__ == '__main__':
    root = Path(__file__).parent.parent.parent
    
    print("🔍 Analyzing unused files...\n")
    
    # Find unused files
    unused_files = find_unused_files(root)
    
    # Find unused directories
    unused_dirs = find_unused_directories(root)
    
    # Print results
    print("=" * 80)
    print("UNUSED FILES")
    print("=" * 80)
    
    if unused_files:
        # Group by type
        test_files = [f for f in unused_files if f['type'] == 'test']
        code_files = [f for f in unused_files if f['type'] == 'code']
        
        if code_files:
            print(f"\n📄 Code Files ({len(code_files)}):")
            for f in code_files[:50]:  # Limit output
                size_kb = f['size'] / 1024
                print(f"  - {f['path']} ({size_kb:.1f} KB)")
            if len(code_files) > 50:
                print(f"  ... and {len(code_files) - 50} more")
        
        if test_files:
            print(f"\n🧪 Test Files ({len(test_files)}):")
            for f in test_files[:30]:
                size_kb = f['size'] / 1024
                print(f"  - {f['path']} ({size_kb:.1f} KB)")
            if len(test_files) > 30:
                print(f"  ... and {len(test_files) - 30} more")
    else:
        print("\n✅ No unused files found!")
    
    print("\n" + "=" * 80)
    print("POTENTIALLY UNUSED DIRECTORIES")
    print("=" * 80)
    
    if unused_dirs:
        for dir_path in unused_dirs[:30]:
            print(f"  - {dir_path}/")
        if len(unused_dirs) > 30:
            print(f"  ... and {len(unused_dirs) - 30} more")
    else:
        print("\n✅ No unused directories found!")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY")
    print("=" * 80)
    print(f"Total unused files: {len(unused_files)}")
    print(f"  - Code files: {len([f for f in unused_files if f['type'] == 'code'])}")
    print(f"  - Test files: {len([f for f in unused_files if f['type'] == 'test'])}")
    print(f"Potentially unused directories: {len(unused_dirs)}")

