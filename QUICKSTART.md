# PhishGuard.uz - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Extract the ZIP
Extract `phishguard_flask_app.zip` to a folder on your computer

### Step 2: Install Dependencies
Open terminal/command prompt in the extracted folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
**On Windows:**
- Double-click `run.bat`

**On Mac/Linux:**
```bash
./run.sh
```

**Or manually:**
```bash
python app.py
```

### Step 4: Access the Application
Open your browser and go to: **http://localhost:5000**

---

## 🔐 Login Credentials

**Built-in Admin Account:**
- Username: `admin`
- Password: `sulaymon123`

**Create New User:**
- Click "Register new account" on the login page
- Choose any username and password

---

## 📚 Application Structure

```
phishguard_app/
├── app.py              # Main Flask application (DO NOT MODIFY)
├── run.sh              # Linux/Mac startup script
├── run.bat             # Windows startup script
├── requirements.txt    # Python dependencies
├── README.md           # Full documentation
├── templates/          # All HTML files (DESIGN PRESERVED)
│   ├── login.html
│   ├── modules.html
│   ├── m1-lesson1.html ... m3-lesson5.html (16 lessons)
│   ├── final-exam.html
│   ├── certificate.html
│   └── admin_exam.html
└── static/             # Static files (currently empty)
```

---

## ✅ Features Included

- ✓ User authentication (login/register)
- ✓ Session-based security
- ✓ Password hashing
- ✓ 3 training modules (16 total lessons)
- ✓ Progress tracking (SQLite database)
- ✓ Final exam (10 questions)
- ✓ Certificate generation
- ✓ Admin panel for exam management
- ✓ Bilingual support (EN/UZ)
- ✓ Responsive design (mobile-friendly)

---

## 🎯 User Flow

1. **Login/Register** → Start at login page
2. **View Modules** → See 3 modules on dashboard
3. **Complete Lessons** → Go through each module's lessons
4. **Unlock Exam** → Final exam unlocks after completing all modules
5. **Take Exam** → Score 70% or higher to pass
6. **Get Certificate** → View and print your certificate

---

## 🔧 Admin Features

**Access Admin Panel:**
1. Login as `admin` with password `sulaymon123`
2. Go to: http://localhost:5000/admin/exam-questions
3. Add, edit, or delete exam questions
4. Changes apply immediately

---

## 📋 Database Tables

The application automatically creates a `phishguard.db` SQLite database with:

- **users** - User accounts
- **progress** - Learning progress for each user
- **exam_questions** - Final exam questions (editable by admin)

---

## ⚠️ Important Notes

### Design Preservation
✅ **All HTML/CSS designs are EXACTLY as provided**
- No layout changes
- No color modifications
- No font changes
- Only dynamic content (user data, progress) is added via Flask/Jinja2

### Security
🔒 **For Production Use:**
1. Change `app.secret_key` in `app.py` to a secure random string
2. Set `debug=False`
3. Use HTTPS
4. Consider using PostgreSQL instead of SQLite

### Progress Tracking
💾 **Progress is stored in the database, NOT in browser localStorage**
- Each user has their own progress
- Progress persists across sessions
- No data loss on browser clear

---

## 🐛 Troubleshooting

**Port 5000 already in use?**
```bash
# Kill the process using port 5000
# On Linux/Mac:
lsof -ti:5000 | xargs kill -9

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Database errors?**
```bash
# Delete and recreate database
rm phishguard.db
python app.py
```

**Can't login?**
- Check username/password (case-sensitive)
- Ensure database exists
- Try resetting: delete `phishguard.db` and restart

**Module not unlocking?**
- Complete ALL lessons in the previous modules
- Check progress on home page

---

## 📞 Need Help?

1. Check `README.md` for full documentation
2. Review Flask logs in the terminal
3. Check database with SQLite browser: https://sqlitebrowser.org/

---

## 🎓 System Requirements

- Python 3.7 or higher
- Flask 3.0.0
- SQLite (built into Python)
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

**Built with Flask + SQLite | All Original Designs Preserved | Production-Ready**
