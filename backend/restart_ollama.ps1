# Restart Ollama and verify it's ready

Write-Host "Starting Ollama..." -ForegroundColor Yellow

# Start ollama (adjust path if needed - usually it's in Program Files or user AppData)
$ollamaPath = "ollama"  # Assumes ollama.exe is in PATH

try {
    Start-Process $ollamaPath -WindowStyle Hidden
    Start-Sleep -Seconds 5
    
    # Verify it's running
    $process = Get-Process ollama -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "✓ Ollama process started (PID: $($process.Id))" -ForegroundColor Green
        
        # Test API
        Start-Sleep -Seconds 3
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -TimeoutSec 10
        Write-Host "✓ Ollama API responding (version: $($response.version))" -ForegroundColor Green
        
        # List models
        $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10
        $modelNames = $models.models | ForEach-Object { $_.name }
        Write-Host "✓ Available models: $($modelNames -join ', ')" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "Ollama is ready!" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Ollama process not found" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manually start Ollama by running 'ollama serve' in a new terminal" -ForegroundColor Yellow
}
