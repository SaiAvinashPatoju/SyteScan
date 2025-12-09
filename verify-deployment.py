#!/usr/bin/env python3
"""
SyteScan Progress Analyzer - Deployment Verification Script
This script verifies that all deployment components are properly configured.
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (NOT FOUND)")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status"""
    if os.path.isdir(dir_path):
        print(f"✓ {description}: {dir_path}")
        return True
    else:
        print(f"✗ {description}: {dir_path} (NOT FOUND)")
        return False

def verify_docker_files():
    """Verify Docker configuration files"""
    print("\n🐳 Docker Configuration")
    print("=" * 50)
    
    docker_files = [
        ("Dockerfile.frontend", "Frontend Dockerfile"),
        ("Dockerfile.backend", "Backend Dockerfile"),
        ("docker-compose.yml", "Docker Compose configuration"),
        (".env.example", "Environment variables example")
    ]
    
    all_present = True
    for file_path, description in docker_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def verify_backend_structure():
    """Verify backend structure and files"""
    print("\n🔧 Backend Structure")
    print("=" * 50)
    
    backend_files = [
        ("backend/main.py", "Main application file"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/app/config.py", "Configuration module"),
        ("backend/app/middleware/logging.py", "Logging middleware"),
        ("backend/app/monitoring/metrics.py", "Metrics monitoring"),
        ("backend/tests/test_e2e_workflow.py", "End-to-end tests")
    ]
    
    all_present = True
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def verify_frontend_structure():
    """Verify frontend structure and files"""
    print("\n🎨 Frontend Structure")
    print("=" * 50)
    
    frontend_files = [
        ("package.json", "Package configuration"),
        ("src/test/e2e-workflow.test.tsx", "End-to-end tests"),
        ("next.config.js", "Next.js configuration"),
        ("tailwind.config.js", "Tailwind CSS configuration")
    ]
    
    all_present = True
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def verify_documentation():
    """Verify documentation files"""
    print("\n📚 Documentation")
    print("=" * 50)
    
    doc_files = [
        ("DEVELOPMENT.md", "Development setup guide"),
        ("DEPLOYMENT.md", "Deployment guide"),
        ("README.md", "Project README")
    ]
    
    all_present = True
    for file_path, description in doc_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def verify_test_runners():
    """Verify test runner scripts"""
    print("\n🧪 Test Runners")
    print("=" * 50)
    
    test_files = [
        ("test-runner.sh", "Unix test runner script"),
        ("test-runner.bat", "Windows test runner script")
    ]
    
    all_present = True
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def check_package_json_scripts():
    """Check if package.json has required scripts"""
    print("\n📦 Package.json Scripts")
    print("=" * 50)
    
    try:
        with open("package.json", "r") as f:
            package_data = json.load(f)
        
        required_scripts = [
            "dev", "build", "start", "test", "test:e2e", "test:all"
        ]
        
        scripts = package_data.get("scripts", {})
        all_present = True
        
        for script in required_scripts:
            if script in scripts:
                print(f"✓ Script '{script}': {scripts[script]}")
            else:
                print(f"✗ Script '{script}': NOT FOUND")
                all_present = False
        
        return all_present
        
    except FileNotFoundError:
        print("✗ package.json not found")
        return False
    except json.JSONDecodeError:
        print("✗ package.json is not valid JSON")
        return False

def main():
    """Main verification function"""
    print("🚀 SyteScan Progress Analyzer - Deployment Verification")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all verification checks
    checks = [
        verify_docker_files(),
        verify_backend_structure(),
        verify_frontend_structure(),
        verify_documentation(),
        verify_test_runners(),
        check_package_json_scripts()
    ]
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 50)
    
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    if passed_checks == total_checks:
        print(f"✅ All {total_checks} verification checks passed!")
        print("\n🎉 Deployment configuration is complete and ready!")
        print("\nNext steps:")
        print("1. Run 'docker-compose up --build' to start the application")
        print("2. Run test suite with 'test-runner.bat' (Windows) or 'test-runner.sh' (Unix)")
        print("3. Check health endpoints at http://localhost:8000/health")
        return 0
    else:
        print(f"❌ {total_checks - passed_checks} out of {total_checks} checks failed")
        print("\nPlease fix the missing files/configurations before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())