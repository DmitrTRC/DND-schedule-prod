# 🚀 Setup Instructions for Schedule DND

**Author:** DmitrTRC  
**Repository:** https://github.com/DmitrTRC/schedule-dnd

---

## ⚠️ Important: Read This First!

The setup process requires **TWO phases**:

1. **Phase 1**: Copy configuration files from Claude artifacts
2. **Phase 2**: Run automated setup script

**Do NOT skip Phase 1!** The setup script will fail without the configuration files.

---

## 📋 Phase 1: Copy Configuration Files

### Step 1: Identify Configuration Files

From Claude's conversation, you have received several **artifact files**. You need to copy these to your project:

| Artifact Name | Destination | Required |
|--------------|-------------|----------|
| `pyproject.toml` | Project root | ✅ YES |
| `.gitignore` | Project root | ✅ YES |
| `.env.example` | Project root | ✅ YES |
| `Makefile` | Project root | ✅ YES |
| `.pre-commit-config.yaml` | Project root | ✅ YES |
| `.github/workflows/ci.yml` | `.github/workflows/` | ✅ YES |

### Step 2: Create Required Directories

```bash
# If they don't exist, create:
mkdir -p .github/workflows
mkdir -p scripts
```

### Step 3: Copy Each File

**For each artifact from Claude:**

1. Click on the artifact in Claude's interface
2. Copy its content
3. Create the file in your project at the specified destination
4. Paste the content
5. Save the file

**Example for pyproject.toml:**

```bash
# In your project root
touch pyproject.toml

# Open in your editor and paste the content from Claude's artifact
vim pyproject.toml  # or nano, or your preferred editor
```

### Step 4: Verify Files Are in Place

Run the verification script:

```bash
# Make it executable
chmod +x scripts/copy_config_files.sh

# Run checker
./scripts/copy_config_files.sh
```

**Expected output if everything is correct:**
```
✓ pyproject.toml (exists in Project root)
✓ .gitignore (exists in Project root)
✓ .env.example (exists in Project root)
✓ Makefile (exists in Project root)
✓ .pre-commit-config.yaml (exists in Project root)
✓ .github/workflows/ci.yml (exists in GitHub workflows directory)

✓ All configuration files are in place!

You can now run:
  ./scripts/setup.sh
```

---

## 🎯 Phase 2: Run Automated Setup

Once all configuration files are in place:

### Step 1: Make Setup Script Executable

```bash
chmod +x scripts/setup.sh
```

### Step 2: Run Setup

```bash
./scripts/setup.sh
```

### What This Script Does:

1. ✅ Checks Python 3.11+ installation
2. ✅ Installs Poetry (if needed)
3. ✅ Creates complete project structure
4. ✅ Copies .env.example to .env
5. ✅ Installs all dependencies
6. ✅ Sets up pre-commit hooks
7. ✅ Initializes git repository
8. ✅ Creates initial commit

---

## 🔍 Troubleshooting

### Error: "pyproject.toml not found"

**Problem:** Configuration files not copied to project root.

**Solution:**
1. Go back to Phase 1
2. Run `./scripts/copy_config_files.sh` to see what's missing
3. Copy the missing files from Claude's artifacts
4. Run setup again

### Error: "Poetry could not find a pyproject.toml"

**Problem:** You're in the wrong directory, or pyproject.toml is in wrong location.

**Solution:**
```bash
# Check current directory
pwd

# Should be in project root like:
# /Users/yourusername/Projects/schedule-dnd

# Check if pyproject.toml exists
ls -la pyproject.toml

# If it doesn't exist, copy it from artifacts
```

### Error: "Permission denied"

**Problem:** Scripts are not executable.

**Solution:**
```bash
# Make all scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Error: "Python not found"

**Problem:** Python 3.11+ is not installed.

**Solution:**
```bash
# Check Python version
python3 --version

# If < 3.11 or not installed:
# On macOS:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11

# On Windows:
# Download from python.org
```

---

## ✅ Verification Checklist

After setup completes, verify everything works:

### Check 1: Python Environment

```bash
# Should show your virtual environment
poetry env info

# Should show installed packages
poetry show
```

### Check 2: Project Structure

```bash
# Should show the directory tree
tree -L 2 src/

# Or use ls
ls -R src/schedule_dnd/
```

### Check 3: Pre-commit Hooks

```bash
# Should show installed hooks
ls -la .git/hooks/

# Test pre-commit
poetry run pre-commit run --all-files
```

### Check 4: Run Tests

```bash
# Should pass (even if no tests yet)
make test
```

### Check 5: Check Commands

```bash
# Should show help
make help

# Should show version
poetry run schedule-dnd --version
```

---

## 🎉 Success!

If all checks pass, you're ready to start development:

```bash
# Activate virtual environment
poetry shell

# Start coding!
code .  # or your preferred editor
```

---

## 📚 Next Steps

1. Review the project structure in `src/schedule_dnd/`
2. Check out `docs/architecture.md` for architecture overview
3. Read `docs/contributing.md` for development guidelines
4. Start implementing domain models in `src/schedule_dnd/domain/`

---

## 🆘 Still Having Issues?

1. **Check this file again** - Make sure you followed all steps
2. **Run the checker**: `./scripts/copy_config_files.sh`
3. **Check file permissions**: `ls -la` to see if files exist
4. **Review error messages** - They usually tell you what's wrong
5. **Start fresh**: Delete everything and start over with Phase 1

---

## 📝 Quick Reference

**Configuration Files Location:**
```
project-root/
├── pyproject.toml              ← Claude artifact
├── .gitignore                  ← Claude artifact
├── .env.example                ← Claude artifact
├── Makefile                    ← Claude artifact
├── .pre-commit-config.yaml     ← Claude artifact
└── .github/
    └── workflows/
        └── ci.yml              ← Claude artifact
```

**Setup Commands:**
```bash
# Phase 1
./scripts/copy_config_files.sh  # Check what's missing

# Phase 2
./scripts/setup.sh              # Run full setup
```

**Common Commands:**
```bash
make help           # Show all commands
make dev-install    # Install dependencies
make test           # Run tests
make lint           # Check code quality
make format         # Format code
make ci             # Full CI pipeline locally
poetry shell        # Activate environment
```

---

**Last Updated:** October 2025  
**For Issues:** Check error messages and this guide  
**Maintained by:** DmitrTRC
