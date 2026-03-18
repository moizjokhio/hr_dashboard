# Test NLP Query API with proper JSON escaping for PowerShell

$headers = @{
    "Content-Type" = "application/json"
}

$queries = @(
    @{
        name = "Test 1: UBL Head Office departments"
        body = @{
            query = "Show me all departments in UBL Head Office location"
        }
        expected = "odbc.LOCATION_NAME"
    },
    @{
        name = "Test 2: Grade AVP-I count"
        body = @{
            query = "How many employees have grade AVP-I?"
        }
        expected = "grade_level"
    },
    @{
        name = "Test 3: Average salary"
        body = @{
            query = "What is the average salary by department?"
        }
        expected = "total_monthly_salary"
    }
)

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "TESTING NLP QUERY SERVICE WITH CORRECTED SCHEMA" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

foreach ($test in $queries) {
    Write-Host "`n$($test.name)" -ForegroundColor Yellow
    
    $json = $test.body | ConvertTo-Json -Compress
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/ai/query" `
                                     -Method Post `
                                     -Headers $headers `
                                     -Body $json `
                                     -TimeoutSec 30
        
        $success = $response.success
        $sql = $response.generated_sql.raw_sql
        $rowCount = $response.row_count
        
        Write-Host "  Success: $success" -ForegroundColor $(if ($success) { "Green" } else { "Red" })
        Write-Host "  SQL: $sql"
        Write-Host "  Rows: $rowCount"
        
        if ($sql -like "*$($test.expected)*") {
            Write-Host "  ✓ CORRECT - Contains expected: $($test.expected)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ WRONG - Should contain: $($test.expected)" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
