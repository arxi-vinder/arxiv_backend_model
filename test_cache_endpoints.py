"""
Test script untuk semua cache dan vectorization endpoints
Jalankan: python test_cache_endpoints.py
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Color codes untuk output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_request(method: str, endpoint: str):
    print(f"{Colors.OKBLUE}{Colors.BOLD}{method}{Colors.ENDC} {endpoint}")


def print_response(response: Dict[str, Any], status_code: int = None):
    """Pretty print response"""
    if status_code:
        if status_code == 200:
            print(f"{Colors.OKGREEN}Status: {status_code}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}Status: {status_code}{Colors.ENDC}")
    print(json.dumps(response, indent=2, default=str))


def test_cache_info():
    """Test: GET /api/v1/cache/info"""
    print_header("TEST 1: Get Cache Information")

    endpoint = f"{BASE_URL}/api/v1/cache/info"
    print_request("GET", endpoint)

    try:
        response = requests.get(endpoint, timeout=10)
        print_response(response.json(), response.status_code)

        if response.status_code == 200:
            data = response.json()
            if data.get("cache_status") == "cached":
                print_success("Cache ditemukan!")
                return True
            else:
                print_info("Cache belum ada. Jalankan vectorization terlebih dahulu.")
                return False
        else:
            print_error(f"Request gagal dengan status code {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_vectorization_status():
    """Test: GET /api/v1/vectorization/status"""
    print_header("TEST 2: Get Vectorization Status")

    endpoint = f"{BASE_URL}/api/v1/vectorization/status"
    print_request("GET", endpoint)

    try:
        response = requests.get(endpoint, timeout=10)
        print_response(response.json(), response.status_code)

        if response.status_code == 200:
            data = response.json()
            db_papers = data.get("database", {}).get("total_papers_in_db", 0)
            cache_status = data.get("cache", {}).get("status", "unknown")

            print_success(f"Database: {db_papers} papers")
            print_success(f"Cache Status: {cache_status}")
            return True
        else:
            print_error(f"Request gagal dengan status code {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_vectorize_all_papers():
    """Test: POST /api/v1/vectorize-all-papers"""
    print_header("TEST 3: Vectorize All Papers")

    print_info("⚠️  Proses ini akan memakan waktu lama (5-15 menit)")
    print_info("Tekan Ctrl+C untuk membatalkan")

    endpoint = f"{BASE_URL}/api/v1/vectorize-all-papers"
    print_request("POST", endpoint)

    params = {
        "batch_size": 100
    }

    try:
        print_info("Memulai vectorization...")
        start_time = time.time()

        response = requests.post(endpoint, params=params, timeout=600)
        elapsed_time = time.time() - start_time

        print_response(response.json(), response.status_code)

        if response.status_code == 200:
            print_success(f"Vectorization selesai dalam {elapsed_time:.2f} detik")
            return True
        else:
            print_error(f"Vectorization gagal dengan status code {response.status_code}")
            return False

    except requests.Timeout:
        print_error("Request timeout - vectorization memakan waktu terlalu lama")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_cache_status():
    """Test: GET /api/v1/cache/status"""
    print_header("TEST 4: Get Cache Status (Quick Check)")

    endpoint = f"{BASE_URL}/api/v1/cache/status"
    print_request("GET", endpoint)

    headers = {
        "Authorization": "Bearer test_token"  # Sesuaikan dengan token yang valid
    }

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)

        if response.status_code == 401 or response.status_code == 403:
            print_info("Skipped: Memerlukan authentication")
            return True

        print_response(response.json(), response.status_code)

        if response.status_code == 200:
            print_success("Cache status retrieved successfully")
            return True
        else:
            print_error(f"Request gagal dengan status code {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_clear_cache():
    """Test: DELETE /api/v1/cache/clear"""
    print_header("TEST 5: Clear Cache")

    print_info("⚠️  Operasi ini akan MENGHAPUS cache. Tidak bisa dibatalkan!")
    confirm = input("Ketik 'yes' untuk melanjutkan: ").strip().lower()

    if confirm != "yes":
        print_info("Skipped: User membatalkan operasi")
        return True

    endpoint = f"{BASE_URL}/api/v1/cache/clear"
    print_request("DELETE", endpoint)

    headers = {
        "Authorization": "Bearer test_token"  # Sesuaikan dengan token yang valid
    }

    try:
        response = requests.delete(endpoint, headers=headers, timeout=10)
        print_response(response.json(), response.status_code)

        if response.status_code == 200:
            print_success("Cache cleared successfully")
            return True
        else:
            print_error(f"Clear cache gagal dengan status code {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Main test runner"""
    print(f"{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════╗")
    print("║     Cache & Vectorization Endpoints Test Suite    ║")
    print("╚════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    print_info(f"Base URL: {BASE_URL}")
    print_info("Pastikan API server sudah running...")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("API server sudah berjalan")
        else:
            print_error("API server responding with error")
            return
    except requests.ConnectionError:
        print_error("Tidak bisa terhubung ke API server")
        print_info("Jalankan: uvicorn app.main:app --reload")
        return

    # Run tests
    tests = [
        ("Cache Info", test_cache_info),
        ("Vectorization Status", test_vectorization_status),
        ("Vectorize All Papers", test_vectorize_all_papers),
        ("Cache Status", test_cache_status),
        ("Clear Cache", test_clear_cache),
    ]

    print("\nPilih test yang ingin dijalankan:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"{i}. {name}")
    print("0. Jalankan semua test")
    print("q. Keluar")

    choice = input("\nPilihan: ").strip().lower()

    if choice == "q":
        print_info("Keluar dari test suite")
        return

    if choice == "0":
        # Run all tests
        for name, test_func in tests:
            try:
                test_func()
                print()
            except KeyboardInterrupt:
                print_error("\nTest dibatalkan oleh user")
                break
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tests):
                name, test_func = tests[idx]
                print(f"\nMenjalankan: {name}")
                test_func()
            else:
                print_error("Pilihan tidak valid")
        except ValueError:
            print_error("Pilihan harus berupa angka")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Test suite selesai!{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Program dihentikan oleh user{Colors.ENDC}")
