#!/usr/bin/env python3
"""
Comprehensive Testing Script for Trivanta ERP Application
========================================================

This script provides a step-by-step manual testing guide for all templates,
pages, and functionality across all portals (Admin, Manager, Employee).

Usage:
1. Start the Flask application: python app.py
2. Follow this testing script step by step
3. Check for Jinja2 errors, broken links, and functionality issues
4. Document any errors found

Prerequisites:
- Flask application running on http://localhost:5000
- Test data available in data/trivanta_erp.json
- All dependencies installed (requirements.txt)
"""

import time
import webbrowser
from datetime import datetime

class ERPTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8080"
        self.test_results = []
        self.current_test = 1
        
    def log_test(self, test_name, status="PASS", notes=""):
        """Log test results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] Test {self.current_test}: {test_name} - {status}"
        if notes:
            result += f" - {notes}"
        print(result)
        self.test_results.append({
            'test_id': self.current_test,
            'name': test_name,
            'status': status,
            'notes': notes,
            'timestamp': timestamp
        })
        self.current_test += 1
        
    def open_url(self, url, description):
        """Open URL and log the action"""
        full_url = f"{self.base_url}{url}"
        print(f"\n{'='*60}")
        print(f"TESTING: {description}")
        print(f"URL: {full_url}")
        print(f"{'='*60}")
        
        try:
            webbrowser.open(full_url)
            input("Press Enter after testing this page...")
        except Exception as e:
            print(f"Error opening URL: {e}")
            
    def run_comprehensive_test(self):
        """Run comprehensive testing across all portals"""
        print("🚀 Starting Comprehensive ERP Application Testing")
        print("=" * 60)
        
        # 1. PUBLIC PAGES TESTING
        print("\n📋 SECTION 1: PUBLIC PAGES TESTING")
        print("-" * 40)
        
        self.open_url("/", "Main Index Page (should redirect to login)")
        self.log_test("Main Index Page", "TESTED", "Check redirect behavior")
        
        self.open_url("/login", "Login Page")
        self.log_test("Login Page", "TESTED", "Check form rendering and validation")
        
        # 2. ADMIN PORTAL TESTING
        print("\n👑 SECTION 2: ADMIN PORTAL TESTING")
        print("-" * 40)
        print("Login as admin: admin@trivantaedge.com / admin123")
        
        # Admin Dashboard
        self.open_url("/admin/dashboard", "Admin Dashboard")
        self.log_test("Admin Dashboard", "TESTED", "Check analytics, metrics, and navigation")
        
        # Admin Users Management
        self.open_url("/admin/users", "Admin Users List")
        self.log_test("Admin Users List", "TESTED", "Check user table, search, and actions")
        
        self.open_url("/admin/users/create", "Admin Create User")
        self.log_test("Admin Create User", "TESTED", "Check form fields, validation, and submission")
        
        # Test with a sample user ID (adjust as needed)
        self.open_url("/admin/users/user_001/edit", "Admin Edit User")
        self.log_test("Admin Edit User", "TESTED", "Check form population and update functionality")
        
        # Admin Projects
        self.open_url("/admin/projects", "Admin Projects List")
        self.log_test("Admin Projects List", "TESTED", "Check project table and management")
        
        # Admin Clients
        self.open_url("/admin/clients", "Admin Clients List")
        self.log_test("Admin Clients List", "TESTED", "Check client table and management")
        
        # Admin Leads
        self.open_url("/admin/leads", "Admin Leads List")
        self.log_test("Admin Leads List", "TESTED", "Check leads table and conversion")
        
        # Admin Tasks
        self.open_url("/admin/tasks", "Admin Tasks Management")
        self.log_test("Admin Tasks Management", "TESTED", "Check task assignment and tracking")
        
        # Admin Attendance
        self.open_url("/admin/attendance", "Admin Attendance Overview")
        self.log_test("Admin Attendance Overview", "TESTED", "Check attendance reports and monitoring")
        
        # Admin Analytics
        self.open_url("/admin/analytics", "Admin Analytics Dashboard")
        self.log_test("Admin Analytics Dashboard", "TESTED", "Check charts, metrics, and data visualization")
        
        # Admin Reports
        self.open_url("/admin/reports", "Admin Reports Generation")
        self.log_test("Admin Reports Generation", "TESTED", "Check report types and export functionality")
        
        # Admin Settings
        self.open_url("/admin/settings", "Admin System Settings")
        self.log_test("Admin System Settings", "TESTED", "Check configuration options")
        
        # 3. MANAGER PORTAL TESTING
        print("\n👔 SECTION 3: MANAGER PORTAL TESTING")
        print("-" * 40)
        print("Login as manager (use test credentials)")
        
        # Manager Dashboard
        self.open_url("/manager/dashboard", "Manager Dashboard")
        self.log_test("Manager Dashboard", "TESTED", "Check team overview and project status")
        
        # Manager Employees
        self.open_url("/manager/employees", "Manager Employees List")
        self.log_test("Manager Employees List", "TESTED", "Check employee management and assignments")
        
        self.open_url("/manager/employees/create", "Manager Create Employee")
        self.log_test("Manager Create Employee", "TESTED", "Check employee creation form")
        
        # Test with a sample employee ID
        self.open_url("/manager/employees/emp_001/edit", "Manager Edit Employee")
        self.log_test("Manager Edit Employee", "TESTED", "Check employee editing functionality")
        
        # Manager Projects
        self.open_url("/manager/projects", "Manager Projects List")
        self.log_test("Manager Projects List", "TESTED", "Check project management and team assignments")
        
        self.open_url("/manager/projects/create", "Manager Create Project")
        self.log_test("Manager Create Project", "TESTED", "Check project creation form and validation")
        
        # Manager Clients
        self.open_url("/manager/clients", "Manager Clients List")
        self.log_test("Manager Clients List", "TESTED", "Check client relationship management")
        
        self.open_url("/manager/clients/create", "Manager Create Client")
        self.log_test("Manager Create Client", "TESTED", "Check client creation form")
        
        # Manager Leads
        self.open_url("/manager/leads", "Manager Leads List")
        self.log_test("Manager Leads List", "TESTED", "Check lead management and conversion")
        
        self.open_url("/manager/leads/create", "Manager Create Lead")
        self.log_test("Manager Create Lead", "TESTED", "Check lead creation and tracking")
        
        # Manager Tasks
        self.open_url("/manager/tasks", "Manager Tasks Management")
        self.log_test("Manager Tasks Management", "TESTED", "Check task assignment and progress tracking")
        
        # Manager Inventory
        self.open_url("/manager/inventory", "Manager Inventory Management")
        self.log_test("Manager Inventory Management", "TESTED", "Check stock levels and management")
        
        # Manager Reports
        self.open_url("/manager/reports", "Manager Reports")
        self.log_test("Manager Reports", "TESTED", "Check team performance reports")
        
        # Manager Analytics
        self.open_url("/manager/analytics", "Manager Analytics")
        self.log_test("Manager Analytics", "TESTED", "Check team metrics and performance data")
        
        # Manager Attendance
        self.open_url("/manager/attendance", "Manager Attendance Monitoring")
        self.log_test("Manager Attendance Monitoring", "TESTED", "Check team attendance tracking")
        
        # 4. EMPLOYEE PORTAL TESTING
        print("\n👷 SECTION 4: EMPLOYEE PORTAL TESTING")
        print("-" * 40)
        print("Login as employee (use test credentials)")
        
        # Employee Dashboard
        self.open_url("/employee/dashboard", "Employee Dashboard")
        self.log_test("Employee Dashboard", "TESTED", "Check personal overview and assigned projects")
        
        # Employee Profile
        self.open_url("/employee/profile", "Employee Profile")
        self.log_test("Employee Profile", "TESTED", "Check personal information display")
        
        self.open_url("/employee/profile/edit", "Employee Edit Profile")
        self.log_test("Employee Edit Profile", "TESTED", "Check profile editing functionality")
        
        # Employee Projects
        self.open_url("/employee/projects", "Employee Projects List")
        self.log_test("Employee Projects List", "TESTED", "Check assigned projects and status")
        
        # Test with a sample project ID
        self.open_url("/employee/projects/proj_001", "Employee Project Detail")
        self.log_test("Employee Project Detail", "TESTED", "Check project information and tasks")
        
        # Employee Tasks
        self.open_url("/employee/tasks", "Employee Tasks List")
        self.log_test("Employee Tasks List", "TESTED", "Check task assignments and progress")
        
        # Employee Attendance
        self.open_url("/employee/attendance", "Employee Attendance")
        self.log_test("Employee Attendance", "TESTED", "Check check-in/out functionality and history")
        
        # Employee Clients
        self.open_url("/employee/clients", "Employee Clients")
        self.log_test("Employee Clients", "TESTED", "Check client information and interactions")
        
        self.open_url("/employee/clients/create", "Employee Create Client")
        self.log_test("Employee Create Client", "TESTED", "Check client creation form")
        
        # Employee Leads
        self.open_url("/employee/leads", "Employee Leads")
        self.log_test("Employee Leads", "TESTED", "Check lead management and conversion")
        
        self.open_url("/employee/leads/create", "Employee Create Lead")
        self.log_test("Employee Create Lead", "TESTED", "Check lead creation and tracking")
        
        # Employee Reports
        self.open_url("/employee/reports", "Employee Reports")
        self.log_test("Employee Reports", "TESTED", "Check personal performance reports")
        
        # 5. AUTHENTICATION & SECURITY TESTING
        print("\n🔐 SECTION 5: AUTHENTICATION & SECURITY TESTING")
        print("-" * 40)
        
        self.open_url("/setup-2fa", "2FA Setup Page")
        self.log_test("2FA Setup Page", "TESTED", "Check 2FA configuration")
        
        self.open_url("/verify-2fa", "2FA Verification Page")
        self.log_test("2FA Verification Page", "TESTED", "Check 2FA verification flow")
        
        # Test logout
        self.open_url("/logout", "Logout Functionality")
        self.log_test("Logout Functionality", "TESTED", "Check session clearing and redirect")
        
        # 6. ERROR PAGES TESTING
        print("\n❌ SECTION 6: ERROR PAGES TESTING")
        print("-" * 40)
        
        self.open_url("/nonexistent-page", "404 Error Page")
        self.log_test("404 Error Page", "TESTED", "Check custom 404 template")
        
        # 7. TEMPLATE SPECIFIC TESTING
        print("\n📝 SECTION 7: TEMPLATE SPECIFIC TESTING")
        print("-" * 40)
        print("Check each template for the following issues:")
        
        template_checks = [
            "Jinja2 syntax errors",
            "Missing template variables",
            "Broken template inheritance",
            "Missing CSS/JS includes",
            "Broken navigation links",
            "Form validation errors",
            "Flash message display",
            "Responsive design issues",
            "Button functionality",
            "Modal/popup functionality",
            "Data table rendering",
            "Search and filter functionality",
            "Pagination controls",
            "Export functionality",
            "Print functionality"
        ]
        
        for check in template_checks:
            self.log_test(f"Template Check: {check}", "VERIFY", "Ensure this works across all templates")
        
        # 8. FUNCTIONALITY TESTING CHECKLIST
        print("\n⚙️ SECTION 8: FUNCTIONALITY TESTING CHECKLIST")
        print("-" * 40)
        
        functionality_checks = [
            "User authentication and authorization",
            "Role-based access control",
            "CRUD operations for all entities",
            "File upload and management",
            "Email notifications",
            "Real-time updates via WebSocket",
            "Data validation and sanitization",
            "CSRF protection",
            "Session management",
            "Password reset functionality",
            "User profile management",
            "Project lifecycle management",
            "Task assignment and tracking",
            "Client relationship management",
            "Lead conversion process",
            "Attendance tracking system",
            "Reporting and analytics",
            "Data export functionality",
            "Search and filtering",
            "Bulk operations"
        ]
        
        for check in functionality_checks:
            self.log_test(f"Functionality Check: {check}", "VERIFY", "Test this functionality thoroughly")
        
        # 9. PERFORMANCE & UX TESTING
        print("\n🚀 SECTION 9: PERFORMANCE & UX TESTING")
        print("-" * 40)
        
        performance_checks = [
            "Page load times",
            "Database query performance",
            "Image and asset loading",
            "Form submission responsiveness",
            "Search response time",
            "Report generation speed",
            "Mobile responsiveness",
            "Cross-browser compatibility",
            "Accessibility compliance",
            "User experience flow"
        ]
        
        for check in performance_checks:
            self.log_test(f"Performance Check: {check}", "VERIFY", "Monitor and optimize as needed")
        
        # 10. FINAL VERIFICATION
        print("\n✅ SECTION 10: FINAL VERIFICATION")
        print("-" * 40)
        
        final_checks = [
            "All navigation links work correctly",
            "All forms submit successfully",
            "All buttons perform expected actions",
            "All modals and popups function properly",
            "All data tables render correctly",
            "All search and filter functions work",
            "All export functions generate proper files",
            "All user roles have appropriate access",
            "All error messages are user-friendly",
            "All success messages display correctly"
        ]
        
        for check in final_checks:
            self.log_test(f"Final Check: {check}", "VERIFY", "Ensure this is working correctly")
        
        # Generate Test Summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate a summary of all test results"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        tested_tests = len([r for r in self.test_results if r['status'] == 'TESTED'])
        verify_tests = len([r for r in self.test_results if r['status'] == 'VERIFY'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Tested: {tested_tests}")
        print(f"Need Verification: {verify_tests}")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "🔄" if result['status'] == 'TESTED' else "❓"
            print(f"{status_icon} {result['name']} - {result['status']}")
            if result['notes']:
                print(f"   Note: {result['notes']}")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Review all 'VERIFY' status tests")
        print("2. Fix any Jinja2 template errors found")
        print("3. Resolve broken functionality issues")
        print("4. Optimize performance bottlenecks")
        print("5. Improve user experience issues")
        print("6. Run regression tests after fixes")
        
        # Save results to file
        self.save_test_results()
        
    def save_test_results(self):
        """Save test results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"erp_test_results_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("Trivanta ERP Application - Test Results\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in self.test_results:
                f.write(f"Test {result['test_id']}: {result['name']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Notes: {result['notes']}\n")
                f.write(f"Timestamp: {result['timestamp']}\n")
                f.write("-" * 30 + "\n")
        
        print(f"\n💾 Test results saved to: {filename}")

def main():
    """Main function to run the ERP testing"""
    print("🔧 Trivanta ERP Application - Comprehensive Testing Script")
    print("=" * 60)
    print("\nThis script will guide you through testing all aspects of your ERP application.")
    print("Make sure your Flask app is running on http://127.0.0.1:8080")
    print("\nPress Enter to start testing...")
    input()
    
    tester = ERPTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
