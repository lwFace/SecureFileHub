#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码哈希生成工具
用于为文件共享服务生成安全的密码哈希值

使用方法:
1. 直接运行: python generate_password_hash.py
2. 导入使用: from generate_password_hash import hash_password
"""

from werkzeug.security import generate_password_hash
import getpass
import sys

def hash_password(password):
    """
    生成密码哈希值
    
    Args:
        password (str): 明文密码
        
    Returns:
        str: 密码哈希值
    """
    return generate_password_hash(password)

def main():
    """
    主函数 - 交互式密码哈希生成
    """
    print("=" * 50)
    print("🔐 文件共享服务 - 密码哈希生成工具")
    print("=" * 50)
    print()
    
    try:
        while True:
            print("请选择操作:")
            print("1. 生成单个密码哈希")
            print("2. 批量生成密码哈希")
            print("3. 退出")
            print()
            
            choice = input("请输入选择 (1-3): ").strip()
            
            if choice == '1':
                generate_single_hash()
            elif choice == '2':
                generate_batch_hashes()
            elif choice == '3':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            print()
            
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)

def generate_single_hash():
    """
    生成单个密码哈希
    """
    print("\n--- 生成单个密码哈希 ---")
    
    # 获取用户名（可选）
    username = input("用户名 (可选): ").strip()
    
    # 安全地获取密码
    password = getpass.getpass("请输入密码: ")
    
    if not password:
        print("❌ 密码不能为空")
        return
    
    # 生成哈希
    password_hash = hash_password(password)
    
    print("\n✅ 密码哈希生成成功！")
    print("-" * 40)
    
    if username:
        print(f"用户名: {username}")
    
    print(f"密码哈希: {password_hash}")
    print()
    print("📋 复制以下代码到 app.py 的 USERS 字典中:")
    
    if username:
        print(f"    '{username}': '{password_hash}',")
    else:
        print(f"    'username': '{password_hash}',")
    
    print("-" * 40)

def generate_batch_hashes():
    """
    批量生成密码哈希
    """
    print("\n--- 批量生成密码哈希 ---")
    print("格式: 用户名:密码 (每行一个，输入空行结束)")
    print("示例: admin:admin123")
    print()
    
    users = []
    
    while True:
        line = input("输入用户信息 (用户名:密码): ").strip()
        
        if not line:
            break
            
        if ':' not in line:
            print("❌ 格式错误，请使用 用户名:密码 格式")
            continue
            
        username, password = line.split(':', 1)
        username = username.strip()
        password = password.strip()
        
        if not username or not password:
            print("❌ 用户名和密码都不能为空")
            continue
            
        users.append((username, password))
        print(f"✓ 已添加用户: {username}")
    
    if not users:
        print("❌ 没有输入任何用户信息")
        return
    
    print("\n🔄 正在生成密码哈希...")
    print("\n✅ 批量生成完成！")
    print("=" * 50)
    print("📋 复制以下代码到 app.py 的 USERS 字典中:")
    print()
    print("USERS = {")
    
    for username, password in users:
        password_hash = hash_password(password)
        print(f"    '{username}': '{password_hash}',")
    
    print("}")
    print("=" * 50)

if __name__ == '__main__':
    main()