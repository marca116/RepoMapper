#!/usr/bin/env python3
"""
Simple test script for RepoMap functionality.
"""

import tempfile
import os
from pathlib import Path
from repomap import RepoMap, find_src_files

def test_basic_functionality():
    """Test basic RepoMap functionality."""
    
    # Create a temporary directory with some Python files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple Python file
        test_file = temp_path / "test.py"
        test_file.write_text("""
def hello_world():
    '''A simple greeting function.'''
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
    tc = TestClass()
    print(tc.get_value())
""")
        
        # Create a README file
        readme_file = temp_path / "README.md"
        readme_file.write_text("# Test Project\n\nThis is a test project.")
        
        # Test find_src_files
        src_files = find_src_files(str(temp_path))
        print(f"Found {len(src_files)} files:")
        for f in src_files:
            print(f"  {f}")
        
        # Test RepoMap
        repo_map = RepoMap(
            map_tokens=1024,
            root=str(temp_path),
            verbose=True
        )
        
        # Generate map
        map_content = repo_map.get_repo_map(
            chat_files=[],
            other_files=src_files
        )
        
        if map_content:
            print("\n" + "="*50)
            print("GENERATED REPOSITORY MAP:")
            print("="*50)
            print(map_content)
        else:
            print("No map content generated")

if __name__ == "__main__":
    test_basic_functionality()
