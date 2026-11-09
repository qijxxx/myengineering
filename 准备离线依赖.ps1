$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path "vendor" | Out-Null

Write-Host "正在下载 SheetJS..."
Invoke-WebRequest -Uri "https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js" -OutFile "vendor\xlsx.full.min.js"

Write-Host "正在下载 jsPDF..."
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" -OutFile "vendor\jspdf.umd.min.js"

Write-Host "正在下载 html2canvas..."
Invoke-WebRequest -Uri "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" -OutFile "vendor\html2canvas.min.js"

Write-Host ""
Write-Host "离线依赖准备完成。"
Read-Host "按回车退出"
