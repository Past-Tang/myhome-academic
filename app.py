from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_from_directory
import hashlib
import os
import random
import string
from io import BytesIO
import base64
from functools import wraps
from database import get_db_connection, init_database, create_default_profile
import markdown
import json
from datetime import datetime

# 尝试导入PIL用于生成验证码图片
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# 确保数据库初始化
init_database()
create_default_profile()

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    """密码哈希函数"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    """验证密码"""
    return hash_password(password) == hash_value

def generate_captcha_text():
    """生成验证码文本"""
    # 避免容易混淆的字符
    chars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ123456789'
    return ''.join(random.choice(chars) for _ in range(4))

def generate_captcha_image(text):
    """生成验证码图片"""
    if not PIL_AVAILABLE:
        return None
        
    width, height = 120, 50
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            # 备用字体
            font = ImageFont.load_default()
        except:
            font = None
    
    # 绘制文本
    for i, char in enumerate(text):
        x = 20 + i * 20 + random.randint(-5, 5)
        y = 15 + random.randint(-5, 5)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        draw.text((x, y), char, font=font, fill=color)
    
    # 添加干扰线
    for _ in range(5):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([start, end], fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
    
    # 添加噪点
    for _ in range(50):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    return image

# 验证码相关路由
@app.route('/api/captcha')
def get_captcha():
    """获取验证码"""
    captcha_text = generate_captcha_text()
    session['captcha'] = captcha_text.upper()
    
    if PIL_AVAILABLE:
        # 生成图片验证码
        image = generate_captcha_image(captcha_text)
        if image:
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            return jsonify({
                'type': 'image',
                'data': f'data:image/png;base64,{image_data}',
                'text': None  # 不返回文本，增加安全性
            })
    
    # 如果PIL不可用，返回文本验证码
    return jsonify({
        'type': 'text',
        'data': None,
        'text': captcha_text
    })

# 认证相关路由
@app.route('/api/login', methods=['POST'])
def login():
    """管理员登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    captcha = data.get('captcha', '').upper()
    
    if not username or not password or not captcha:
        return jsonify({'error': 'Username, password and captcha required'}), 400
    
    # 验证验证码
    if 'captcha' not in session or session['captcha'] != captcha:
        # 清除验证码，防止重复使用
        session.pop('captcha', None)
        return jsonify({'error': 'Invalid captcha'}), 400
    
    # 清除已使用的验证码
    session.pop('captcha', None)
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({'message': 'Login successful', 'user': user['username']})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """管理员登出"""
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/check-auth')
def check_auth():
    """检查登录状态"""
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'username': session.get('username')})
    return jsonify({'authenticated': False})

