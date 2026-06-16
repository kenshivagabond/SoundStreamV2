
import sys
import os

# Add parent directory to path to allow importing app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.UserDAO import UserDAO

def test_authentication():
    """
    Tests authentication for 3 users:
    1. Romain (admin)
    2. Tristan (marketing)
    3. Abou (sales)

    Passwords are defined in the seeder (Seeder.py).
    """

    print("=== AUTHENTICATION TEST ===\n")

    # Create a DAO instance
    dao = UserDAO()

    # List of users to test
    test_users = [
        {"username": "Romain", "password": "12345", "expected_role": "admin"},
        {"username": "Tristan", "password": "678910", "expected_role": "marketing"},
        {"username": "Abou", "password": "1112131415", "expected_role": "sales"}
    ]

    # Result counters
    tests_passed = 0
    tests_failed = 0

    # Test each user
    for user_test in test_users:
        username = user_test["username"]
        password = user_test["password"]
        expected_role = user_test["expected_role"]

        print(f"Testing {username}...")

        # Check 1: Does the user exist?
        user = dao.findByUsername(username)
        if user is None:
            print(f"   FAIL: User '{username}' not found in the database\n")
            tests_failed += 1
            continue

        # Check 2: Is the password correct?
        if not dao.verifyUser(username, password):
            print(f"  ❌ FAIL: Incorrect password for '{username}'\n")
            tests_failed += 1
            continue

        # Check 3: Is the role correct?
        if user.role != expected_role:
            print(f"  ❌ FAIL: Incorrect role for '{username}'")
            print(f"     Expected: {expected_role}, Got: {user.role}\n")
            tests_failed += 1
            continue

        # All checks passed
        print(f"  ✅ PASS: {username} authenticated correctly (role: {user.role})\n")
        tests_passed += 1

    # Summary
    print("=== TEST SUMMARY ===")
    print(f"Tests passed: {tests_passed}/3")
    print(f"Tests failed: {tests_failed}/3")

    if tests_passed == 3:
        print("\n ALL TESTS PASSED!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return False

def test_wrong_password():
    """
    Verifies that authentication fails with an incorrect password.
    """
    print("\n=== WRONG PASSWORD TEST ===\n")

    dao = UserDAO()

    # Attempt with a wrong password
    if dao.verifyUser("Romain", "wrongpassword"):
        print(" FAIL: The system accepted an incorrect password!")
        return False
    else:
        print(" PASS: The system correctly rejected the wrong password")
        return True

if __name__ == "__main__":
    # Run the tests
    auth_ok = test_authentication()
    bonus_ok = test_wrong_password()

    # Exit code (0 = success, 1 = failure)
    sys.exit(0 if (auth_ok and bonus_ok) else 1)