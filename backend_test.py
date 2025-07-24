#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Crypto Investment Platform
Tests all core functionalities including auth, investments, bot users, and admin features.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://d1db1c13-27d3-436a-899f-da07a09336fb.preview.emergentagent.com/api"

class CryptoInvestmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_user_email = None
        self.test_results = {
            "auth_system": {"passed": False, "details": []},
            "investment_management": {"passed": False, "details": []},
            "bot_users": {"passed": False, "details": []},
            "admin_panel": {"passed": False, "details": []},
            "asset_management": {"passed": False, "details": []}
        }
        
    def log_result(self, category, message, success=True):
        """Log test result with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ PASS" if success else "❌ FAIL"
        log_message = f"[{timestamp}] {status}: {message}"
        print(log_message)
        self.test_results[category]["details"].append(log_message)
        if not success:
            self.test_results[category]["passed"] = False
            
    def test_admin_creation(self):
        """Test admin user creation endpoint"""
        print("\n🔧 Testing Admin Creation...")
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/create-admin")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("admin_panel", f"Admin creation endpoint working: {data.get('message', 'Success')}")
                return True
            else:
                self.log_result("admin_panel", f"Admin creation failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("admin_panel", f"Admin creation request failed: {str(e)}", False)
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        print("\n👤 Testing User Registration...")
        try:
            user_data = {
                "email": f"michael.trader{datetime.now().microsecond}@gmail.com",
                "username": f"MichaelTrader{datetime.now().microsecond}",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.log_result("auth_system", f"User registration successful for {data['user']['username']}")
                    self.log_result("auth_system", f"JWT token generated: {self.user_token[:20]}...")
                    return True
                else:
                    self.log_result("auth_system", "Registration response missing token or user data", False)
                    return False
            else:
                self.log_result("auth_system", f"Registration failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("auth_system", f"Registration request failed: {str(e)}", False)
            return False
    
    def test_user_login(self):
        """Test user login endpoint"""
        print("\n🔐 Testing User Login...")
        try:
            login_data = {
                "email": f"michael.trader{datetime.now().microsecond}@gmail.com",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.log_result("auth_system", f"User login successful for {data['user']['username']}")
                    self.log_result("auth_system", f"User balance: ${data['user']['balance']}")
                    return True
                else:
                    self.log_result("auth_system", "Login response missing token or user data", False)
                    return False
            else:
                self.log_result("auth_system", f"Login failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("auth_system", f"Login request failed: {str(e)}", False)
            return False
    
    def test_admin_login(self):
        """Test admin login to get admin token"""
        print("\n👑 Testing Admin Login...")
        try:
            admin_data = {
                "email": "admin@xspace.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=admin_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and data["user"].get("is_admin"):
                    self.admin_token = data["token"]
                    self.log_result("admin_panel", "Admin login successful")
                    return True
                else:
                    self.log_result("admin_panel", "Admin login failed - not admin user", False)
                    return False
            else:
                self.log_result("admin_panel", f"Admin login failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("admin_panel", f"Admin login request failed: {str(e)}", False)
            return False
    
    def test_assets_endpoint(self):
        """Test assets listing endpoint"""
        print("\n💰 Testing Assets Endpoint...")
        try:
            response = self.session.get(f"{BACKEND_URL}/assets")
            
            if response.status_code == 200:
                assets = response.json()
                if isinstance(assets, list) and len(assets) > 0:
                    self.log_result("asset_management", f"Assets endpoint working - found {len(assets)} assets")
                    
                    # Check for expected assets
                    symbols = [asset.get("symbol") for asset in assets]
                    expected_assets = ["BTC", "ETH", "ADA", "DOT", "TESLA"]
                    found_assets = [asset for asset in expected_assets if asset in symbols]
                    
                    self.log_result("asset_management", f"Found assets: {', '.join(found_assets)}")
                    
                    # Verify asset structure
                    sample_asset = assets[0]
                    required_fields = ["symbol", "name", "current_price", "asset_type"]
                    if all(field in sample_asset for field in required_fields):
                        self.log_result("asset_management", "Asset data structure is correct")
                        return True
                    else:
                        self.log_result("asset_management", "Asset data missing required fields", False)
                        return False
                else:
                    self.log_result("asset_management", "Assets endpoint returned empty or invalid data", False)
                    return False
            else:
                self.log_result("asset_management", f"Assets endpoint failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("asset_management", f"Assets request failed: {str(e)}", False)
            return False
    
    def test_investment_creation(self):
        """Test investment creation endpoint"""
        print("\n📈 Testing Investment Creation...")
        if not self.user_token:
            self.log_result("investment_management", "Cannot test investment - no user token", False)
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test investment in Bitcoin
            investment_data = {
                "asset_symbol": "BTC",
                "amount": 5000.0,
                "multiplier": 2.0
            }
            
            response = self.session.post(f"{BACKEND_URL}/invest", 
                                       params=investment_data, 
                                       headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "investment" in data:
                    investment = data["investment"]
                    self.log_result("investment_management", f"Investment created successfully in {investment['symbol']}")
                    self.log_result("investment_management", f"Investment amount: ${investment['amount']} with {investment['multiplier']}x multiplier")
                    return True
                else:
                    self.log_result("investment_management", "Investment response missing investment data", False)
                    return False
            else:
                self.log_result("investment_management", f"Investment creation failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("investment_management", f"Investment creation request failed: {str(e)}", False)
            return False
    
    def test_portfolio_retrieval(self):
        """Test portfolio retrieval endpoint"""
        print("\n📊 Testing Portfolio Retrieval...")
        if not self.user_token:
            self.log_result("investment_management", "Cannot test portfolio - no user token", False)
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BACKEND_URL}/portfolio", headers=headers)
            
            if response.status_code == 200:
                portfolio = response.json()
                if isinstance(portfolio, list):
                    self.log_result("investment_management", f"Portfolio retrieved successfully - {len(portfolio)} investments")
                    
                    if len(portfolio) > 0:
                        sample_investment = portfolio[0]
                        required_fields = ["asset_name", "symbol", "amount", "quantity", "profit_loss"]
                        if all(field in sample_investment for field in required_fields):
                            self.log_result("investment_management", "Portfolio data structure is correct")
                            return True
                        else:
                            self.log_result("investment_management", "Portfolio data missing required fields", False)
                            return False
                    else:
                        self.log_result("investment_management", "Portfolio is empty (expected after fresh registration)")
                        return True
                else:
                    self.log_result("investment_management", "Portfolio endpoint returned invalid data format", False)
                    return False
            else:
                self.log_result("investment_management", f"Portfolio retrieval failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("investment_management", f"Portfolio retrieval request failed: {str(e)}", False)
            return False
    
    def test_leaderboard_and_bots(self):
        """Test leaderboard endpoint and verify bot users exist"""
        print("\n🏆 Testing Leaderboard & Bot Users...")
        try:
            response = self.session.get(f"{BACKEND_URL}/leaderboard")
            
            if response.status_code == 200:
                leaderboard = response.json()
                if isinstance(leaderboard, list) and len(leaderboard) > 0:
                    self.log_result("bot_users", f"Leaderboard retrieved successfully - {len(leaderboard)} users")
                    
                    # Check for bot users
                    bot_users = [user for user in leaderboard if user.get("is_bot", False)]
                    human_users = [user for user in leaderboard if not user.get("is_bot", False)]
                    
                    self.log_result("bot_users", f"Found {len(bot_users)} bot users and {len(human_users)} human users")
                    
                    if len(bot_users) >= 15:  # Should have around 20 bot users
                        self.log_result("bot_users", "Bot user generation working correctly")
                        
                        # Check bot user data structure
                        sample_bot = bot_users[0]
                        if all(field in sample_bot for field in ["username", "total_profit_loss", "is_bot"]):
                            self.log_result("bot_users", f"Sample bot user: {sample_bot['username']} with P&L: ${sample_bot['total_profit_loss']:.2f}")
                            return True
                        else:
                            self.log_result("bot_users", "Bot user data missing required fields", False)
                            return False
                    else:
                        self.log_result("bot_users", f"Insufficient bot users found - expected ~20, got {len(bot_users)}", False)
                        return False
                else:
                    self.log_result("bot_users", "Leaderboard endpoint returned empty or invalid data", False)
                    return False
            else:
                self.log_result("bot_users", f"Leaderboard endpoint failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("bot_users", f"Leaderboard request failed: {str(e)}", False)
            return False
    
    def test_admin_stats(self):
        """Test admin stats endpoint"""
        print("\n📊 Testing Admin Stats...")
        if not self.admin_token:
            self.log_result("admin_panel", "Cannot test admin stats - no admin token", False)
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_users", "total_bots", "total_investments", "total_platform_value"]
                if all(field in stats for field in required_fields):
                    self.log_result("admin_panel", f"Admin stats working - Users: {stats['total_users']}, Bots: {stats['total_bots']}")
                    self.log_result("admin_panel", f"Total investments: {stats['total_investments']}, Platform value: ${stats['total_platform_value']:.2f}")
                    return True
                else:
                    self.log_result("admin_panel", "Admin stats missing required fields", False)
                    return False
            else:
                self.log_result("admin_panel", f"Admin stats failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("admin_panel", f"Admin stats request failed: {str(e)}", False)
            return False
    
    def test_admin_users(self):
        """Test admin users listing endpoint"""
        print("\n👥 Testing Admin Users Listing...")
        if not self.admin_token:
            self.log_result("admin_panel", "Cannot test admin users - no admin token", False)
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) > 0:
                    bot_count = sum(1 for user in users if user.get("is_bot", False))
                    human_count = len(users) - bot_count
                    
                    self.log_result("admin_panel", f"Admin users listing working - {len(users)} total users")
                    self.log_result("admin_panel", f"Breakdown: {human_count} humans, {bot_count} bots")
                    return True
                else:
                    self.log_result("admin_panel", "Admin users endpoint returned empty or invalid data", False)
                    return False
            else:
                self.log_result("admin_panel", f"Admin users failed with status {response.status_code}: {response.text}", False)
                return False
                
        except Exception as e:
            self.log_result("admin_panel", f"Admin users request failed: {str(e)}", False)
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Crypto Investment Platform Backend Tests")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test sequence following user flow
        tests_passed = 0
        total_tests = 0
        
        # 1. Admin setup
        total_tests += 1
        if self.test_admin_creation():
            tests_passed += 1
            self.test_results["admin_panel"]["passed"] = True
        
        # 2. Authentication system
        total_tests += 2
        auth_passed = 0
        if self.test_user_registration():
            auth_passed += 1
        if self.test_user_login():
            auth_passed += 1
        
        if auth_passed == 2:
            tests_passed += 2
            self.test_results["auth_system"]["passed"] = True
        
        # 3. Asset management
        total_tests += 1
        if self.test_assets_endpoint():
            tests_passed += 1
            self.test_results["asset_management"]["passed"] = True
        
        # 4. Investment management
        total_tests += 2
        investment_passed = 0
        if self.test_investment_creation():
            investment_passed += 1
        if self.test_portfolio_retrieval():
            investment_passed += 1
            
        if investment_passed == 2:
            tests_passed += 2
            self.test_results["investment_management"]["passed"] = True
        
        # 5. Bot users and leaderboard
        total_tests += 1
        if self.test_leaderboard_and_bots():
            tests_passed += 1
            self.test_results["bot_users"]["passed"] = True
        
        # 6. Admin functionality
        total_tests += 2
        admin_tests_passed = 0
        if self.test_admin_login():
            if self.test_admin_stats():
                admin_tests_passed += 1
            if self.test_admin_users():
                admin_tests_passed += 1
        
        if admin_tests_passed == 2:
            tests_passed += 2
            if not self.test_results["admin_panel"]["passed"]:  # Don't override if already passed from creation
                self.test_results["admin_panel"]["passed"] = True
        
        # Print final results
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        for category, result in self.test_results.items():
            status = "✅ WORKING" if result["passed"] else "❌ FAILED"
            category_name = category.replace("_", " ").title()
            print(f"{category_name}: {status}")
        
        print(f"\nOverall: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All backend functionality is working correctly!")
            return True
        else:
            print("⚠️  Some backend functionality needs attention.")
            return False

def main():
    """Main test execution"""
    tester = CryptoInvestmentTester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()