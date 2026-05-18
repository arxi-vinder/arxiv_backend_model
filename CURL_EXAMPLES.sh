#!/bin/bash

# Quick Reference: CURL Commands untuk Cache & Vectorization Endpoints
# Sesuaikan BASE_URL sesuai dengan API server Anda

BASE_URL="http://localhost:8000"
TOKEN="your_auth_token_here"

echo "╔════════════════════════════════════════════════════╗"
echo "║  Cache & Vectorization API - CURL Examples        ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# 1. GET Cache Information
# ============================================================
echo "1️⃣  GET CACHE INFORMATION"
echo "   (Equivalent: CLI 'cache-info' command)"
echo ""
echo "Command:"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/info\""
echo ""
echo "Description: Lihat informasi detail cache yang sudah ada"
echo ""
echo "---"
echo ""

# ============================================================
# 2. GET Vectorization Status
# ============================================================
echo "2️⃣  GET VECTORIZATION STATUS"
echo "   (Equivalent: CLI 'status' command)"
echo ""
echo "Command:"
echo "curl -X GET \"${BASE_URL}/api/v1/vectorization/status\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "Description: Lihat status lengkap database dan cache"
echo ""
echo "---"
echo ""

# ============================================================
# 3. POST Vectorize All Papers
# ============================================================
echo "3️⃣  POST VECTORIZE ALL PAPERS"
echo "   (Equivalent: CLI 'vectorize-all' command)"
echo "   ⚠️  WARNING: Proses ini memakan waktu 5-15 menit!"
echo ""
echo "Command (dengan default batch size 100):"
echo "curl -X POST \"${BASE_URL}/api/v1/vectorize-all-papers\""
echo ""
echo "Command (dengan custom batch size):"
echo "curl -X POST \"${BASE_URL}/api/v1/vectorize-all-papers?batch_size=50\""
echo ""
echo "Description: Vectorize semua papers dalam database dan simpan cache"
echo ""
echo "---"
echo ""

# ============================================================
# 4. GET Quick Cache Status
# ============================================================
echo "4️⃣  GET QUICK CACHE STATUS"
echo "   (Lebih ringkas dari cache/info)"
echo ""
echo "Command:"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/status\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "Description: Pengecekan cepat status cache"
echo ""
echo "---"
echo ""

# ============================================================
# 5. DELETE Clear Cache
# ============================================================
echo "5️⃣  DELETE CLEAR CACHE"
echo "   (Equivalent: CLI 'clear-cache' command)"
echo "   ⚠️  WARNING: Operasi ini TIDAK BISA DIBATALKAN!"
echo ""
echo "Command:"
echo "curl -X DELETE \"${BASE_URL}/api/v1/cache/clear\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "Description: Hapus cache (memerlukan authentication)"
echo ""
echo "---"
echo ""

# ============================================================
# 6. GET Recommendations (Bonus)
# ============================================================
echo "6️⃣  GET RECOMMENDATIONS (BONUS)"
echo ""
echo "Command:"
echo "curl -X GET \"${BASE_URL}/api/v1/recommend/1?top_n=5\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "Description: Get top 5 recommendations untuk paper ID 1"
echo "Parameters:"
echo "  - paper_id: ID paper yang ingin direkomendasi (path param)"
echo "  - top_n: Jumlah top recommendations (default: 5)"
echo ""
echo "---"
echo ""

# ============================================================
# 7. POST Refresh UCB Scores (Bonus)
# ============================================================
echo "7️⃣  POST REFRESH UCB SCORES (BONUS)"
echo ""
echo "Command:"
echo "curl -X POST \"${BASE_URL}/api/v1/recommend/1/refresh-ucb?top_n=5\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "Description: Refresh UCB scores untuk paper ID 1"
echo "Parameters:"
echo "  - paper_id: ID paper (path param)"
echo "  - top_n: Jumlah top recommendations (default: 5)"
echo ""
echo "---"
echo ""

