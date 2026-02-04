# PhishGuard.uz - Phishing Awareness Training Platform

A complete Flask-based phishing awareness training platform with user authentication, progress tracking, and exam management.

## Features

✅ **User Authentication**
- Session-based login system
- Password hashing with Werkzeug
- Built-in admin account (username: `admin`, password: `sulaymon123`)
- User registration

✅ **Progress Tracking**
- SQLite database stores user progress
- Track current module and lesson
- Automatically unlock final exam after completing all 3 modules
- Module completion status

✅ **Three Training Modules**
- Module 1: Introduction to Phishing (5 lessons)
- Module 2: Common Phishing Types in Uzbekistan (6 lessons)
- Module 3: Spotting Red Flags (5 lessons)

✅ **Final Exam**
- Locked until all modules are completed
- Dynamic question system from database
- 70% passing score required
- Automatic scoring

✅ **Certificate Generation**
- Awarded upon passing final exam
- Professional design
- Printable format
- Shows user name, score, and date

✅ **Admin Panel**
- Manage exam questions (add, edit, delete)
- Admin-only access
- Easy-to-use interface

✅ **Bilingual Support**
- English and Uzbek (O'zbek tili)
- Language switcher on all pages
- LocalStorage-based preference

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python app.py
```

3. **Access the application:**
- Open your browser and navigate to: `http://localhost:5000`

## Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `sulaymon123`

**Creating New Users:**
- Click "Register new account" on the login page
- Choose a username and password
- Login with your new credentials

## Project Structure

```
phishguard_app/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── phishguard.db              # SQLite database (created on first run)
├── templates/                  # HTML templates
│   ├── login.html             # Login page
│   ├── modules.html           # Home/Dashboard
│   ├── m1-lesson1.html        # Module 1, Lesson 1
│   ├── m1-lesson2.html        # ... and so on for all lessons
│   ├── final-exam.html        # Final examination
│   ├── certificate.html       # Certificate page
│   └── admin_exam.html        # Admin exam management
└── static/                     # Static files (if needed)
```

## Database Schema

### `users` table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `is_admin`: Admin flag (0 or 1)
- `created_at`: Registration timestamp

### `progress` table
- `user_id`: Foreign key to users
- `current_module`: Current module number (1-3)
- `current_lesson`: Current lesson number
- `modules_completed`: Comma-separated list of completed modules
- `final_exam_unlocked`: Boolean flag
- `final_exam_completed`: Boolean flag
- `final_exam_score`: Exam score (0-100)
- `updated_at`: Last update timestamp

### `exam_questions` table
- `id`: Primary key
- `question`: Question text
- `option_a`: Option A text
- `option_b`: Option B text
- `option_c`: Option C text
- `option_d`: Option D text
- `correct_answer`: Correct option ('a', 'b', 'c', or 'd')
- `created_at`: Creation timestamp

## Routes

### Public Routes
- `/` - Redirect to login or home
- `/login` - Login page (GET/POST)
- `/register` - Register new user (POST)

### Protected Routes (Login Required)
- `/home` - Home/Dashboard with module overview
- `/lesson/<module>/<lesson>` - Display specific lesson
- `/complete-module/<module>` - Mark module as completed (POST)
- `/final-exam` - Final examination (unlocked after completing all modules)
- `/submit-exam` - Submit exam answers (POST)
- `/certificate` - View certificate (available after passing exam)
- `/logout` - Logout user

### Admin Routes (Admin Access Required)
- `/admin/exam-questions` - Manage exam questions
- `/admin/add-question` - Add new question (POST)
- `/admin/update-question/<id>` - Update question (POST)
- `/admin/delete-question/<id>` - Delete question (POST)

## Usage Flow

1. **Login/Register**
   - Users start at the login page
   - Can register a new account or login with existing credentials

2. **Complete Modules**
   - Dashboard shows 3 training modules
   - Click on any module to start from Lesson 1
   - Navigate through lessons using Previous/Next buttons
   - Complete each module by finishing all its lessons

3. **Take Final Exam**
   - Final exam unlocks automatically after completing all 3 modules
   - Answer all questions and submit
   - Must score 70% or higher to pass

4. **Get Certificate**
   - Upon passing the final exam, certificate becomes available
   - View and print your certificate

## Admin Features

Admins can manage exam questions:
1. Login as admin
2. Navigate to `/admin/exam-questions`
3. Add, edit, or delete questions
4. Changes take effect immediately

## Technical Notes

- **Session Management**: Flask session with secure secret key
- **Password Security**: Uses Werkzeug's `generate_password_hash` and `check_password_hash`
- **Database**: SQLite with automatic initialization
- **Progress Tracking**: Server-side tracking (no localStorage for progress)
- **Design Preservation**: All original HTML/CSS designs are preserved
- **Responsive**: Mobile-friendly design

## Security Considerations

⚠️ **Important for Production:**

1. Change the `app.secret_key` in `app.py` to a random, secure value
2. Set `debug=False` in production
3. Use a production-grade database (PostgreSQL, MySQL)
4. Add HTTPS/SSL certificates
5. Implement rate limiting for login attempts
6. Add CSRF protection for forms
7. Regular database backups

## Troubleshooting

**Issue**: Database not found
- **Solution**: Delete `phishguard.db` and restart the app to recreate it

**Issue**: Login not working
- **Solution**: Check that username and password are correct (case-sensitive)

**Issue**: Admin panel not accessible
- **Solution**: Ensure you're logged in as admin (username: `admin`)

**Issue**: Progress not saving
- **Solution**: Check file permissions for `phishguard.db`

## License

Educational use only - PhishGuard.uz Platform

## Support

For issues or questions, please check the application logs or database state.

---

**Developed with Flask + SQLite | All designs preserved | Production-ready**
