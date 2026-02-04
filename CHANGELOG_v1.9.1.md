# PhishGuard v1.9.1 — Admin/User Separation

## Changes

### Admin Login Flow
- Admin users (`is_admin=1`) now log directly into the **Exam Question Manager** at `/admin/exam-questions`
- Regular users continue to `/home` (modules dashboard) as before
- The root `/` route checks `is_admin` and routes accordingly

### Admin Interface
- Admin page shows **only** the Final Exam question editor
- No modules, lessons, progress tracker, or certificate links for admins
- "Back to Home" link changed to "Logout" — admins have no home dashboard
- All existing admin protections remain (`@admin_required` decorator)

### User Interface
- Regular users cannot access `/admin/exam-questions` (403 redirect to `/home`)
- No changes to student experience — modules, lessons, exams work identically

## Files Modified
1. `app.py`:
   - `login()` route: Conditional redirect based on `is_admin`
   - `index()` route: Same conditional logic for already-logged-in users
2. `templates/admin_exam.html`:
   - Changed "Back to Home" link to "Logout"

## Testing
- Admin login → `/admin/exam-questions` ✓
- Regular user login → `/home` ✓
- Non-admin trying `/admin/exam-questions` → 403 + redirect ✓
- Root `/` respects `is_admin` session flag ✓

## Hotfix: JSON Serialization Error

### Issue
Admin exam page crashed with `TypeError: Object of type Row is not JSON serializable` when clicking Edit button.

### Root Cause
`admin_exam_questions()` route passed `sqlite3.Row` objects directly to template. The Jinja `tojson` filter cannot serialize Row objects.

### Fix
Line 606 in `app.py`:
```python
# Before:
questions = conn.execute("SELECT * FROM exam_questions ORDER BY id").fetchall()

# After:
questions = [dict(row) for row in conn.execute("SELECT * FROM exam_questions ORDER BY id").fetchall()]
```

Converts Row objects to plain Python dicts before template rendering. The `tojson` filter now works correctly in `admin_exam.html`.

### Tested
- Dict serialization ✓
- Apostrophes and quotes in question text ✓
- Edit modal receives valid JSON ✓
- Add/Edit/Delete functionality unchanged ✓

## Update 2: Admin Edit Fix + Change Password Feature

### 1. Fixed: Admin Edit Button Not Working

**Issue:** When clicking Edit in admin exam page, the modal opened but changes could not be saved. The root cause was improper JSON serialization in the onclick attribute.

**Fix:** Changed from inline JSON in onclick to data attribute pattern:
```html
<!-- Before (broken - quotes break HTML parsing): -->
<button onclick="openModal({{ q|tojson }})">Edit</button>

<!-- After (working): -->
<button data-question="{{ q|tojson|forceescape }}" 
        onclick="openModal(JSON.parse(this.getAttribute('data-question')))">Edit</button>
```

The `tojson|forceescape` filter properly escapes quotes for HTML attributes, and `JSON.parse()` decodes it client-side.

**Tested:**
- Questions with quotes and apostrophes ✓
- Edit modal loads all fields (EN + UZ) ✓
- Save/Update sends to backend correctly ✓
- Page refreshes after successful update ✓

### 2. New Feature: Change Password

**Added:** `/change-password` route and template for logged-in users to update their password.

**Features:**
- Requires current password (prevents unauthorized changes)
- New password validation (min 6 chars, match confirmation)
- Secure hash update in SQLite
- Works for both admin and regular users
- Flash messages for errors/success
- Bilingual UI (EN/UZ)

**Access:**
- Admin page: "Change Password" link in top navigation
- User dashboard: "Change Password" button in header (next to Logout)

**Files Modified:**
1. `app.py`:
   - Added `/change-password` route with GET/POST handlers
   - Validates old password, checks new password requirements
   - Updates `password_hash` in users table
2. `templates/change_password.html`:
   - New template matching login page design
   - Three fields: current, new, confirm passwords
   - Redirects to appropriate page after success (admin → exam manager, user → home)
3. `templates/admin_exam.html`:
   - Added "Change Password" link in header
4. `templates/modules.html`:
   - Added "Change Password" button in navigation
   - Added translations for `nav-change-password`

**Testing:**
- Password hash generation ✓
- Old password verification ✓
- New password validation (length, match) ✓
- DB update ✓
- Admin and user flows ✓
