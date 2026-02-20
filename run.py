#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人学术主页系统启动脚本
"""

import os
import sys
from database import init_database, create_default_profile, create_default_data, create_admin_user
from app import app

def setup_database():
    """设置数据库"""
    print("正在初始化数据库...")
    init_database()
    create_default_profile()
    create_default_data()
    print("数据库初始化完成！")

def create_default_admin():
    """创建默认管理员账户"""
    print("\n=== 创建管理员账户 ===")
    
    # 检查是否已存在管理员
    from database import get_db_connection
    conn = get_db_connection()
    existing_user = conn.execute('SELECT username FROM users LIMIT 1').fetchone()
    conn.close()
    
    if existing_user:
        print(f"管理员账户已存在: {existing_user['username']}")
        return
    
    # 创建新的管理员账户
    while True:
        username = input("请输入管理员用户名 (默认: admin): ").strip() or "admin"
        password = input("请输入管理员密码: ").strip()
        
        if not password:
            print("密码不能为空！")
            continue
        
        if len(password) < 6:
            print("密码长度至少6位！")
            continue
            
        email = input("请输入管理员邮箱 (可选): ").strip() or None
        
        if create_admin_user(username, password, email):
            print(f"管理员账户 '{username}' 创建成功！")
            break
        else:
            print("创建失败，请重试。")

def main():
    """主函数"""
    print("=== 个人学术主页系统 ===")
    print("正在启动系统...")
    
    # 确保必要的目录存在
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # 初始化数据库
    setup_database()
    
    # 检查是否需要创建管理员账户
    create_default_admin()
    
    print("\n=== 系统启动 ===")
    print("访问地址:")
    print("- 学术主页: http://localhost:5000/")
    print("- 管理后台: http://localhost:5000/admin")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动Flask应用
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)

if __name__ == '__main__':
    main() 