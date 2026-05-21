# Async Vectorization API - Complete Guide

## 🎯 Overview

Endpoint async vectorization memungkinkan proses vectorization yang **tidak akan timeout** karena dijalankan di **background thread**. Response langsung kembali dengan `job_id` untuk polling status.

### Masalah yang Diselesaikan
- ❌ **Synchronous endpoint**: Timeout untuk dataset besar (5-15 menit)
- ✅ **Async endpoint**: Response immediate, tidak timeout
- ✅ **Progress tracking**: Real-time polling untuk monitor progress
- ✅ **Multiple jobs**: Bisa jalankan multiple vectorization sekaligus
- ✅ **Cancellation**: Bisa cancel pending jobs

---

## 📋 Endpoints

### 1. **POST `/api/v1/vectorize-async`** - Start Async Vectorization

**Deskripsi:** Start vectorization di background thread. Response immediate dengan job_id.

**Parameters:**
```
batch_size: int (default: 100)
  - Ukuran batch untuk processing
  - Smaller batch = more memory efficient tapi lebih slow
  - Larger batch = faster tapi lebih banyak memory
```

**Example Request:**
```bash
# Dengan default batch size
curl -X POST "http://localhost:8000/api/v1/vectorize-async"

# Dengan custom batch size
curl -X POST "http://localhost:8000/api/v1/vectorize-async?batch_size=50"
```

**Example Response (Success):**
```json
{
  "status": "success",
  "message": "Vectorization started in background",
  "data": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "batch_size": 100,
    "status_url": "/api/v1/vectorization-job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status",
    "next_step": "Poll status dengan: GET /api/v1/vectorization-job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status"
  }
}
```

**Error Response (Too Many Jobs):**
```json
{
  "status": "error",
  "message": "Too many vectorization jobs running (3). Please wait for some to complete."
}
```

---

### 2. **GET `/api/v1/vectorization-job/{job_id}/status`** - Check Job Status

**Deskripsi:** Polling status vectorization job. Gunakan job_id dari response POST vectorize-async.

**Parameters:**
```
job_id: str (path parameter)
  - Job ID dari POST /vectorize-async response
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/vectorization-job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status"
```

**Example Response (Pending):**
```json
{
  "status": "success",
  "data": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "pending",
    "created_at": "2026-05-18T14:30:00.123456",
    "started_at": null,
    "completed_at": null,
    "progress": {
      "total_papers": 0,
      "processed_papers": 0,
      "progress_percentage": 0,
      "current_batch": 0,
      "total_batches": 0
    },
    "elapsed_time_seconds": null,
    "batch_size": 100
  }
}
```

**Example Response (Running):**
```json
{
  "status": "success",
  "data": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "running",
    "created_at": "2026-05-18T14:30:00.123456",
    "started_at": "2026-05-18T14:30:05.234567",
    "completed_at": null,
    "progress": {
      "total_papers": 5000,
      "processed_papers": 1200,
      "progress_percentage": 24.0,
      "current_batch": 13,
      "total_batches": 50
    },
    "elapsed_time_seconds": 125.45,
    "batch_size": 100
  }
}
```

**Example Response (Completed):**
```json
{
  "status": "success",
  "data": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "created_at": "2026-05-18T14:30:00.123456",
    "started_at": "2026-05-18T14:30:05.234567",
    "completed_at": "2026-05-18T14:45:30.567890",
    "progress": {
      "total_papers": 5000,
      "processed_papers": 5000,
      "progress_percentage": 100.0,
      "current_batch": 50,
      "total_batches": 50
    },
    "elapsed_time_seconds": 925.33,
    "batch_size": 100,
    "result": {
      "total_papers_processed": 5000,
      "cosine_matrix_size": "5000x5000",
      "batch_size_used": 100,
      "cached": true
    }
  }
}
```

**Example Response (Failed):**
```json
{
  "status": "success",
  "data": {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "failed",
    "created_at": "2026-05-18T14:30:00.123456",
    "started_at": "2026-05-18T14:30:05.234567",
    "completed_at": "2026-05-18T14:31:00.890123",
    "progress": {
      "total_papers": 5000,
      "processed_papers": 500,
      "progress_percentage": 10.0,
      "current_batch": 5,
      "total_batches": 50
    },
    "elapsed_time_seconds": 55.65,
    "batch_size": 100,
    "error": {
      "message": "Database connection error",
      "traceback": "..."
    }
  }
}
```

---

### 3. **DELETE `/api/v1/vectorization-job/{job_id}/cancel`** - Cancel Job

**Deskripsi:** Cancel pending job. Hanya bisa cancel job dengan status `pending`, tidak bisa cancel job yang sudah `running`.

