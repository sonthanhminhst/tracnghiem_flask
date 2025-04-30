from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import csv
import os
import random

app = Flask(__name__)
app.secret_key = 'secret_key_123'

DB_NAME = 'database.db'
QUESTIONS_FILE = 'questions.csv'

# Khởi tạo database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                avatar TEXT DEFAULT 'default.png'
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER,
                total INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

# Trang chủ
@app.route('/')
def home():
    return render_template('home.html')

# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                flash("Đăng ký thành công. Mời đăng nhập.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Email đã tồn tại.", "danger")

    return render_template('register.html')

# Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            # Thêm avatar vào SELECT
            c.execute("SELECT id, name, password, role, avatar FROM users WHERE email = ?", (email,))
            user = c.fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['role'] = user[3]
            session['avatar'] = user[4]  # 🔥 Thêm dòng này
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('home'))
        else:
            flash("Sai thông tin đăng nhập", "danger")

    return render_template('login.html')


# Đăng xuất
@app.route('/logout')
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for('home'))

# Load câu hỏi từ CSV
def load_questions(selected_class, selected_topic):
    questions = []

    with open(QUESTIONS_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['class'] == selected_class and row['topic'] == selected_topic:
                questions.append({
                    'question': row['question'],
                    'option_a': row['option_a'],
                    'option_b': row['option_b'],
                    'option_c': row['option_c'],
                    'option_d': row['option_d'],
                    'correct_option': row['correct_option']
                })

    return random.sample(questions, min(10, len(questions)))

# Làm bài trắc nghiệm
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    all_topics = {
        'Tin học 6': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Mạng máy tính và Internet',
            'Chủ đề 3: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 4: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 5: Ứng dụng tin học',
            'Chủ đề 6: Giải quyết vấn đề với sự trợ giúp của máy tính'
        ],
        'Tin học 7': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính'
        ],
        'Tin học 8': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính',
            'Chủ đề 6: Hướng nghiệp với Tin học'
        ],
        'Tin học 9': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính',
            'Chủ đề 6: Hướng nghiệp với Tin học'
        ]
    }

    if request.method == 'POST':
        selected_class = request.form.get('selected_class')
        selected_topic = request.form.get('selected_topic')

        if selected_class and not selected_topic:
            topics = all_topics.get(selected_class, [])
            return render_template('quiz.html', selected_class=selected_class, topics=topics)

        if selected_class and selected_topic and 'question_0' not in request.form:
            questions = load_questions(selected_class, selected_topic)
            session['questions'] = questions
            return render_template('quiz.html', selected_class=selected_class, selected_topic=selected_topic, questions=questions)

        # Nộp bài
        questions = session.get('questions', [])
        score = sum(1 for idx, q in enumerate(questions) if request.form.get(f'question_{idx}') == q['correct_option'])
        total = len(questions)

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO results (user_id, score, total) VALUES (?, ?, ?)", (session['user_id'], score, total))
            conn.commit()

        session['latest_result'] = (score, total)
        return redirect(url_for('result'))

    return render_template('quiz.html')

# Kết quả
@app.route('/result')
def result():
    if 'latest_result' not in session:
        return redirect(url_for('quiz'))

    score, total = session['latest_result']
    return render_template('result.html', score=score, total=total)

# Lịch sử
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT score, total FROM results WHERE user_id = ?", (session['user_id'],))
        results = c.fetchall()

    return render_template('history.html', results=results)

# Admin quản lý câu hỏi
@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('home'))

    questions = []
    with open(QUESTIONS_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader):
            questions.append({
                'id': idx,
                'class': row['class'],
                'topic': row['topic'],
                'question': row['question'],
                'option_a': row['option_a'],
                'option_b': row['option_b'],
                'option_c': row['option_c'],
                'option_d': row['option_d'],
                'correct_option': row['correct_option']
            })

    return render_template('admin.html', questions=questions)

