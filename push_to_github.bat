@echo off
echo Initializing Git repository...
git init

echo Adding all files...
git add .

echo Committing changes...
git commit -m "Fix Railway deployment issues: update next.config.js and Dockerfiles"

echo Renaming branch to main...
git branch -M main

echo Adding remote origin...
git remote add origin https://github.com/SaiAvinashPatoju/sytescan.git

echo Pushing to GitHub...
git push -u origin main

echo Done!
pause