# 个人信息API
@app.route('/api/profile')
def get_profile():
    """获取个人信息"""
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profile WHERE id = 1').fetchone()
    conn.close()
    
    if profile:
        return jsonify(dict(profile))
    return jsonify({'error': 'Profile not found'}), 404

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新个人信息"""
    data = request.get_json()
    conn = get_db_connection()
    
    # 构建更新SQL
    fields = ['name', 'title', 'bio', 'avatar_url', 'email', 'phone', 'address', 
              'website', 'linkedin', 'github', 'orcid', 'research_interests']
    
    update_fields = []
    values = []
    
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if update_fields:
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(1)  # WHERE id = 1
        
        sql = f"UPDATE profile SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(sql, values)
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Profile updated successfully'})

# 教育背景API
@app.route('/api/education')
def get_education():
    """获取教育背景"""
    conn = get_db_connection()
    education = conn.execute('SELECT * FROM education ORDER BY order_index, start_year DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in education])

@app.route('/api/education', methods=['POST'])
@login_required
def create_education():
    """创建教育记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO education (degree, institution, field, start_year, end_year, description, tags, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('degree'), data.get('institution'), data.get('field'),
          data.get('start_year'), data.get('end_year'), data.get('description'),
          data.get('tags', ''), data.get('order_index', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Education record created successfully'})

@app.route('/api/education/<int:education_id>', methods=['PUT'])
@login_required
def update_education(education_id):
    """更新教育记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE education 
        SET degree = ?, institution = ?, field = ?, start_year = ?, 
            end_year = ?, description = ?, tags = ?, order_index = ?
        WHERE id = ?
    ''', (data.get('degree'), data.get('institution'), data.get('field'),
          data.get('start_year'), data.get('end_year'), data.get('description'),
          data.get('tags', ''), data.get('order_index', 0), education_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Education record updated successfully'})

@app.route('/api/education/<int:education_id>', methods=['DELETE'])
@login_required
def delete_education(education_id):
    """删除教育记录"""
    conn = get_db_connection()
    conn.execute('DELETE FROM education WHERE id = ?', (education_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Education record deleted successfully'})

# 论文发表API
@app.route('/api/publications')
def get_publications():
    """获取论文列表"""
    conn = get_db_connection()
    publications = conn.execute('SELECT * FROM publications ORDER BY order_index, year DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in publications])

@app.route('/api/publications', methods=['POST'])
@login_required
def create_publication():
    """创建论文记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO publications (title, authors, journal, year, volume, pages, 
                                doi, url, abstract, keywords, type, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('authors'), data.get('journal'),
          data.get('year'), data.get('volume'), data.get('pages'),
          data.get('doi'), data.get('url'), data.get('abstract'),
          data.get('keywords'), data.get('type', 'journal'), data.get('order_index', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Publication created successfully'})

@app.route('/api/publications/<int:pub_id>', methods=['PUT'])
@login_required
def update_publication(pub_id):
    """更新论文记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE publications 
        SET title = ?, authors = ?, journal = ?, year = ?, volume = ?, 
            pages = ?, doi = ?, url = ?, abstract = ?, keywords = ?, 
            type = ?, order_index = ?
        WHERE id = ?
    ''', (data.get('title'), data.get('authors'), data.get('journal'),
          data.get('year'), data.get('volume'), data.get('pages'),
          data.get('doi'), data.get('url'), data.get('abstract'),
          data.get('keywords'), data.get('type', 'journal'), 
          data.get('order_index', 0), pub_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Publication updated successfully'})

@app.route('/api/publications/<int:pub_id>', methods=['DELETE'])
@login_required
def delete_publication(pub_id):
    """删除论文记录"""
    conn = get_db_connection()
    conn.execute('DELETE FROM publications WHERE id = ?', (pub_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Publication deleted successfully'})

# 项目经历API
@app.route('/api/projects')
def get_projects():
    """获取项目列表"""
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects ORDER BY order_index, start_date DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in projects])

@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """创建项目记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO projects (title, description, detailed_description, role, start_date, end_date, 
                            technologies, url, github_url, status, tags, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('description'), data.get('detailed_description', ''),
          data.get('role'), data.get('start_date'), data.get('end_date'), data.get('technologies'),
          data.get('url'), data.get('github_url'), data.get('status', 'completed'),
          data.get('tags', ''), data.get('order_index', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Project created successfully'})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """更新项目记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE projects 
        SET title = ?, description = ?, detailed_description = ?, role = ?, start_date = ?, end_date = ?,
            technologies = ?, url = ?, github_url = ?, status = ?, tags = ?, order_index = ?
        WHERE id = ?
    ''', (data.get('title'), data.get('description'), data.get('detailed_description', ''), data.get('role'),
          data.get('start_date'), data.get('end_date'), data.get('technologies'),
          data.get('url'), data.get('github_url'), data.get('status', 'completed'),
          data.get('tags', ''), data.get('order_index', 0), project_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Project updated successfully'})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目记录"""
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Project deleted successfully'})

# 工作经历API
@app.route('/api/experience')
def get_experience():
    """获取工作经历"""
    conn = get_db_connection()
    experience = conn.execute('SELECT * FROM experience ORDER BY order_index, start_date DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in experience])

@app.route('/api/experience', methods=['POST'])
@login_required
def create_experience():
    """创建工作经历"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO experience (position, organization, start_date, end_date, 
                              description, location, tags, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('position'), data.get('organization'), data.get('start_date'),
          data.get('end_date'), data.get('description'), data.get('location'),
          data.get('tags', ''), data.get('order_index', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Experience created successfully'})

@app.route('/api/experience/<int:exp_id>', methods=['PUT'])
@login_required
def update_experience(exp_id):
    """更新工作经历"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE experience 
        SET position = ?, organization = ?, start_date = ?, end_date = ?,
            description = ?, location = ?, tags = ?, order_index = ?
        WHERE id = ?
    ''', (data.get('position'), data.get('organization'), data.get('start_date'),
          data.get('end_date'), data.get('description'), data.get('location'),
          data.get('tags', ''), data.get('order_index', 0), exp_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Experience updated successfully'})

@app.route('/api/experience/<int:exp_id>', methods=['DELETE'])
@login_required
def delete_experience(exp_id):
    """删除工作经历"""
    conn = get_db_connection()
    conn.execute('DELETE FROM experience WHERE id = ?', (exp_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Experience deleted successfully'})

# 荣誉奖项API
@app.route('/api/awards')
def get_awards():
    """获取荣誉奖项"""
    conn = get_db_connection()
    awards = conn.execute('SELECT * FROM awards ORDER BY order_index, year DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in awards])

@app.route('/api/awards', methods=['POST'])
@login_required
def create_award():
    """创建奖项记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO awards (title, organization, year, description, tags, order_index)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('organization'), data.get('year'),
          data.get('description'), data.get('tags', ''), data.get('order_index', 0)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Award created successfully'})

@app.route('/api/awards/<int:award_id>', methods=['PUT'])
@login_required
def update_award(award_id):
    """更新奖项记录"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE awards 
        SET title = ?, organization = ?, year = ?, description = ?, tags = ?, order_index = ?
        WHERE id = ?
    ''', (data.get('title'), data.get('organization'), data.get('year'),
          data.get('description'), data.get('tags', ''), data.get('order_index', 0), award_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Award updated successfully'})

@app.route('/api/awards/<int:award_id>', methods=['DELETE'])
@login_required
def delete_award(award_id):
    """删除奖项记录"""
    conn = get_db_connection()
    conn.execute('DELETE FROM awards WHERE id = ?', (award_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Award deleted successfully'})

# 友情链接API
@app.route('/api/friends')
def get_friends():
    """获取友情链接"""
    conn = get_db_connection()
    friends = conn.execute('SELECT * FROM friends WHERE is_active = 1 ORDER BY order_index, created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in friends])

@app.route('/api/friends', methods=['POST'])
@login_required
def create_friend():
    """创建友情链接"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        INSERT INTO friends (name, url, description, avatar, order_index, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('url'), data.get('description'),
          data.get('avatar'), data.get('order_index', 0), data.get('is_active', 1)))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Friend link created successfully'})

@app.route('/api/friends/<int:friend_id>', methods=['PUT'])
@login_required
def update_friend(friend_id):
    """更新友情链接"""
    data = request.get_json()
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE friends 
        SET name = ?, url = ?, description = ?, avatar = ?, order_index = ?, is_active = ?
        WHERE id = ?
    ''', (data.get('name'), data.get('url'), data.get('description'),
          data.get('avatar'), data.get('order_index', 0), data.get('is_active', 1), friend_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Friend link updated successfully'})

@app.route('/api/friends/<int:friend_id>', methods=['DELETE'])
@login_required
def delete_friend(friend_id):
    """删除友情链接"""
    conn = get_db_connection()
    conn.execute('DELETE FROM friends WHERE id = ?', (friend_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Friend link deleted successfully'})

# 系统设置API
@app.route('/api/settings')
def get_settings():
    """获取系统设置"""
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM settings WHERE id = 1').fetchone()
    conn.close()
    
    if settings:
        return jsonify(dict(settings))
    return jsonify({'beian': '', 'site_title': '个人学术主页', 'site_description': ''})

@app.route('/api/settings', methods=['PUT'])
@login_required
def update_settings():
    """更新系统设置"""
    data = request.get_json()
    conn = get_db_connection()
    
    # 检查设置是否存在
    existing = conn.execute('SELECT id FROM settings WHERE id = 1').fetchone()
    
    if existing:
        # 更新现有设置
        conn.execute('''
            UPDATE settings 
            SET beian = ?, site_title = ?, site_description = ?, keywords = ?, 
                analytics_code = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (data.get('beian'), data.get('site_title'), data.get('site_description'),
              data.get('keywords'), data.get('analytics_code')))
    else:
        # 创建新设置
        conn.execute('''
            INSERT INTO settings (id, beian, site_title, site_description, keywords, analytics_code)
            VALUES (1, ?, ?, ?, ?, ?)
        ''', (data.get('beian'), data.get('site_title'), data.get('site_description'),
              data.get('keywords'), data.get('analytics_code')))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Settings updated successfully'})

# 前端页面路由
@app.route('/')
def index():
    """学术主页首页"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """管理后台页面"""
    return render_template('admin.html')

# 文件上传处理（头像等）
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join('static', 'uploads', filename)
        
        # 确保上传目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        return jsonify({'message': 'File uploaded successfully', 'url': f'/static/uploads/{filename}'})
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 