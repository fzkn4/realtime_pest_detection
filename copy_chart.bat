@echo off
echo Copying Chart.js...
if not exist "static\js" mkdir "static\js"
copy /Y "node_modules\chart.js\dist\chart.umd.min.js" "static\js\Chart.min.js"
if exist "static\js\Chart.min.js" (
    echo SUCCESS: Chart.min.js copied successfully!
) else (
    echo ERROR: Failed to copy file
    pause
)

