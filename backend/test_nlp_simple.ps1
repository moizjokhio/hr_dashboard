# Test NLP Query - Simple version

$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "Testing NLP Query Service..." -ForegroundColor Cyan

# Test 1
Write-Host "`nTest 1: UBL Head Office departments" -ForegroundColor Yellow
$body1 = '{"query":"Show me all departments in UBL Head Office location"}'
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ai/query" -Method Post -Headers $headers -Body $body1 -TimeoutSec 30
    Write-Host "  Success: $($response.success)" -ForegroundColor Green
    Write-Host "  SQL: $($response.generated_sql.raw_sql)"
    Write-Host "  Rows: $($response.row_count)"
} catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2
Write-Host "`nTest 2: Grade AVP-I count" -ForegroundColor Yellow
$body2 = '{"query":"How many employees have grade AVP-I?"}'
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ai/query" -Method Post -Headers $headers -Body $body2 -TimeoutSec 30
    Write-Host "  Success: $($response.success)" -ForegroundColor Green
    Write-Host "  SQL: $($response.generated_sql.raw_sql)"
    Write-Host "  Rows: $($response.row_count)"
} catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3
Write-Host "`nTest 3: Average salary by department" -ForegroundColor Yellow
$body3 = '{"query":"What is the average salary by department?"}'
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ai/query" -Method Post -Headers $headers -Body $body3 -TimeoutSec 30
    Write-Host "  Success: $($response.success)" -ForegroundColor Green
    Write-Host "  SQL: $($response.generated_sql.raw_sql)"
    Write-Host "  Rows: $($response.row_count)"
} catch {
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest Complete!" -ForegroundColor Cyan
