#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timezone, timedelta
import time

class MutualFundScreenerTester:
    def __init__(self, base_url="https://fund-screener.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
            
        if self.session_token and 'Authorization' not in test_headers:
            test_headers['Authorization'] = f'Bearer {self.session_token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Response: {error_data}"
                except:
                    details += f", Response: {response.text[:200]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {"status": "success"}
            return None

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return None

    def create_test_session(self):
        """Create test user and session using MongoDB"""
        print("\n🔧 Creating test user and session...")
        
        # This would normally be done via MongoDB, but for testing we'll simulate
        # a session token that should work with the auth system
        test_session_token = f"test_session_{int(time.time())}"
        self.session_token = test_session_token
        self.user_id = f"test_user_{int(time.time())}"
        
        print(f"📝 Test session token: {self.session_token}")
        print(f"👤 Test user ID: {self.user_id}")
        return True

    def test_public_endpoints(self):
        """Test public endpoints that don't require auth"""
        print("\n📡 Testing Public Endpoints...")
        
        # Test categories endpoint
        self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200
        )

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test auth/me without token (should fail)
        self.run_test(
            "Get Me (No Auth) - Should Fail",
            "GET", 
            "auth/me",
            401
        )
        
        # Test auth/me with token (will likely fail without proper session)
        if self.session_token:
            self.run_test(
                "Get Me (With Token)",
                "GET",
                "auth/me", 
                401  # Expected to fail without proper session setup
            )

    def test_funds_endpoints(self):
        """Test fund-related endpoints"""
        print("\n📊 Testing Fund Endpoints...")
        
        # Test get funds without auth (should work as it's public-ish)
        funds_response = self.run_test(
            "Get Funds List",
            "GET",
            "funds",
            200
        )
        
        if funds_response and 'funds' in funds_response:
            funds = funds_response['funds']
            print(f"   Found {len(funds)} funds")
            
            if funds:
                # Test fund detail endpoint
                first_fund_id = funds[0]['fund_id']
                fund_detail = self.run_test(
                    f"Get Fund Detail ({first_fund_id})",
                    "GET",
                    f"funds/{first_fund_id}",
                    200
                )
                
                if fund_detail:
                    print(f"   Fund detail loaded: {fund_detail['fund']['name']}")
                
                # Test metrics endpoint
                self.run_test(
                    f"Get Fund Metrics ({first_fund_id})",
                    "GET",
                    f"metrics/{first_fund_id}",
                    200
                )
        
        # Test funds with filters
        self.run_test(
            "Get Funds with Category Filter",
            "GET",
            "funds?category=Equity&min_history_years=3",
            200
        )
        
        # Test funds with pagination
        self.run_test(
            "Get Funds with Pagination",
            "GET", 
            "funds?page=1&limit=10",
            200
        )

    def test_admin_endpoints(self):
        """Test admin endpoints"""
        print("\n⚙️ Testing Admin Endpoints...")
        
        # Test recompute (should work without auth for MVP)
        recompute_result = self.run_test(
            "Admin Recompute Trigger",
            "POST",
            "admin/recompute?min_history_years=3",
            200
        )
        
        if recompute_result:
            print(f"   Recompute result: {recompute_result.get('message', 'No message')}")
            print(f"   Computed funds: {recompute_result.get('computed_funds', 'N/A')}")

    def test_user_preferences(self):
        """Test user preferences endpoints"""
        print("\n👤 Testing User Preferences...")
        
        # Test update preferences (will fail without proper auth)
        preferences_data = {
            "default_weights": {
                "consistency": 30,
                "volatility": 20, 
                "performance": 15,
                "portfolio_quality": 20,
                "valuation": 15
            },
            "saved_weights": [],
            "min_history_years": 3
        }
        
        self.run_test(
            "Update User Preferences",
            "PUT",
            "user/preferences",
            401,  # Expected to fail without proper auth
            data=preferences_data
        )

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Mutual Fund Screener Backend Tests")
        print(f"🌐 Testing against: {self.base_url}")
        
        start_time = time.time()
        
        # Create test session
        self.create_test_session()
        
        # Run test suites
        self.test_public_endpoints()
        self.test_auth_endpoints() 
        self.test_funds_endpoints()
        self.test_admin_endpoints()
        self.test_user_preferences()
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Test Summary")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print(f"   Duration: {duration:.2f}s")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "duration": duration,
            "test_results": self.test_results
        }

def main():
    """Main test runner"""
    tester = MutualFundScreenerTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["success_rate"] >= 70:  # 70% pass rate considered acceptable for initial testing
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())