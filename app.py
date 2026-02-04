from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'phishguard-uz-secure-key-2026'  # Change in production

# Database configuration
DATABASE = 'phishguard.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_db():
    """Add Uzbek columns to exam_questions if they don't exist yet.
       Safe to call on every startup — checks before each ALTER.
       Also backfills question_uz with the EN text as a placeholder
       so the exam never shows blank questions while waiting for
       the admin to translate."""
    conn = get_db()
    cursor = conn.cursor()

    # Grab existing column names.  PRAGMA returns zero rows (not an error)
    # when the table doesn't exist yet — that's the fresh-install case.
    # init_db() will create the table with the UZ columns already present,
    # so there is nothing for us to do here.
    cursor.execute("PRAGMA table_info(exam_questions)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if not existing_cols:
        conn.close()
        return

    uz_cols = ['question_uz', 'option_a_uz', 'option_b_uz', 'option_c_uz', 'option_d_uz']
    for col in uz_cols:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE exam_questions ADD COLUMN {col} TEXT")

    # Backfill: copy EN → UZ for any row where question_uz is still NULL
    # so the exam never shows a blank question.
    cursor.execute("""
        UPDATE exam_questions
        SET question_uz  = COALESCE(question_uz,  question),
            option_a_uz  = COALESCE(option_a_uz,  option_a),
            option_b_uz  = COALESCE(option_b_uz,  option_b),
            option_c_uz  = COALESCE(option_c_uz,  option_c),
            option_d_uz  = COALESCE(option_d_uz,  option_d)
        WHERE question_uz IS NULL
    """)

    conn.commit()
    conn.close()

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            current_module INTEGER DEFAULT 1,
            current_lesson INTEGER DEFAULT 1,
            modules_completed TEXT DEFAULT '',
            final_exam_unlocked INTEGER DEFAULT 0,
            final_exam_completed INTEGER DEFAULT 0,
            final_exam_score INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Exam questions table (EN + UZ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            question_uz TEXT,
            option_a_uz TEXT,
            option_b_uz TEXT,
            option_c_uz TEXT,
            option_d_uz TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if admin exists, if not create it
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        admin_password = generate_password_hash('sulaymon123')
        cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
                      ('admin', admin_password))
    
    # Add default exam questions if none exist
    cursor.execute("SELECT COUNT(*) as count FROM exam_questions")
    if cursor.fetchone()['count'] == 0:
        # Each tuple: (EN question, EN a-d, correct, UZ question, UZ a-d)
        default_questions = [
            ("What is phishing?",
             "A type of fish", "A cyber attack using fake emails", "A computer virus", "A hacking tool", "b",
             "Fishing nima?",
             "Baliqlarning bir turi", "Sakhta email orqali kiberhujum", "Kompyuter virusi", "Hakerlik qurolı"),
            ("Which is a red flag in emails?",
             "Company logo", "Urgent requests for personal info", "Professional grammar", "Known sender", "b",
             "Email-larda qizil bayroq nima?",
             "Kompaniya logosu", "Shaxsiy ma'lumot uchun jiddiY so'rov", "Kasbiy grammatika", "Taniqli jo'natuvchi"),
            ("What should you do with suspicious emails?",
             "Click links to verify", "Reply with your info", "Report to IT/security", "Forward to friends", "c",
             "Shubhali email-lar bilan nini qilish kerak?",
             "Tasdiqlash uchun havolaga bosing", "O'z ma'lumotingiz bilan javob bering", "IT/xavfsizlikka xabar bering", "Do'stlarga yuborish"),
            ("What is spear phishing?",
             "Fishing in the ocean", "Targeted phishing attack", "Mass email campaign", "Antivirus software", "b",
             "Spear fishing nima?",
             "Okean baliq ovlashi", "Maqsadli fishing hujumi", "Ommaviy email kampaniya", "Antivirus dasturlari"),
            ("Best way to verify suspicious email?",
             "Click the link", "Call sender using known contact", "Reply to email", "Ignore it", "b",
             "Shubhali email-ni tekshirish uchun eng yaxshi usul?",
             "Havolaga bosing", "Taniqli telefon nomeri bilan jo'natuvchini chaqiring", "Email-ga javob bering", "Uni e'tibor bermay qoldiring"),
            ("What is MFA?",
             "Multiple File Access", "Multi-Factor Authentication", "Main Frame Access", "Manual Form Approval", "b",
             "MFA nima?",
             "Ko'p fayl kirish", "Ko'p omilli autentikatsiya", "Asosiy kadr kirish", "Qo'lbatil forma tasdiqi"),
            ("Common phishing technique?",
             "Strong passwords", "Fake login pages", "Encrypted emails", "Secure connections", "b",
             "Uchratilgan fishing texnikasi?",
             "Kuchli parollar", "Sakhta login sahifalari", "Shifrlangan email-lar", "Xavfsiz ulanishlar"),
            ("What to check in URLs?",
             "Color scheme", "Domain spelling", "Font size", "Image quality", "b",
             "URL-larda nini tekshirish kerak?",
             "Rang sxemi", "Domen imlosi", "Shrift o'lchamı", "Rasm sifati"),
            ("Purpose of phishing awareness?",
             "Increase email traffic", "Reduce security incidents", "Slow down work", "Replace antivirus", "b",
             "Fishing sabahligi maqsadi?",
             "Email harakatini kochirish", "Xavfsizlik hodisalarini kamaytirishh", "Ishni sekinlashtirish", "Antivirusni almashtirish"),
            ("What makes a password strong?",
             "Common words", "Personal info", "Mix of characters, numbers, symbols", "Short and simple", "c",
             "Parolni kuchli qiladigan narsalar?",
             "Oddiy so'zlar", "Shaxsiy ma'lumot", "Harflar, raqamlar, belgilar aralashmasi", "Qisqa va sodda")
        ]
        for row in default_questions:
            (q, a, b, c, d, ans,
             q_uz, a_uz, b_uz, c_uz, d_uz) = row
            cursor.execute("""INSERT INTO exam_questions 
                           (question, option_a, option_b, option_c, option_d, correct_answer,
                            question_uz, option_a_uz, option_b_uz, option_c_uz, option_d_uz) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (q, a, b, c, d, ans, q_uz, a_uz, b_uz, c_uz, d_uz))
    
    conn.commit()
    conn.close()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db()
        user = conn.execute("SELECT is_admin FROM users WHERE id = ?", 
                          (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or not user['is_admin']:
            flash('Admin access required', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_progress(user_id):
    """Get user progress from database"""
    conn = get_db()
    progress = conn.execute("SELECT * FROM progress WHERE user_id = ?", (user_id,)).fetchone()
    
    if not progress:
        # Create default progress
        conn.execute("""INSERT INTO progress 
                       (user_id, current_module, current_lesson, modules_completed) 
                       VALUES (?, 1, 1, '')""", (user_id,))
        conn.commit()
        progress = conn.execute("SELECT * FROM progress WHERE user_id = ?", (user_id,)).fetchone()
    
    conn.close()
    return dict(progress)

def update_progress(user_id, module, lesson):
    """Update user progress"""
    conn = get_db()
    conn.execute("""UPDATE progress 
                   SET current_module = ?, current_lesson = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = ?""", (module, lesson, user_id))
    conn.commit()
    conn.close()

def complete_module(user_id, module):
    """Mark module as completed"""
    conn = get_db()
    progress = conn.execute("SELECT modules_completed FROM progress WHERE user_id = ?", 
                          (user_id,)).fetchone()
    
    completed = progress['modules_completed'].split(',') if progress['modules_completed'] else []
    if str(module) not in completed:
        completed.append(str(module))
    
    completed_str = ','.join(filter(None, completed))
    
    # Check if all 3 modules completed
    unlock_exam = len([m for m in completed if m]) >= 3
    
    conn.execute("""UPDATE progress 
                   SET modules_completed = ?, final_exam_unlocked = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = ?""", (completed_str, 1 if unlock_exam else 0, user_id))
    conn.commit()
    conn.close()

# Module lesson mapping
MODULE_LESSONS = {
    1: 5,  # Module 1 has 5 lessons
    2: 6,  # Module 2 has 6 lessons
    3: 5   # Module 3 has 5 lessons
}

@app.route('/')
def index():
    """Redirect to login or appropriate dashboard based on session"""
    if 'user_id' in session:
        # Admins go to exam manager, users to home dashboard
        if session.get('is_admin'):
            return redirect(url_for('admin_exam_questions'))
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user_row:
            # Convert sqlite3.Row to dict to use .get() method
            user = dict(user_row)
            
            if check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['is_admin'] = user['is_admin']
                session['name'] = user.get('name', '')
                session['surname'] = user.get('surname', '')
                
                # Admins go directly to exam manager, users to home dashboard
                if user['is_admin']:
                    return redirect(url_for('admin_exam_questions'))
                return redirect(url_for('home'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'GET':
        return render_template('register.html')
    
    name = request.form.get('name', '').strip()
    surname = request.form.get('surname', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validation
    if not username or not password:
        flash('Username and password required', 'error')
        return render_template('register.html')
    
    if len(username) < 3:
        flash('Username must be at least 3 characters', 'error')
        return render_template('register.html')
    
    if len(password) < 6:
        flash('Password must be at least 6 characters', 'error')
        return render_template('register.html')
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('register.html')
    
    conn = get_db()
    try:
        password_hash = generate_password_hash(password)
        cursor = conn.execute("INSERT INTO users (name, surname, username, password_hash) VALUES (?, ?, ?, ?)",
                            (name, surname, username, password_hash))
        conn.commit()
        
        # Create default progress
        conn.execute("""INSERT INTO progress 
                       (user_id, current_module, current_lesson, modules_completed) 
                       VALUES (?, 1, 1, '')""", (cursor.lastrowid,))
        conn.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash('Username already exists', 'error')
        return render_template('register.html')
    finally:
        conn.close()
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not old_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('change_password.html', lang=session.get('lang', 'en'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html', lang=session.get('lang', 'en'))
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters', 'error')
            return render_template('change_password.html', lang=session.get('lang', 'en'))
        
        # Verify old password
        conn = get_db()
        user = conn.execute("SELECT password_hash FROM users WHERE id = ?", 
                          (session['user_id'],)).fetchone()
        
        if not user or not check_password_hash(user['password_hash'], old_password):
            conn.close()
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html', lang=session.get('lang', 'en'))
        
        # Update password
        new_hash = generate_password_hash(new_password)
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                    (new_hash, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Password changed successfully', 'success')
        
        # Redirect based on user type
        if session.get('is_admin'):
            return redirect(url_for('admin_exam_questions'))
        return redirect(url_for('home'))
    
    return render_template('change_password.html', lang=session.get('lang', 'en'))

@app.route('/set-lang/<lang>')
@login_required
def set_lang(lang):
    """Persist language choice in the server-side session, then redirect back."""
    if lang in ('en', 'uz'):
        session['lang'] = lang
    # Redirect to the page the user came from, or /home as fallback
    return redirect(request.referrer or url_for('home'))


@app.route('/home')
@login_required
def home():
    """Home/dashboard page"""
    progress = get_user_progress(session['user_id'])
    
    # Parse completed modules
    completed_modules = []
    if progress['modules_completed']:
        completed_modules = [int(m) for m in progress['modules_completed'].split(',') if m]
    
    # Labels for template that can't be done via client-side JS (inside Jinja expressions)
    _labels = {
        'en': {'module': 'Module', 'lesson': 'Lesson'},
        'uz': {'module': 'Modul',  'lesson': 'Dars'}
    }
    current_lang = session.get('lang', 'en')

    return render_template('modules.html', 
                         progress=progress,
                         completed_modules=completed_modules,
                         username=session['username'],
                         name=session.get('name', ''),
                         surname=session.get('surname', ''),
                         lang=current_lang,
                         translations_labels=_labels[current_lang])

@app.route('/lesson/<int:module>/<int:lesson>')
@login_required
def lesson(module, lesson):
    """Display a lesson"""
    if module not in MODULE_LESSONS or lesson < 1 or lesson > MODULE_LESSONS[module]:
        flash('Invalid lesson', 'error')
        return redirect(url_for('home'))
    
    # Update progress
    update_progress(session['user_id'], module, lesson)
    
    # Get progress for navigation
    progress = get_user_progress(session['user_id'])
    is_last_lesson = (lesson == MODULE_LESSONS[module])
    
    return render_template(f'm{module}-lesson{lesson}.html',
                         module=module,
                         lesson=lesson,
                         is_last_lesson=is_last_lesson,
                         total_lessons=MODULE_LESSONS[module],
                         lang=session.get('lang', 'en'))


@app.route('/complete-lesson/<int:module>/<int:lesson>', methods=['POST'])
@login_required
def complete_lesson_route(module, lesson):
    """Mark a lesson as completed"""
    # Update progress to next lesson
    max_lessons = {1: 5, 2: 6, 3: 5}
    
    if module in max_lessons:
        if lesson < max_lessons[module]:
            # Move to next lesson
            next_lesson = lesson + 1
            update_progress(session['user_id'], module, next_lesson)
        else:
            # Last lesson in module, keep at this lesson
            # User will click "Complete Module" button
            update_progress(session['user_id'], module, lesson)
    
    return jsonify({'success': True})

@app.route('/record-quiz-pass/<int:module>', methods=['POST'])
@login_required
def record_quiz_pass(module):
    """Record that the user passed the module quiz (≥70%).
       Called by the client immediately after showScore() confirms pass.
       Sets a session flag that complete_module_route checks before
       writing to the DB, so the module cannot be completed without
       actually passing the quiz."""
    if module not in MODULE_LESSONS:
        return jsonify({'error': 'Invalid module'}), 400
    session[f'quiz_passed_{module}'] = True
    return jsonify({'success': True})

@app.route('/complete-module/<int:module>', methods=['POST'])
@login_required
def complete_module_route(module):
    """Complete a module"""
    if module not in MODULE_LESSONS:
        return jsonify({'error': 'Invalid module'}), 400

    # Server-side guard: every module's last-lesson quiz must be passed
    # before the module can be marked complete.  The flag is set by
    # POST /record-quiz-pass/<module> which the page JS calls only after
    # showScore() confirms ≥70%.
    if not session.get(f'quiz_passed_{module}'):
        return jsonify({
            'success': False,
            'error': 'Quiz not passed',
            'message': 'You must pass the quiz (≥70%) before completing the module.'
        }), 403

    complete_module(session['user_id'], module)

    # Advance current_module → next module, lesson 1.
    # If this was the last module (3), stay on 3 / last lesson so
    # "Continue Learning" disappears once all three are done.
    if module < 3:
        update_progress(session['user_id'], module + 1, 1)
    # else: leave current_module at 3; the Home template hides
    # "Continue Learning" when all 3 modules are in completed_modules.

    return jsonify({
        'success': True,
        'message': f'Module {module} completed!',
        'redirect': url_for('home')
    })

@app.route('/final-exam')
@login_required
def final_exam():
    """Final exam page"""
    progress = get_user_progress(session['user_id'])
    
    if not progress['final_exam_unlocked']:
        flash('Complete all 3 modules to unlock the final exam', 'error')
        return redirect(url_for('home'))
    
    if progress['final_exam_completed']:
        return redirect(url_for('certificate'))
    
    # Get exam questions
    conn = get_db()
    questions = conn.execute("SELECT * FROM exam_questions ORDER BY id").fetchall()
    user = conn.execute("SELECT name, surname FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    user_name = user['name'] if user and user['name'] else ''
    user_surname = user['surname'] if user and user['surname'] else ''
    
    return render_template('final-exam.html', 
                         questions=questions,
                         username=session['username'],
                         name=user_name,
                         surname=user_surname,
                         lang=session.get('lang', 'en'))

@app.route('/submit-exam', methods=['POST'])
@login_required
def submit_exam():
    """Submit final exam"""
    progress = get_user_progress(session['user_id'])
    
    if not progress['final_exam_unlocked']:
        return jsonify({'error': 'Exam not unlocked'}), 403
    
    # Safely parse JSON body
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data received'}), 400
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400

    user_answers = data.get('answers', {})
    
    # Get correct answers from DB
    conn = get_db()
    questions = conn.execute("SELECT id, correct_answer FROM exam_questions").fetchall()
    
    # Calculate score with robust normalization
    correct = 0
    total = len(questions)
    
    for q in questions:
        q_id = str(q['id'])
        if q_id in user_answers:
            # Normalize user answer: strip whitespace, lowercase
            raw = str(user_answers[q_id]).strip().lower()
            # Handle "option_a" / "option_b" / etc. → extract just the letter
            if raw.startswith('option_'):
                raw = raw.replace('option_', '')
            # Now raw should be a single letter: a, b, c, or d
            
            # Normalize correct answer the same way
            correct_raw = str(q['correct_answer']).strip().lower()
            if correct_raw.startswith('option_'):
                correct_raw = correct_raw.replace('option_', '')
            
            if raw == correct_raw:
                correct += 1
    
    score = int((correct / total) * 100) if total > 0 else 0
    passed = score >= 70
    
    # Update progress if passed
    if passed:
        conn.execute("""UPDATE progress 
                       SET final_exam_completed = 1, final_exam_score = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE user_id = ?""", (score, session['user_id']))
        conn.commit()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'score': score,
        'correct': correct,
        'total': total,
        'passed': passed
    })

@app.route('/certificate')
@login_required
def certificate():
    """Certificate page"""
    progress = get_user_progress(session['user_id'])
    
    if not progress['final_exam_completed']:
        flash('Complete the final exam to get your certificate', 'error')
        return redirect(url_for('home'))

    # Pull name + surname from the users table (authoritative source)
    conn = get_db()
    user = conn.execute("SELECT name, surname FROM users WHERE id = ?",
                        (session['user_id'],)).fetchone()
    conn.close()

    name = (user['name'] or '').strip() if user else ''
    surname = (user['surname'] or '').strip() if user else ''
    full_name = f"{name} {surname}".strip() or session.get('username', '')

    return render_template('certificate.html',
                         full_name=full_name,
                         score=progress['final_exam_score'],
                         date=datetime.now().strftime('%B %d, %Y'),
                         lang=session.get('lang', 'en'))

@app.route('/admin/exam-questions')
@admin_required
def admin_exam_questions():
    """Admin page to manage exam questions"""
    conn = get_db()
    questions = [dict(row) for row in conn.execute("SELECT * FROM exam_questions ORDER BY id").fetchall()]
    conn.close()
    
    return render_template('admin_exam.html', questions=questions, lang=session.get('lang', 'en'))

@app.route('/admin/add-question', methods=['POST'])
@admin_required
def add_question():
    """Add exam question (EN + UZ)"""
    data = request.get_json()
    
    conn = get_db()
    conn.execute("""INSERT INTO exam_questions 
                   (question, option_a, option_b, option_c, option_d, correct_answer,
                    question_uz, option_a_uz, option_b_uz, option_c_uz, option_d_uz) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data['question'], data['option_a'], data['option_b'], 
                 data['option_c'], data['option_d'], data['correct_answer'],
                 data.get('question_uz', ''), data.get('option_a_uz', ''),
                 data.get('option_b_uz', ''), data.get('option_c_uz', ''),
                 data.get('option_d_uz', '')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/update-question/<int:question_id>', methods=['POST'])
@admin_required
def update_question(question_id):
    """Update exam question (EN + UZ)"""
    data = request.get_json()
    
    conn = get_db()
    conn.execute("""UPDATE exam_questions 
                   SET question = ?, option_a = ?, option_b = ?, option_c = ?, 
                       option_d = ?, correct_answer = ?,
                       question_uz = ?, option_a_uz = ?, option_b_uz = ?,
                       option_c_uz = ?, option_d_uz = ?
                   WHERE id = ?""",
                (data['question'], data['option_a'], data['option_b'], 
                 data['option_c'], data['option_d'], data['correct_answer'],
                 data.get('question_uz', ''), data.get('option_a_uz', ''),
                 data.get('option_b_uz', ''), data.get('option_c_uz', ''),
                 data.get('option_d_uz', ''), question_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/delete-question/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    """Delete exam question"""
    conn = get_db()
    conn.execute("DELETE FROM exam_questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # migrate_db() adds UZ columns to any pre-existing DB (idempotent).
    # init_db() creates tables + seeds defaults (all IF NOT EXISTS).
    # Both are safe to call every time.
    migrate_db()
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
