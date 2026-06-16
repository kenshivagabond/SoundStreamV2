"""
TEST EXPLANATION:
-----------------
We verify that:
1. An 'admin' user can access admin pages (devices, logs, tools)
2. A 'marketing' user can access devices and timetable but NOT logs
3. A 'sales' user can access devices and timetable but NOT logs

How it works:
- We simulate a login for each user
- We try to access different pages
- We check the HTTP status code returned:
  * 200 = OK, access granted
  * 403 = Forbidden, access denied (expected for certain roles)
  * 302 = Redirect (usually to login page when not authenticated)
"""

import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from app.models.UserDAO import UserDAO

def test_admin_access():
    """
    Tests that the ADMIN user has access to all pages.

    Pages tested:
    - /devices/<orga>: Must be accessible (200)
    - /logs/<orga>: Must be accessible (200)
    - /dashboard/<orga>: Must be accessible (200)
    """
    print("\n=== ADMIN ACCESS TEST ===")

    with app.test_client() as client:
        # Login as admin (Romain)
        response = client.post('/login', data={
            'username': 'Romain',
            'password': '12345'
        }, follow_redirects=True)

        # Verify login succeeded
        if response.status_code != 200:
            print("❌ FAIL: Unable to log in as admin")
            return False

        print("✅ Admin login successful")

        # Test organisation name (from Seeder.py)
        orga = "Harman_Kardon"

        # Test 1: Access /devices
        response = client.get(f'/devices/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Admin can access /devices/{orga}")
        else:
            print(f"  ❌ Admin CANNOT access /devices/{orga} (code: {response.status_code})")
            return False

        # Test 2: Access /logs (admin-only)
        response = client.get(f'/logs/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Admin can access /logs/{orga}")
        else:
            print(f"  ❌ Admin CANNOT access /logs/{orga} (code: {response.status_code})")
            return False

        # Test 3: Access dashboard
        response = client.get(f'/dashboard/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Admin can access /dashboard/{orga}")
        else:
            print(f"  ❌ Admin CANNOT access /dashboard/{orga} (code: {response.status_code})")
            return False

        print("✅ ALL ADMIN TESTS PASSED\n")
        return True


def test_communication_access():
    """
    Tests that the MARKETING user has limited access.

    Pages tested:
    - /devices/<orga>: Must be accessible (200)
    - /dashboard/<orga>: Must be accessible (200)
    - /logs/<orga>: Must NOT be accessible (403)
    """
    print("\n=== MARKETING ACCESS TEST ===")

    with app.test_client() as client:
        # Login as marketing (Tristan)
        response = client.post('/login', data={
            'username': 'Tristan',
            'password': '12345'
        }, follow_redirects=True)

        if response.status_code != 200:
            print("❌ FAIL: Unable to log in as marketing")
            return False

        print("✅ Marketing login successful")

        orga = "Harman_Kardon"

        # Test 1: Access /devices (should work)
        response = client.get(f'/devices/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Marketing can access /devices/{orga}")
        else:
            print(f"  ❌ Marketing CANNOT access /devices/{orga} (code: {response.status_code})")
            return False

        # Test 2: Access dashboard (should work)
        response = client.get(f'/dashboard/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Marketing can access /dashboard/{orga}")
        else:
            print(f"  ❌ Marketing CANNOT access /dashboard/{orga} (code: {response.status_code})")
            return False

        # Test 3: Access /logs (should NOT work - admin only)
        response = client.get(f'/logs/{orga}')
        if response.status_code == 403:
            print(f"  ✅ Marketing CANNOT access /logs/{orga} (as expected)")
        else:
            print(f"  ❌ ISSUE: Marketing CAN access /logs/{orga} (code: {response.status_code})")
            print(f"     Expected: 403 (Forbidden)")
            return False

        print("✅ ALL MARKETING TESTS PASSED\n")
        return True


def test_commercial_access():
    """
    Tests that the SALES user has limited access.

    Pages tested:
    - /devices/<orga>: Must be accessible (200)
    - /dashboard/<orga>: Must be accessible (200)
    - /logs/<orga>: Must NOT be accessible (403)
    """
    print("\n=== SALES ACCESS TEST ===")

    with app.test_client() as client:
        # Login as sales (Abou)
        response = client.post('/login', data={
            'username': 'Abou',
            'password': '12345'
        }, follow_redirects=True)

        if response.status_code != 200:
            print("❌ FAIL: Unable to log in as sales")
            return False

        print("✅ Sales login successful")

        orga = "Harman_Kardon"

        # Test 1: Access /devices (should work)
        response = client.get(f'/devices/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Sales can access /devices/{orga}")
        else:
            print(f"  ❌ Sales CANNOT access /devices/{orga} (code: {response.status_code})")
            return False

        # Test 2: Access dashboard (should work)
        response = client.get(f'/dashboard/{orga}')
        if response.status_code == 200:
            print(f"  ✅ Sales can access /dashboard/{orga}")
        else:
            print(f"  ❌ Sales CANNOT access /dashboard/{orga} (code: {response.status_code})")
            return False

        # Test 3: Access /logs (should NOT work - admin only)
        response = client.get(f'/logs/{orga}')
        if response.status_code == 403:
            print(f"  ✅ Sales CANNOT access /logs/{orga} (as expected)")
        else:
            print(f"  ❌ ISSUE: Sales CAN access /logs/{orga} (code: {response.status_code})")
            print(f"     Expected: 403 (Forbidden)")
            return False

        print("✅ ALL SALES TESTS PASSED\n")
        return True


def test_no_authentication():
    """
    Tests that a NON-authenticated user cannot access any protected page.

    All pages should redirect to /login (code 302).
    """
    print("\n=== NO AUTHENTICATION TEST ===")

    with app.test_client() as client:
        orga = "Harman_Kardon"

        # Test 1: Attempt to access /devices without being logged in
        response = client.get(f'/devices/{orga}')
        if response.status_code == 302:  # 302 = Redirect to login
            print(f"  ✅ Access to /devices/{orga} correctly redirects to login")
        else:
            print(f"  ❌ ISSUE: /devices/{orga} accessible without login (code: {response.status_code})")
            return False

        # Test 2: Attempt to access dashboard without being logged in
        response = client.get(f'/dashboard/{orga}')
        if response.status_code == 302:
            print(f"  ✅ Access to /dashboard/{orga} correctly redirects to login")
        else:
            print(f"  ❌ ISSUE: /dashboard/{orga} accessible without login (code: {response.status_code})")
            return False

        # Test 3: Attempt to access logs without being logged in
        response = client.get(f'/logs/{orga}')
        if response.status_code == 302:
            print(f"  ✅ Access to /logs/{orga} correctly redirects to login")
        else:
            print(f"  ❌ ISSUE: /logs/{orga} accessible without login (code: {response.status_code})")
            return False

        print("✅ ALL NO-AUTH TESTS PASSED\n")
        return True


if __name__ == "__main__":
    print("╔════════════════════════════════════════════╗")
    print("║   ROLE-BASED PAGE ACCESS TESTS              ║")
    print("╚════════════════════════════════════════════╝")

    # Run all tests
    admin_ok = test_admin_access()
    comm_ok = test_communication_access()
    commercial_ok = test_commercial_access()
    no_auth_ok = test_no_authentication()

    # Final summary
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    print(f"Admin:          {'✅ PASSED' if admin_ok else '❌ FAILED'}")
    print(f"Marketing:      {'✅ PASSED' if comm_ok else '❌ FAILED'}")
    print(f"Sales:          {'✅ PASSED' if commercial_ok else '❌ FAILED'}")
    print(f"No auth:        {'✅ PASSED' if no_auth_ok else '❌ FAILED'}")
    print("="*50)

    # Exit code
    all_ok = admin_ok and comm_ok and commercial_ok and no_auth_ok

    if all_ok:
        print("\n ALL TESTS PASSED!")
    else:
        print("\n SOME TESTS FAILED")

    sys.exit(0 if all_ok else 1)