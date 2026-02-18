"""
Script to update all MongoDB connections from localhost to environment variable
"""
import os
import re

# Pattern to find and replace
OLD_PATTERN = r'client = MongoClient\("mongodb://localhost:27017"\)'
NEW_CODE = '''import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())'''

def update_file(filepath):
    """Update a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file needs updating
        if 'MongoClient("mongodb://localhost:27017")' not in content:
            return False
        
        # Check if already updated
        if 'load_dotenv()' in content and 'MONGO_URI' in content:
            print(f"✓ Already updated: {filepath}")
            return False
        
        # Find the import section
        lines = content.split('\n')
        
        # Find where MongoClient is imported
        import_index = -1
        for i, line in enumerate(lines):
            if 'from pymongo import MongoClient' in line:
                import_index = i
                break
        
        if import_index == -1:
            print(f"✗ Could not find MongoClient import in: {filepath}")
            return False
        
        # Replace the old connection pattern
        new_content = re.sub(
            r'client = MongoClient\("mongodb://localhost:27017"\)',
            'client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())',
            content
        )
        
        # Add necessary imports after the MongoClient import
        if 'import os' not in new_content:
            lines = new_content.split('\n')
            lines.insert(import_index, 'import os')
            new_content = '\n'.join(lines)
            import_index += 1
        
        if 'from dotenv import load_dotenv' not in new_content:
            lines = new_content.split('\n')
            lines.insert(import_index, 'from dotenv import load_dotenv')
            new_content = '\n'.join(lines)
            import_index += 1
        
        if 'import certifi' not in new_content:
            lines = new_content.split('\n')
            lines.insert(import_index, 'import certifi')
            new_content = '\n'.join(lines)
            import_index += 1
        
        # Add load_dotenv() and MONGO_URI before the client connection
        if 'load_dotenv()' not in new_content:
            new_content = re.sub(
                r'(client = MongoClient\(MONGO_URI, tlsCAFile=certifi\.where\(\)\))',
                r'load_dotenv()\n\nMONGO_URI = os.getenv("MONGO_URI")\n\n\1',
                new_content
            )
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Updated: {filepath}")
        return True
        
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def find_and_update_files(root_dir):
    """Find all Python files with localhost connections and update them"""
    updated_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip virtual environments and cache directories
        if 'venv' in dirpath or '__pycache__' in dirpath or '.git' in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                if update_file(filepath):
                    updated_count += 1
    
    return updated_count

if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Connection Updater")
    print("=" * 60)
    print()
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    count = find_and_update_files(backend_dir)
    
    print()
    print("=" * 60)
    print(f"✓ Updated {count} files")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install required packages: pip install python-dotenv certifi")
    print("2. Verify your .env file contains: MONGO_URI=<your_connection_string>")
    print("3. Test a script to ensure connection works")