# Thêm câu hỏi
@app.route('/add_question', methods=['POST'])
def add_question():
    if 'role' not in session or session['role'] != 'admin':
        flash('Bạn không có quyền.', 'danger')
        return redirect(url_for('home'))

    new_question = {
        'class': request.form['selected_class'],
        'topic': request.form['topic'],
        'question': request.form['question'],
        'option_a': request.form['option_a'],
        'option_b': request.form['option_b'],
        'option_c': request.form['option_c'],
        'option_d': request.form['option_d'],
        'correct_option': request.form['correct_option']
    }

    # Đọc dữ liệu cũ
    rows = []
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

    rows.append(new_question)

    # Ghi lại vào file
    with open(QUESTIONS_FILE, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['class', 'topic', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    flash('Đã thêm câu hỏi mới!', 'success')
    return redirect(url_for('admin'))

# Xóa câu hỏi
@app.route('/delete_question/<int:question_id>')
def delete_question(question_id):
    if 'role' not in session or session['role'] != 'admin':
        flash('Bạn không có quyền.', 'danger')
        return redirect(url_for('home'))

    with open(QUESTIONS_FILE, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if 0 <= question_id < len(rows):
        rows.pop(question_id)

        with open(QUESTIONS_FILE, mode='w', encoding='utf-8', newline='') as file:
            fieldnames = ['class', 'topic', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        flash('Đã xóa câu hỏi.', 'success')
    else:
        flash('Không tìm thấy câu hỏi.', 'danger')

    return redirect(url_for('admin'))



UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tạo thư mục upload nếu chưa có
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Lấy thông tin người dùng từ database
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT name, email, avatar, password FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()

    if not user:
        flash('Không tìm thấy người dùng.', 'danger')
        return redirect(url_for('home'))

    user_data = {
        'name': user[0],
        'email': user[1],
        'avatar': user[2],
        'password_hash': user[3]
    }

    if request.method == 'POST':
        # --- Xử lý upload avatar ---
        avatar_file = request.files.get('avatar')
        if avatar_file and allowed_file(avatar_file.filename):
            filename = secure_filename(f"user_{user_id}_" + avatar_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar_file.save(filepath)

            with sqlite3.connect(DB_NAME) as conn:
                c = conn.cursor()
                c.execute('UPDATE users SET avatar = ? WHERE id = ?', (filename, user_id))
                conn.commit()

            flash('Cập nhật ảnh đại diện thành công.', 'success')

        # --- Xử lý đổi mật khẩu nếu có nhập ---
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password or new_password or confirm_password:
            # Chỉ kiểm tra khi nhập ít nhất 1 trong 3 trường
            if not (current_password and new_password and confirm_password):
                flash('Vui lòng điền đầy đủ các ô mật khẩu để đổi mật khẩu.', 'warning')
            else:
                if check_password_hash(user_data['password_hash'], current_password):
                    if new_password == confirm_password:
                        new_password_hash = generate_password_hash(new_password)
                        with sqlite3.connect(DB_NAME) as conn:
                            c = conn.cursor()
                            c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password_hash, user_id))
                            conn.commit()
                        flash('Đổi mật khẩu thành công.', 'success')
                    else:
                        flash('Mật khẩu mới và xác nhận không khớp.', 'danger')
                else:
                    flash('Mật khẩu hiện tại không đúng.', 'danger')

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user_data)

@app.route('/mock_test', methods=['GET', 'POST'])
def mock_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    all_topics = {
        'Tin học 6': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Mạng máy tính và Internet',
            'Chủ đề 3: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 4: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 5: Ứng dụng tin học',
            'Chủ đề 6: Giải quyết vấn đề với sự trợ giúp của máy tính'
        ],
        'Tin học 7': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính'
        ],
        'Tin học 8': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính',
            'Chủ đề 6: Hướng nghiệp với Tin học'
        ],
        'Tin học 9': [
            'Chủ đề 1: Máy tính và cộng đồng',
            'Chủ đề 2: Tổ chức lưu trữ tìm kiếm và trao đổi thông tin',
            'Chủ đề 3: Đạo đức pháp luật văn hóa trong môi trường số',
            'Chủ đề 4: Ứng dụng tin học',
            'Chủ đề 5: Giải quyết vấn đề với sự trợ giúp của máy tính',
            'Chủ đề 6: Hướng nghiệp với Tin học'
        ]
    }

    if request.method == 'POST':
        selected_class = request.form.get('selected_class')
        selected_topic = request.form.get('selected_topic')

        # Bước 1: Chọn khối
        if selected_class and not selected_topic:
            topics = all_topics.get(selected_class, [])
            return render_template('mock_test.html', selected_class=selected_class, topics=topics)

        # Bước 2: Chọn chủ đề → load câu hỏi
        if selected_class and selected_topic and 'question_0' not in request.form:
            questions = load_questions(selected_class, selected_topic)
            session['mock_questions'] = questions
            return render_template('mock_test.html', selected_class=selected_class, selected_topic=selected_topic, questions=questions)

        # Bước 3: Nộp bài (chấm điểm nhưng KHÔNG lưu vào lịch sử)
        questions = session.get('mock_questions', [])
        score = sum(1 for idx, q in enumerate(questions) if request.form.get(f'question_{idx}') == q['correct_option'])
        total = len(questions)

        return render_template('result_mock.html', score=score, total=total)

    return render_template('mock_test.html')


# Khởi tạo database nếu chưa có
if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
