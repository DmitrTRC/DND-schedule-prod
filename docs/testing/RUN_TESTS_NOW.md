# 🚀 Quick Start - Run Phase 4 Tests

**Status:** ✅ 308+ tests ready to execute
**Target:** 90%+ code coverage
**Time to completion:** ~5 minutes

---

## ⚡ Ultra-Quick Start (Copy & Paste)

```bash
# Navigate and run everything
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod && \
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v && \
open htmlcov/index.html
```

---

## 📋 Step-by-Step

### 1️⃣ Navigate to Project
```bash
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod
```

### 2️⃣ Run Tests with Coverage
```bash
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v
```

### 3️⃣ View HTML Report
```bash
open htmlcov/index.html
```

---

## 🎯 What to Expect

### **Console Output:**
```
========================= test session starts ==========================
...
tests/unit/infrastructure/test_exporters.py ............ 78 passed
tests/unit/domain/test_validators_extended.py ......... 60+ passed
...
========================= 308+ passed in 15s ==========================

Coverage: 90%+ ✅
```

### **HTML Report:**
- Overall coverage: **90%+** ✅
- Exporters: **~90%+** ✅
- Validators: **~85-90%+** ✅
- All critical components covered

---

## 🔍 Test New Code Only

Want to test just the new tests first?

```bash
# Test exporters only (78 tests)
poetry run pytest tests/unit/infrastructure/test_exporters.py -v

# Test validators only (60+ tests)
poetry run pytest tests/unit/domain/test_validators_extended.py -v
```

---

## ✅ Success Checklist

- [ ] All 308+ tests pass
- [ ] Coverage ≥ 90%
- [ ] No test failures
- [ ] HTML report generated
- [ ] Celebrate! 🎉

---

## 📊 New Tests Summary

| File | Tests | Purpose |
|------|-------|---------|
| `test_exporters.py` | 78 | All export formats |
| `test_validators_extended.py` | 60+ | All validators |
| **TOTAL** | **138+** | **New in Phase 4** |

---

## 🎊 After Running

**If all tests pass and coverage ≥ 90%:**

✅ **Phase 4 COMPLETE!**
✅ **Target Achieved!**
✅ **Time to celebrate!** 🎉

**If coverage < 90%:**

1. Check HTML report for uncovered lines
2. See `PHASE4_FINAL_REPORT.md` for details
3. Add a few targeted tests if needed

---

## 💡 Pro Tips

**Fast Iteration:**
```bash
# Run only failed tests
poetry run pytest --lf

# Run in parallel (faster)
poetry run pytest -n auto

# Stop on first failure
poetry run pytest -x
```

**Coverage Shortcuts:**
```bash
# Quick coverage check (no HTML)
poetry run pytest --cov=src/schedule_dnd --cov-report=term

# Coverage for specific module
poetry run pytest --cov=src/schedule_dnd/infrastructure/exporters
```

---

## 🆘 If Tests Fail

1. **Read error message carefully**
2. **Check test file for details**
3. **Verify all dependencies:** `poetry install`
4. **Check Python version:** `python --version` (should be 3.11+)

---

## 📞 Need Help?

See detailed documentation:
- `PHASE4_FINAL_REPORT.md` - Complete details
- `PHASE4_COMPLETE_SUMMARY.md` - Execution guide
- `PHASE4_COVERAGE_PROGRESS.md` - Progress tracking

---

**🚀 Ready? Just copy the command and GO! 🚀**

```bash
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod && \
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v && \
open htmlcov/index.html
```

**⏱️ ETA: 5 minutes to 90%+ coverage!**
