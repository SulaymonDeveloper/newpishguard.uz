# PhishGuard.uz v1.2.1 - Hotfix

## Issues Fixed

### 1. Login Crash (AttributeError) ✅
**Error**: `AttributeError: 'sqlite3.Row' object has no attribute 'get'`
**Location**: `app.py` line 199-200 in `login()` function
**Cause**: sqlite3.Row objects don't support `.get()` method

**Fix Applied**:
- Convert `sqlite3.Row` to `dict` after `fetchone()`
- Changed: `user = conn.execute(...).fetchone()`
- To: `user_row = conn.execute(...).fetchone()` then `user = dict(user_row)`
- Now `.get('name', '')` and `.get('surname', '')` work correctly

**Result**: ✅ No more AttributeError on login

### 2. Login Card Width ✅
**Request**: Make login card slightly wider

**Changes**:
- `login.html`: Increased from 540px to **580px**
- `register.html`: Increased from 540px to **580px** (to match)
- Maintains responsive design with `width: 100%`
- Same padding, border-radius, and styling

**Result**: ✅ Login/register cards are now wider and more spacious

---

## Technical Details

**Files Modified**:
1. `app.py` - Fixed login route (lines 185-208)
2. `templates/login.html` - Updated card width to 580px
3. `templates/register.html` - Updated card width to 580px

**No Other Changes**:
- All navigation working
- All quizzes working
- User display working
- Continue button working
- Design preserved

---

## Quick Start

```bash
unzip phishguard_flask_app_v1.2.1.zip
cd phishguard_app
pip install -r requirements.txt
python app.py
```

**Access**: http://localhost:5000  
**Login**: `admin` / `sulaymon123`

---

**Version**: 1.2.1  
**Date**: February 2, 2026  
**Status**: Production Ready ✅
