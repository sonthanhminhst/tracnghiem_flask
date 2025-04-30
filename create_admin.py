import sqlite3
from werkzeug.security import generate_password_hash

# Kết nối tới database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Thông tin admin
admin_name = 'Admin'
admin_email = 'admin@example.com'
admin_password = 'admin123'  # Mật khẩu bạn muốn đặt
hashed_password = generate_password_hash(admin_password)
admin_avatar = 'default.png'  # Avatar mặc định

# Thêm admin vào bảng users
try:
    c.execute("""
        INSERT INTO users (name, email, password, role, avatar)
        VALUES (?, ?, ?, ?, ?)
    """, (admin_name, admin_email, hashed_password, 'admin', admin_avatar))
    
    conn.commit()
    print("✅ Đã tạo tài khoản admin thành công kèm avatar!")
except sqlite3.IntegrityError:
    print("⚠️ Tài khoản admin đã tồn tại!")

conn.close()