**Parameters:**
```
job_id: str (path parameter)
  - Job ID dari POST /vectorize-async response
```

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/vectorization-job/a1b2c3d4-e5f6-7890-abcd-ef1234567890/cancel"
```

**Example Response (Success):**
```json
{
  "status": "success",
  "message": "Job a1b2c3d4-e5f6-7890-abcd-ef1234567890 cancelled successfully"
}
```

**Error Response (Cannot Cancel):**
```json
{
  "status": "error",
  "message": "Cannot cancel job - job status is 'running' (only pending jobs can be cancelled)"
}
```

---

### 4. **GET `/api/v1/vectorization-jobs`** - List All Jobs

**Deskripsi:** List semua vectorization jobs dengan status mereka. Useful untuk monitoring.

**Parameters:** None

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/vectorization-jobs"
```

**Example Response:**
```json
{
  "status": "success",
  "total_jobs": 3,
  "active_jobs": 1,
  "data": {
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890": {
      "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "status": "completed",
      "created_at": "2026-05-18T14:30:00.123456",
      "started_at": "2026-05-18T14:30:05.234567",
      "completed_at": "2026-05-18T14:45:30.567890",
      "progress": {
        "total_papers": 5000,
        "processed_papers": 5000,
        "progress_percentage": 100.0,
        "current_batch": 50,
        "total_batches": 50
      },
      "elapsed_time_seconds": 925.33,
      "batch_size": 100,
      "result": {
        "total_papers_processed": 5000,
        "cosine_matrix_size": "5000x5000",
        "batch_size_used": 100,
        "cached": true
      }
    },
    "b2c3d4e5-f6a7-8901-bcde-f12345678901": {
      "job_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "status": "running",
      "created_at": "2026-05-18T14:50:00.123456",
      "started_at": "2026-05-18T14:50:05.234567",
      "completed_at": null,
      "progress": {
        "total_papers": 5000,
        "processed_papers": 2500,
        "progress_percentage": 50.0,
        "current_batch": 25,
        "total_batches": 50
      },
      "elapsed_time_seconds": 462.78,
      "batch_size": 100
    }
  }
}
```

---

## 🚀 Usage Workflows

### Workflow 1: Simple Vectorization
```bash
# 1. Start vectorization
JOB_ID=$(curl -X POST "http://localhost:8000/api/v1/vectorize-async" | jq -r '.data.job_id')

# 2. Poll status (repeat until completed)
curl -X GET "http://localhost:8000/api/v1/vectorization-job/$JOB_ID/status" | jq '.data.status'

# 3. Get final result
curl -X GET "http://localhost:8000/api/v1/vectorization-job/$JOB_ID/status" | jq '.data.result'
```

### Workflow 2: Monitor Progress in Loop
```bash
#!/bin/bash

JOB_ID=$(curl -X POST "http://localhost:8000/api/v1/vectorize-async" | jq -r '.data.job_id')
echo "Started job: $JOB_ID"

while true; do
  STATUS=$(curl -s -X GET "http://localhost:8000/api/v1/vectorization-job/$JOB_ID/status" | jq '.data')
  
  JOB_STATUS=$(echo "$STATUS" | jq -r '.status')
  PROGRESS=$(echo "$STATUS" | jq '.progress.progress_percentage')
  ELAPSED=$(echo "$STATUS" | jq '.elapsed_time_seconds')
  
  echo "Status: $JOB_STATUS | Progress: $PROGRESS% | Elapsed: $ELAPSED s"
  
  if [ "$JOB_STATUS" = "completed" ] || [ "$JOB_STATUS" = "failed" ]; then
    break
  fi
  
  sleep 5
done

# Show final result
curl -s -X GET "http://localhost:8000/api/v1/vectorization-job/$JOB_ID/status" | jq '.data'
```

### Workflow 3: Multiple Jobs dengan Polling
```python
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def start_vectorization(batch_size=100):
    """Start vectorization job"""
    response = requests.post(
        f"{BASE_URL}/vectorize-async",
        params={"batch_size": batch_size}
    )
    return response.json()["data"]["job_id"]

def check_status(job_id):
    """Check job status"""
    response = requests.get(
        f"{BASE_URL}/vectorization-job/{job_id}/status"
    )
    return response.json()["data"]

def wait_for_completion(job_id, check_interval=5):
    """Wait for job to complete dengan polling"""
    while True:
        status = check_status(job_id)
        job_status = status["status"]
        progress = status["progress"]["progress_percentage"]
        elapsed = status["elapsed_time_seconds"]
        
        print(f"Job {job_id[:8]}... | Status: {job_status} | Progress: {progress}% | Elapsed: {elapsed}s")
        
        if job_status in ("completed", "failed", "cancelled"):
            return status
        
        time.sleep(check_interval)

# Main
print("Starting vectorization...")
job_id = start_vectorization(batch_size=100)
print(f"Job ID: {job_id}")

print("\nWaiting for completion...")
final_status = wait_for_completion(job_id)
print(f"\nFinal Status: {final_status['status']}")
print(f"Result: {json.dumps(final_status.get('result'), indent=2)}")
```

---

## 📊 Polling Strategy

### Smart Polling Pattern
```python
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"

def poll_with_backoff(job_id, initial_interval=1, max_interval=30):
    """Poll dengan exponential backoff"""
    interval = initial_interval
    
    while True:
        response = requests.get(f"{BASE_URL}/vectorization-job/{job_id}/status")
        status = response.json()["data"]
        
        print(f"Progress: {status['progress']['progress_percentage']}%")
        
        if status["status"] in ("completed", "failed"):
            return status
        
        time.sleep(interval)
        interval = min(interval * 1.5, max_interval)  # Exponential backoff
```

