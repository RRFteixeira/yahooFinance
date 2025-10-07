param(
  [Parameter(Mandatory=$true, Position=0)]
  [ValidateSet("build","smoke","silver","batch","gold","nb","psql","logs")]
  [string]$Cmd,

  # capture remaining args as an array so positional calls work
  [Parameter(Position=1, ValueFromRemainingArguments=$true)]
  [string[]]$Args
)

# resolve compose files relative to this script
$Compose   = Join-Path $PSScriptRoot "..\docker\compose.spark.yml"
$DbCompose = Join-Path $PSScriptRoot "..\docker\compose.db.yml"

switch ($Cmd) {
  "build"  {
    docker compose -f $Compose build
  }

  "smoke"  {
    docker compose -f $Compose run --rm spark python3 -m src.transforms._smoke_spark
  }

  "silver" {
    if ($Args.Count -lt 1) { Write-Error "Usage: dev silver <bronze_parquet_path>"; exit 1 }
    docker compose -f $Compose run --rm spark python3 -m src.transforms.transform_to_silver $Args[0]
  }

  "batch"  {
    if ($Args.Count -lt 1) { Write-Error "Usage: dev batch <YYYY_MM_DD> [category]"; exit 1 }
    if ($Args.Count -ge 2) {
      docker compose -f $Compose run --rm spark python3 -m src.transforms.run_silver_batch $Args[0] $Args[1]
    } else {
      docker compose -f $Compose run --rm spark python3 -m src.transforms.run_silver_batch $Args[0]
    }
  }

  "gold"   {
    if ($Args.Count -lt 1) { Write-Error "Usage: dev gold <YYYY_MM_DD>"; exit 1 }
    docker compose -f $Compose run --rm spark python3 -m src.transforms.silver_to_gold $Args[0]
  }

  "nb"     {
    docker compose -f $Compose run --rm -p 8888:8888 spark bash -lc "jupyter lab --ip=0.0.0.0 --no-browser --allow-root --ServerApp.root_dir=/app --NotebookApp.token=''"
  }

  "psql"   {
    docker compose -f $DbCompose exec postgres psql -U yfinance_app -d yfinance
  }

  "logs"   {
    if ($Args.Count -lt 1) { Write-Error "Usage: dev logs <YYYY_MM_DD>"; exit 1 }
    Get-Content (Join-Path $PSScriptRoot "..\data\silver\$($Args[0]).log") -Wait
  }

  default {
    Write-Host "Usage:"
    Write-Host "  .\scripts\dev.ps1 build"
    Write-Host "  .\scripts\dev.ps1 smoke"
    Write-Host "  .\scripts\dev.ps1 silver  <bronze_parquet_path>"
    Write-Host "  .\scripts\dev.ps1 batch   <YYYY_MM_DD> [category]"
    Write-Host "  .\scripts\dev.ps1 gold    <YYYY_MM_DD>"
    Write-Host "  .\scripts\dev.ps1 nb"
    Write-Host "  .\scripts\dev.ps1 psql"
    Write-Host "  .\scripts\dev.ps1 logs    <YYYY_MM_DD>"
  }
}
