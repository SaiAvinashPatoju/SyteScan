# SyteScan Scripts

This directory contains helper scripts for development, testing, and deployment.

## Directory Structure

```
scripts/
├── setup.sh          # Unix/Linux setup script
├── deploy.sh         # Deployment script
└── windows/          # Windows batch files
    ├── setup.bat       # Windows setup
    ├── start-dev.bat   # Start dev servers
    ├── test-runner.bat # Run tests
    └── cleanup.bat     # Clean build artifacts
```

## Usage

### Unix/Linux/macOS

```bash
# Make scripts executable (first time only)
chmod +x scripts/*.sh

# Setup project
./scripts/setup.sh

# Deploy locally with Docker
./scripts/deploy.sh local
```

### Windows

```cmd
REM Setup project
scripts\windows\setup.bat

REM Start development servers
scripts\windows\start-dev.bat

REM Run tests
scripts\windows\test-runner.bat

REM Clean build artifacts
scripts\windows\cleanup.bat
```

### Using Make (Recommended)

If you have Make available (via WSL, Git Bash, or native):

```bash
make setup      # Install dependencies
make run        # Run instructions
make test       # Run all tests
make lint       # Run linters
make clean      # Remove caches
make docker-up  # Start Docker containers
```

## Script Descriptions

| Script | Purpose |
|--------|---------|
| `setup.sh` / `setup.bat` | Install all dependencies (npm + pip) |
| `start-dev.bat` | Start frontend and backend servers |
| `test-runner.bat` | Run all test suites |
| `cleanup.bat` | Remove __pycache__, .next, etc. |
| `deploy.sh` | Deploy with Docker (local or production) |

## Notes

- Scripts should be run from the project root directory
- Windows scripts use `venv\Scripts\` paths
- Unix scripts use `venv/bin/` paths
- All scripts include error handling and status messages
