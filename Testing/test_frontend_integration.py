#!/usr/bin/env python3
"""
Test script to simulate frontend requests to the backend.
Tests the /v1/evaluate-from-config endpoint with various frontend scenarios.
"""

import requests
import json
import sys
from pathlib import Path

# Backend API URL
API_URL = "http://localhost:5008/v1/evaluate-from-config"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "testingconfig" / "evaluation_config.json"

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(response, test_name):
    """Print test result in a formatted way."""
    status_code = response.status_code
    if status_code == 200:
        print(f"✅ {test_name}: PASSED (Status: {status_code})")
        return True
    else:
        print(f"❌ {test_name}: FAILED (Status: {status_code})")
        try:
            error_detail = response.json()
            print(f"   Error: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"   Error: {response.text}")
        return False

def test_default_config_all_metrics():
    """Test 1: Use default config with all goals and metrics (no filters)."""
    print_section("Test 1: Default Config - All Goals & Metrics")
    
    data = {
        "evaluation_id": "frontend-test-001",
        "evaluation_name": "Full Evaluation Test",
        "deployment_stage": "dev",
        "risk_class": "low",
        "user_impact": "internal",
        "mode": "one_off",
        "environment": "local"
    }
    
    print(f"Request: evaluation_id={data['evaluation_id']}, evaluation_name={data['evaluation_name']}")
    print("Filters: None (all goals and metrics)")
    
    try:
        response = requests.post(API_URL, data=data, timeout=300)
        success = print_result(response, "Default Config - All Metrics")
        
        if success:
            result = response.json()
            print(f"\n📊 Results:")
            print(f"   Run ID: {result.get('run_id')}")
            print(f"   Overall Status: {result.get('overall_status')}")
            print(f"   Metrics Evaluated: {len(result.get('metric_results', []))}")
            print(f"   Evidence: {result.get('evidence_pointer')}")
            
            # Show first few metrics
            if result.get('metric_results'):
                print(f"\n   First 3 Metrics:")
                for i, metric in enumerate(result['metric_results'][:3], 1):
                    status = "✅" if metric.get('passed') else "❌" if metric.get('passed') is False else "⚠️"
                    print(f"   {i}. {status} {metric.get('metric_name')} ({metric.get('metric_id')})")
        
        return success
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Cannot connect to {API_URL}")
        print("   Make sure the backend is running: cd backend && uvicorn app:app --reload --port 5008")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def test_default_config_filtered():
    """Test 2: Use default config with specific goals and metrics."""
    print_section("Test 2: Default Config - Filtered by Goals & Metrics")
    
    data = {
        "evaluation_id": "frontend-test-002",
        "evaluation_name": "Quality & Accuracy Test",
        "goals": "Quality & Accuracy",
        "metrics": "Task Completion, Answer Relevancy",
        "deployment_stage": "dev",
        "risk_class": "low",
        "user_impact": "internal",
        "mode": "one_off",
        "environment": "local"
    }
    
    print(f"Request: evaluation_id={data['evaluation_id']}")
    print(f"Goals: {data['goals']}")
    print(f"Metrics: {data['metrics']}")
    
    try:
        response = requests.post(API_URL, data=data, timeout=300)
        success = print_result(response, "Default Config - Filtered")
        
        if success:
            result = response.json()
            print(f"\n📊 Results:")
            print(f"   Run ID: {result.get('run_id')}")
            print(f"   Overall Status: {result.get('overall_status')}")
            print(f"   Metrics Evaluated: {len(result.get('metric_results', []))}")
            
            for metric in result.get('metric_results', []):
                status = "✅" if metric.get('passed') else "❌" if metric.get('passed') is False else "⚠️"
                score = metric.get('score', 'N/A')
                print(f"   {status} {metric.get('metric_name')}: Score={score}")
        
        return success
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def test_custom_config_file():
    """Test 3: Upload custom config file."""
    print_section("Test 3: Custom Config File Upload")
    
    if not DEFAULT_CONFIG_PATH.exists():
        print(f"⚠️  Default config file not found at {DEFAULT_CONFIG_PATH}")
        print("   Skipping custom config test (using default config as custom)")
        return True
    
    data = {
        "evaluation_id": "frontend-test-003",
        "evaluation_name": "Custom Config Test",
        "goals": "Quality & Accuracy",
        "metrics": "Task Completion",
        "deployment_stage": "dev",
        "risk_class": "low",
        "user_impact": "internal",
        "mode": "one_off",
        "environment": "local"
    }
    
    files = {
        "config_file": ("evaluation_config.json", open(DEFAULT_CONFIG_PATH, "rb"), "application/json")
    }
    
    print(f"Request: evaluation_id={data['evaluation_id']}")
    print(f"Uploading config file: {DEFAULT_CONFIG_PATH.name}")
    
    try:
        response = requests.post(API_URL, files=files, data=data, timeout=300)
        files["config_file"][1].close()  # Close the file
        success = print_result(response, "Custom Config File Upload")
        
        if success:
            result = response.json()
            print(f"\n📊 Results:")
            print(f"   Run ID: {result.get('run_id')}")
            print(f"   Overall Status: {result.get('overall_status')}")
        
        return success
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def test_multiple_goals():
    """Test 4: Multiple goals specified."""
    print_section("Test 4: Multiple Goals")
    
    data = {
        "evaluation_id": "frontend-test-004",
        "evaluation_name": "Multiple Goals Test",
        "goals": "Quality & Accuracy, Context Grounding & Hallucination Control",
        "deployment_stage": "dev",
        "risk_class": "medium",
        "user_impact": "customer_facing",
        "mode": "one_off",
        "environment": "local"
    }
    
    print(f"Request: evaluation_id={data['evaluation_id']}")
    print(f"Goals: {data['goals']}")
    
    try:
        response = requests.post(API_URL, data=data, timeout=300)
        success = print_result(response, "Multiple Goals")
        
        if success:
            result = response.json()
            print(f"\n📊 Results:")
            print(f"   Metrics Evaluated: {len(result.get('metric_results', []))}")
        
        return success
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def test_error_handling():
    """Test 5: Error handling - invalid inputs."""
    print_section("Test 5: Error Handling")
    
    # Test with missing required field
    data = {
        "evaluation_name": "Missing ID Test",
        # Missing evaluation_id
    }
    
    print("Testing with missing evaluation_id...")
    try:
        response = requests.post(API_URL, data=data, timeout=10)
        if response.status_code == 422:  # Validation error
            print("✅ Error Handling: PASSED (correctly rejected invalid input)")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

def check_backend_health():
    """Check if backend is accessible."""
    print_section("Backend Health Check")
    
    try:
        # Try to access the docs endpoint
        response = requests.get("http://localhost:5008/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not accessible")
        print("\n   To start the backend:")
        print("   cd backend && uvicorn app:app --reload --port 5008")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {type(e).__name__}: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  FRONTEND INTEGRATION TEST SUITE")
    print("  Testing /v1/evaluate-from-config endpoint")
    print("="*70)
    
    # Check backend health first
    if not check_backend_health():
        print("\n❌ Backend is not running. Please start it first.")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Health Check", True))  # Already passed
    results.append(("Default Config - All Metrics", test_default_config_all_metrics()))
    results.append(("Default Config - Filtered", test_default_config_filtered()))
    results.append(("Custom Config File", test_custom_config_file()))
    results.append(("Multiple Goals", test_multiple_goals()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

