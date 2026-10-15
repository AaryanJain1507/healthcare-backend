import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            res_body = response.read().decode("utf-8")
            json_body = json.loads(res_body) if res_body else None
            return status_code, json_body
    except urllib.error.HTTPError as e:
        status_code = e.code
        res_body = e.read().decode("utf-8")
        try:
            json_body = json.loads(res_body) if res_body else None
        except Exception:
            json_body = res_body
        return status_code, json_body

def run_tests():
    passed = 0
    failed = 0
    results = []

    def log_test(name, success, details=""):
        nonlocal passed, failed
        if success:
            passed += 1
            results.append(f"  [PASS] {name} - {details}")
        else:
            failed += 1
            results.append(f"  [FAIL] {name} - {details}")

    print("Starting Comprehensive API Endpoint Verification...\n")

    # 1. Register User 1
    u1_email = "user1@test.com"
    u1_pass = "TestPassword123!"
    code, res = request("POST", "/api/auth/register/", {
        "name": "Dr. Alice Walker",
        "email": u1_email,
        "password": u1_pass
    })
    log_test("POST /api/auth/register/ (Valid User 1)", code == 201 and "password" not in res and res.get("email") == u1_email, f"Status: {code}, Body: {res}")

    # 1b. Register Validation - Short Password
    code, res = request("POST", "/api/auth/register/", {
        "name": "Short Pass",
        "email": "short@test.com",
        "password": "short"
    })
    log_test("POST /api/auth/register/ (Short Password < 8)", code == 400, f"Status: {code}, Error: {res}")

    # 1c. Register Validation - Duplicate Email
    code, res = request("POST", "/api/auth/register/", {
        "name": "Duplicate User",
        "email": u1_email,
        "password": u1_pass
    })
    log_test("POST /api/auth/register/ (Duplicate Email)", code == 400, f"Status: {code}, Error: {res}")

    # 1d. Register User 2 (for cross-user permission checks)
    u2_email = "user2@test.com"
    u2_pass = "TestPassword456!"
    code, res = request("POST", "/api/auth/register/", {
        "name": "Dr. Bob Johnson",
        "email": u2_email,
        "password": u2_pass
    })
    log_test("POST /api/auth/register/ (Valid User 2)", code == 201, f"Status: {code}")

    # 2. Login User 1
    code, res = request("POST", "/api/auth/login/", {
        "email": u1_email,
        "password": u1_pass
    })
    user1_token = res.get("access") if res else None
    log_test("POST /api/auth/login/ (User 1)", code == 200 and user1_token is not None, f"Status: {code}, Access token acquired: {bool(user1_token)}")

    # 2b. Login User 2
    code, res = request("POST", "/api/auth/login/", {
        "email": u2_email,
        "password": u2_pass
    })
    user2_token = res.get("access") if res else None
    log_test("POST /api/auth/login/ (User 2)", code == 200 and user2_token is not None, f"Status: {code}")

    # 2c. Login Invalid Password
    code, res = request("POST", "/api/auth/login/", {
        "email": u1_email,
        "password": "WrongPassword!"
    })
    log_test("POST /api/auth/login/ (Invalid Credentials)", code in (400, 401), f"Status: {code}, Message: {res}")

    # 3. Patient Endpoints
    # 3a. Unauthenticated access check
    code, res = request("GET", "/api/patients/")
    log_test("GET /api/patients/ (Unauthenticated)", code == 401, f"Status: {code}")

    # 3b. Create Patient Invalid Age <= 0
    code, res = request("POST", "/api/patients/", {
        "name": "Bad Age Patient",
        "age": 0,
        "gender": "Male",
        "phone": "555-1234",
        "address": "123 Street"
    }, token=user1_token)
    log_test("POST /api/patients/ (Validation: Age <= 0)", code == 400, f"Status: {code}, Error: {res}")

    # 3c. Create Patient 1 by User 1
    code, p1 = request("POST", "/api/patients/", {
        "name": "John Doe",
        "age": 45,
        "gender": "Male",
        "phone": "+1-555-0101",
        "address": "742 Evergreen Terrace",
        "medical_history": "Asthma"
    }, token=user1_token)
    p1_id = p1.get("id") if p1 else None
    log_test("POST /api/patients/ (User 1 creates P1)", code == 201 and p1_id is not None, f"Status: {code}, Patient ID: {p1_id}")

    # 3d. Create Patient 2 by User 1
    code, p2 = request("POST", "/api/patients/", {
        "name": "Jane Smith",
        "age": 29,
        "gender": "Female",
        "phone": "+1-555-0102",
        "address": "100 Elm Street"
    }, token=user1_token)
    p2_id = p2.get("id") if p2 else None
    log_test("POST /api/patients/ (User 1 creates P2)", code == 201, f"Status: {code}, Patient ID: {p2_id}")

    # 3e. List Patients for User 1
    code, res = request("GET", "/api/patients/", token=user1_token)
    log_test("GET /api/patients/ (User 1 sees own patients)", code == 200 and len(res) == 2, f"Status: {code}, Patient count: {len(res) if isinstance(res, list) else 0}")

    # 3f. List Patients for User 2 (should be empty)
    code, res = request("GET", "/api/patients/", token=user2_token)
    log_test("GET /api/patients/ (User 2 sees 0 patients)", code == 200 and len(res) == 0, f"Status: {code}, Patient count: {len(res) if isinstance(res, list) else 0}")

    # 3g. User 1 retrieves P1
    code, res = request("GET", f"/api/patients/{p1_id}/", token=user1_token)
    log_test(f"GET /api/patients/{p1_id}/ (Owner User 1)", code == 200 and res.get("name") == "John Doe", f"Status: {code}")

    # 3h. User 2 attempts to retrieve P1 (cross-user check -> 403 or 404)
    code, res = request("GET", f"/api/patients/{p1_id}/", token=user2_token)
    log_test(f"GET /api/patients/{p1_id}/ (Non-owner User 2 blocked)", code in (403, 404), f"Status: {code}")

    # 3i. User 1 updates P1
    code, res = request("PUT", f"/api/patients/{p1_id}/", {
        "name": "John Doe Updated",
        "age": 46,
        "gender": "Male",
        "phone": "+1-555-0101",
        "address": "742 Evergreen Terrace Apt 2",
        "medical_history": "Asthma, seasonal allergies"
    }, token=user1_token)
    log_test(f"PUT /api/patients/{p1_id}/ (Owner User 1 update)", code == 200 and res.get("age") == 46, f"Status: {code}")

    # 3j. User 2 attempts to update P1 -> 403
    code, res = request("PUT", f"/api/patients/{p1_id}/", {
        "name": "Hacked",
        "age": 50,
        "gender": "Male",
        "phone": "000",
        "address": "Nowhere"
    }, token=user2_token)
    log_test(f"PUT /api/patients/{p1_id}/ (Non-owner User 2 blocked)", code in (403, 404), f"Status: {code}")

    # 3k. User 2 attempts to delete P1 -> 403
    code, res = request("DELETE", f"/api/patients/{p1_id}/", token=user2_token)
    log_test(f"DELETE /api/patients/{p1_id}/ (Non-owner User 2 blocked)", code in (403, 404), f"Status: {code}")

    # 4. Doctors Endpoints
    # 4a. User 1 creates Doctor D1
    code, d1 = request("POST", "/api/doctors/", {
        "name": "Gregory House",
        "specialization": "Diagnostic Medicine",
        "email": "house@princeton.edu",
        "phone": "+1-555-4687",
        "experience_years": 20
    }, token=user1_token)
    d1_id = d1.get("id") if d1 else None
    log_test("POST /api/doctors/ (User 1 creates D1)", code == 201 and d1_id is not None, f"Status: {code}, Doctor ID: {d1_id}")

    # 4b. User 2 creates Doctor D2
    code, d2 = request("POST", "/api/doctors/", {
        "name": "James Wilson",
        "specialization": "Oncology",
        "email": "wilson@princeton.edu",
        "phone": "+1-555-4688",
        "experience_years": 18
    }, token=user2_token)
    d2_id = d2.get("id") if d2 else None
    log_test("POST /api/doctors/ (User 2 creates D2)", code == 201 and d2_id is not None, f"Status: {code}, Doctor ID: {d2_id}")

    # 4c. List all doctors (both User 1 and User 2 can list all doctors)
    code, res = request("GET", "/api/doctors/", token=user1_token)
    log_test("GET /api/doctors/ (Lists all doctors)", code == 200 and len(res) == 2, f"Status: {code}, Count: {len(res) if isinstance(res, list) else 0}")

    # 4d. Get Doctor details (any authenticated user can view)
    code, res = request("GET", f"/api/doctors/{d1_id}/", token=user2_token)
    log_test(f"GET /api/doctors/{d1_id}/ (User 2 views D1 details)", code == 200 and res.get("name") == "Gregory House", f"Status: {code}")

    # 4e. User 2 attempts to update D1 (created by User 1) -> 403
    code, res = request("PUT", f"/api/doctors/{d1_id}/", {
        "name": "Gregory House Hacked",
        "specialization": "None",
        "email": "house@princeton.edu",
        "phone": "+1-555-4687",
        "experience_years": 21
    }, token=user2_token)
    log_test(f"PUT /api/doctors/{d1_id}/ (Non-creator User 2 blocked)", code == 403, f"Status: {code}")

    # 4f. User 1 updates D1 -> 200
    code, res = request("PUT", f"/api/doctors/{d1_id}/", {
        "name": "Gregory House",
        "specialization": "Diagnostic Medicine & Nephrology",
        "email": "house@princeton.edu",
        "phone": "+1-555-4687",
        "experience_years": 21
    }, token=user1_token)
    log_test(f"PUT /api/doctors/{d1_id}/ (Creator User 1 updates D1)", code == 200 and res.get("experience_years") == 21, f"Status: {code}")

    # 5. Mappings Endpoints
    # 5a. User 1 assigns D1 to P1
    code, m1 = request("POST", "/api/mappings/", {
        "patient": p1_id,
        "doctor": d1_id
    }, token=user1_token)
    m1_id = m1.get("id") if m1 else None
    log_test("POST /api/mappings/ (User 1 assigns D1 to P1)", code == 201 and m1_id is not None, f"Status: {code}, Mapping ID: {m1_id}")

    # 5b. User 1 duplicate assignment -> 400
    code, res = request("POST", "/api/mappings/", {
        "patient": p1_id,
        "doctor": d1_id
    }, token=user1_token)
    log_test("POST /api/mappings/ (Duplicate assignment rejected)", code == 400, f"Status: {code}, Error: {res}")

    # 5c. User 2 attempts to assign doctor to User 1's patient P1 -> 400
    code, res = request("POST", "/api/mappings/", {
        "patient": p1_id,
        "doctor": d2_id
    }, token=user2_token)
    log_test("POST /api/mappings/ (Assigning doctor to another user's patient rejected)", code == 400, f"Status: {code}, Error: {res}")

    # 5d. User 1 lists mappings -> returns mapping for P1
    code, res = request("GET", "/api/mappings/", token=user1_token)
    log_test("GET /api/mappings/ (User 1 lists own patient mappings)", code == 200 and len(res) == 1, f"Status: {code}, Count: {len(res) if isinstance(res, list) else 0}")

    # 5e. User 2 lists mappings -> returns empty
    code, res = request("GET", "/api/mappings/", token=user2_token)
    log_test("GET /api/mappings/ (User 2 lists own patient mappings)", code == 200 and len(res) == 0, f"Status: {code}")

    # 5f. User 1 gets doctors assigned to P1
    code, res = request("GET", f"/api/mappings/{p1_id}/", token=user1_token)
    log_test(f"GET /api/mappings/{p1_id}/ (Doctors assigned to P1)", code == 200 and len(res) == 1 and res[0].get("id") == d1_id, f"Status: {code}, Doctors: {res}")

    # 5g. User 2 attempts to get doctors assigned to P1 -> 403
    code, res = request("GET", f"/api/mappings/{p1_id}/", token=user2_token)
    log_test(f"GET /api/mappings/{p1_id}/ (User 2 blocked from viewing P1 mappings)", code == 403, f"Status: {code}")

    # 5h. User 2 attempts to delete User 1's mapping -> 403
    code, res = request("DELETE", f"/api/mappings/{m1_id}/", token=user2_token)
    log_test(f"DELETE /api/mappings/{m1_id}/ (User 2 blocked from deleting User 1 mapping)", code == 403, f"Status: {code}")

    # 5i. User 1 deletes mapping -> 204
    code, res = request("DELETE", f"/api/mappings/{m1_id}/", token=user1_token)
    log_test(f"DELETE /api/mappings/{m1_id}/ (Owner User 1 deletes mapping)", code == 204, f"Status: {code}")

    # 5j. Verify doctors assigned to P1 is now empty
    code, res = request("GET", f"/api/mappings/{p1_id}/", token=user1_token)
    log_test(f"GET /api/mappings/{p1_id}/ (After deletion, assigned doctors empty)", code == 200 and len(res) == 0, f"Status: {code}")

    # 6. Delete Patient P2 by User 1 -> 204
    code, res = request("DELETE", f"/api/patients/{p2_id}/", token=user1_token)
    log_test(f"DELETE /api/patients/{p2_id}/ (Owner deletes patient)", code == 204, f"Status: {code}")

    # 7. Delete Doctor D2 by User 2 -> 204
    code, res = request("DELETE", f"/api/doctors/{d2_id}/", token=user2_token)
    log_test(f"DELETE /api/doctors/{d2_id}/ (Creator deletes doctor)", code == 204, f"Status: {code}")

    print("\n--- Test Results Summary ---")
    for r in results:
        print(r)
    print(f"\nTotal: {passed + failed} | Passed: {passed} | Failed: {failed}")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
