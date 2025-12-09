@echo off
echo Restructuring Project...

:: Create Directories
if not exist "frontend" mkdir frontend
if not exist "backend" mkdir backend
if not exist "ml\models" mkdir ml\models
if not exist "ml\training" mkdir ml\training
if not exist "ml\runs" mkdir ml\runs
if not exist "scripts" mkdir scripts
if not exist "docs" mkdir docs

:: Move Scripts
echo Moving scripts...
if exist *.bat move *.bat scripts\
:: Move this script itself back to root if it gets moved? No, `move *.bat` will move it too if I name it .bat.
:: I will name it `run_restructure.bat` and exclude it or let it accept being moved.
:: Actually, if I run it, and it moves itself, the execution might stop.
:: Better to name it `.cmd` or explicit exclude.
:: Or hardcode the move for specific bats: cleanup.bat, push_to_github.bat, setup.bat, start-dev.bat, test-runner.bat.
if exist cleanup.bat move cleanup.bat scripts\
if exist push_to_github.bat move push_to_github.bat scripts\
if exist setup.bat move setup.bat scripts\
if exist start-dev.bat move start-dev.bat scripts\
if exist test-runner.bat move test-runner.bat scripts\

:: Move Docs
echo Moving documentation...
if exist DEPLOYMENT.md move DEPLOYMENT.md docs\
if exist DEV-SETUP.md move DEV-SETUP.md docs\
if exist DEVELOPMENT.md move DEVELOPMENT.md docs\

:: Move ML Files
echo Moving ML files...
if exist yolov8n.pt move yolov8n.pt ml\models\
if exist sytescan_training move sytescan_training ml\training\
if exist runs move runs ml\runs\

:: Move Backend Files
echo Moving backend config...
if exist Dockerfile.backend move Dockerfile.backend backend\Dockerfile
if exist requirements_final.txt move requirements_final.txt backend\

:: Move Frontend Files
echo Moving frontend files...
if exist Dockerfile.frontend move Dockerfile.frontend frontend\Dockerfile
if exist .env* move .env* frontend\
if exist .gitignore move .gitignore frontend\
if exist .next move .next frontend\
if exist .vscode move .vscode frontend\
if exist next-env.d.ts move next-env.d.ts frontend\
if exist next.config.js move next.config.js frontend\
if exist node_modules move node_modules frontend\
if exist package-lock.json move package-lock.json frontend\
if exist package.json move package.json frontend\
if exist postcss.config.js move postcss.config.js frontend\
if exist public move public frontend\
if exist src move src frontend\
if exist tailwind.config.js move tailwind.config.js frontend\
if exist tsconfig.json move tsconfig.json frontend\
if exist vitest.config.ts move vitest.config.ts frontend\

echo Project restructuring complete.
pause
