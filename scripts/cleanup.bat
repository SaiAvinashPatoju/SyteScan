@echo off
echo Cleaning up workspace...
echo --------------------------------

echo Deleting redundant scripts...
if exist run-tests.bat (
    del run-tests.bat
    echo - Deleted run-tests.bat
)
if exist test-runner.sh (
    del test-runner.sh
    echo - Deleted test-runner.sh
)
if exist run_sytescan_training.bat (
    del run_sytescan_training.bat
    echo - Deleted run_sytescan_training.bat
)
if exist train_francesco.bat (
    del train_francesco.bat
    echo - Deleted train_francesco.bat
)

echo.
echo Deleting temporary Python scripts...
if exist verify-deployment.py (
    del verify-deployment.py
    echo - Deleted verify-deployment.py
)
if exist readytrained_model.py (
    del readytrained_model.py
    echo - Deleted readytrained_model.py
)

echo.
echo Deleting logs...
if exist sytescan_training.log (
    del sytescan_training.log
    echo - Deleted sytescan_training.log
)

echo.
echo Deleting outdated reports...
if exist CURRENT_PROJECT_REPORT.md (
    del CURRENT_PROJECT_REPORT.md
    echo - Deleted CURRENT_PROJECT_REPORT.md
)
if exist demo_performance_report.md (
    del demo_performance_report.md
    echo - Deleted demo_performance_report.md
)
if exist FRANCESCO_TRAINING.md (
    del FRANCESCO_TRAINING.md
    echo - Deleted FRANCESCO_TRAINING.md
)
if exist PROJECT_REPORT.md (
    del PROJECT_REPORT.md
    echo - Deleted PROJECT_REPORT.md
)
if exist SUBMISSION_README.md (
    del SUBMISSION_README.md
    echo - Deleted SUBMISSION_README.md
)
if exist TEAM_PITCH_SCRIPT.md (
    del TEAM_PITCH_SCRIPT.md
    echo - Deleted TEAM_PITCH_SCRIPT.md
)
if exist TEAM_PRESENTATION_DRAFT.md (
    del TEAM_PRESENTATION_DRAFT.md
    echo - Deleted TEAM_PRESENTATION_DRAFT.md
)

echo.
echo --------------------------------
echo Cleanup complete!
pause
