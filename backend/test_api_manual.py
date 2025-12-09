#!/usr/bin/env python3

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test project creation
    project_data = {
        "name": "Test Project",
        "requirements": ["chair", "table", "lamp"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/projects/",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Create project: {response.status_code}")
        if response.status_code == 201:
            project = response.json()
            print(f"Created project: {project}")
            
            # Test get project
            project_id = project["id"]
            get_response = requests.get(f"{base_url}/api/projects/{project_id}")
            print(f"Get project: {get_response.status_code} - {get_response.json()}")
            
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Project creation failed: {e}")

if __name__ == "__main__":
    test_api()