# ============================================================
# WORKFLOW EXAMPLES
# ============================================================
echo "╔════════════════════════════════════════════════════╗"
echo "║        Common Workflows                           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Workflow 1: First Time Setup
echo "WORKFLOW 1: First Time Setup"
echo "═════════════════════════════"
echo ""
echo "# 1. Check if cache already exists"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/info\""
echo ""
echo "# 2. If no cache, start vectorization"
echo "curl -X POST \"${BASE_URL}/api/v1/vectorize-all-papers?batch_size=100\""
echo ""
echo "# 3. Wait for completion, then verify"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/info\""
echo ""
echo "# 4. Start using recommendations"
echo "curl -X GET \"${BASE_URL}/api/v1/recommend/1?top_n=5\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo ""

# Workflow 2: Daily Operations
echo "WORKFLOW 2: Daily Operations"
echo "════════════════════════════"
echo ""
echo "# 1. Check system status"
echo "curl -X GET \"${BASE_URL}/api/v1/vectorization/status\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "# 2. Get recommendations"
echo "curl -X GET \"${BASE_URL}/api/v1/recommend/123?top_n=5\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "# 3. Optional: Refresh UCB if needed"
echo "curl -X POST \"${BASE_URL}/api/v1/recommend/123/refresh-ucb?top_n=5\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo ""

# Workflow 3: Maintenance
echo "WORKFLOW 3: Maintenance (Re-vectorize)"
echo "══════════════════════════════════════"
echo ""
echo "# 1. Check current cache"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/info\""
echo ""
echo "# 2. Clear old cache"
echo "curl -X DELETE \"${BASE_URL}/api/v1/cache/clear\" \\"
echo "  -H \"Authorization: Bearer ${TOKEN}\""
echo ""
echo "# 3. Re-vectorize"
echo "curl -X POST \"${BASE_URL}/api/v1/vectorize-all-papers?batch_size=100\""
echo ""
echo "# 4. Verify new cache"
echo "curl -X GET \"${BASE_URL}/api/v1/cache/info\""
echo ""
echo ""

# ============================================================
# USEFUL TIPS
# ============================================================
echo "╔════════════════════════════════════════════════════╗"
echo "║        Useful Tips & Troubleshooting              ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

echo "💡 TIP 1: Check API Documentation"
echo "   URL: ${BASE_URL}/docs (Swagger UI)"
echo "   URL: ${BASE_URL}/redoc (ReDoc UI)"
echo ""

echo "💡 TIP 2: Pretty Print JSON Response"
echo "   Add pipe to jq:"
echo "   curl -X GET \"${BASE_URL}/api/v1/cache/info\" | jq ."
echo ""

echo "💡 TIP 3: Save Response to File"
echo "   curl -X GET \"${BASE_URL}/api/v1/cache/info\" > cache_info.json"
echo ""

echo "💡 TIP 4: Monitor Vectorization Progress"
echo "   Check logs atau gunakan /vectorization/status endpoint"
echo "   untuk melihat progress real-time"
echo ""

echo "💡 TIP 5: Get Token"
echo "   Dapatkan token dari endpoint /api/v1/auth/login"
echo "   atau sesuaikan dengan authentication method Anda"
echo ""

echo "⚠️  IMPORTANT NOTES:"
echo "   - Cache/info endpoint TIDAK memerlukan authentication"
echo "   - Cache/clear endpoint MEMERLUKAN authentication (security)"
echo "   - Vectorization bisa memakan waktu 5-15 menit"
echo "   - Cache file location: app/cache/vectorization/"
echo ""

# ============================================================
# ERROR HANDLING
# ============================================================
echo "╔════════════════════════════════════════════════════╗"
echo "║        Common Errors & Solutions                  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

echo "❌ Error: \"No cache found\""
echo "   Solution: Jalankan vectorization dengan POST /vectorize-all-papers"
echo ""

echo "❌ Error: \"Connection refused\""
echo "   Solution: Pastikan API server sudah running"
echo "   Command: uvicorn app.main:app --reload"
echo ""

echo "❌ Error: \"401 Unauthorized\""
echo "   Solution: Gunakan token yang valid di header Authorization"
echo "   Example: -H \"Authorization: Bearer your_token\""
echo ""

echo "❌ Error: \"Request timeout\""
echo "   Solution: Vectorization memakan waktu lama, tambah timeout"
echo "   curl --max-time 900 (15 minutes) untuk POST /vectorize-all-papers"
echo ""

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║             End of Quick Reference               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "For detailed documentation, see: CACHE_API_ENDPOINTS.md"
echo ""