### Polling Recommendations
- **Awal (0-20% progress)**: Poll setiap 5-10 detik (proses cepat)
- **Tengah (20-80% progress)**: Poll setiap 10-20 detik
- **Akhir (80-100% progress)**: Poll setiap 20-30 detik (proses melambat)
- **Max interval**: Tidak perlu lebih dari 30 detik

---

## 🔄 Status Transitions

```
┌──────────┐
│ PENDING  │ (Job baru dibuat)
└────┬─────┘
     │ (start_vectorization_async dijalankan)
     ▼
┌──────────┐
│ RUNNING  │ (Vectorization sedang berjalan)
└────┬─────┘
     │
     ├─────────────────────┐
     │                     │
     ▼                     ▼
┌──────────┐         ┌──────────┐
│COMPLETED │         │ FAILED   │
└──────────┘         └──────────┘

Alternative untuk PENDING:
┌──────────┐
│ PENDING  │
└────┬─────┘
     │ (cancel dijalankan sebelum start)
     ▼
┌──────────┐
│CANCELLED │
└──────────┘
```

---

## ⚙️ Configuration

### Max Concurrent Jobs
Default: 3 jobs
Bisa diubah di `recommender_api.py` pada endpoint `vectorize-all-papers-async`:
```python
if active_count > 3:  # Change this number
    raise HTTPException(status_code=429, ...)
```

### Job Cleanup
Jobs otomatis di-cleanup setelah 24 jam (default).
Untuk manual cleanup:
```python
async_service = get_vectorization_async_service()
removed_count = async_service.cleanup_old_jobs(keep_hours=24)
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Job ID not found | Cek job_id sudah benar, atau job sudah di-cleanup |
| Cannot cancel running job | Hanya pending jobs yang bisa di-cancel |
| Too many jobs running | Tunggu beberapa job selesai, or increase max limit |
| Job stuck at 0% | Cek logs, mungkin ada error di database |
| Timeout when polling | Increase timeout di client, atau check server |

---

## 📈 Performance Tips

1. **Batch Size Selection**
   - Small batch (25-50): Lebih stabil, memory efficient
   - Large batch (200-500): Lebih cepat, tapi memory heavy
   - Default (100): Good balance

2. **Polling Frequency**
   - Too frequent: Waste resources
   - Too sparse: Lambat detect completion
   - Recommended: 5-30 second intervals

3. **Concurrent Jobs**
   - Default limit: 3 jobs
   - Untuk server dengan resources besar, bisa increase
   - Batasan: CPU dan memory availability

4. **Database Optimization**
   - Ensure indices on important columns
   - Check connection pool size
   - Monitor query performance

---

## 🔐 Security Considerations

1. **No Authentication Required** (Default)
   - Dapat diakses siapa saja
   - Pertimbangkan untuk menambahkan auth jika sensitive

2. **Job ID Format**
   - UUID v4 format (128-bit, practically unique)
   - Tidak predictable (aman dari enumeration)

3. **Resource Limits**
   - Max 3 concurrent jobs (prevent DoS)
   - Bisa configure di code
   - Consider adding rate limiting

---

## 📋 Example: Complete Python Client

```python
import requests
import time
import json
from typing import Optional, Dict, Any

class AsyncVectorizationClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def start_vectorization(self, batch_size=100) -> str:
        """Start vectorization dan return job_id"""
        response = requests.post(
            f"{self.api_base}/vectorize-async",
            params={"batch_size": batch_size}
        )
        response.raise_for_status()
        return response.json()["data"]["job_id"]
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get current job status"""
        response = requests.get(
            f"{self.api_base}/vectorization-job/{job_id}/status"
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def cancel(self, job_id: str) -> bool:
        """Cancel pending job"""
        response = requests.delete(
            f"{self.api_base}/vectorization-job/{job_id}/cancel"
        )
        return response.status_code == 200
    
    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 3600,
        check_interval: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Wait for job completion dengan timeout"""
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Job {job_id} timeout after {timeout}s")
            
            status = self.get_status(job_id)
            progress = status["progress"]["progress_percentage"]
            
            print(f"[{int(elapsed)}s] Progress: {progress}%")
            
            if status["status"] in ("completed", "failed", "cancelled"):
                return status
            
            time.sleep(check_interval)

# Usage
client = AsyncVectorizationClient()

# Start
job_id = client.start_vectorization(batch_size=100)
print(f"Started job: {job_id}")

# Wait
try:
    result = client.wait_for_completion(job_id, timeout=1800)
    print(f"Completed! Result: {json.dumps(result, indent=2)}")
except TimeoutError as e:
    print(f"Error: {e}")
    client.cancel(job_id)
```

---

**Last Updated:** 2026-05-18  
**Status:** ✅ Ready for Production  
**Version:** 1.0.0
