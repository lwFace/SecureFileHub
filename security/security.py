# -*- coding: utf-8 -*-
"""
安全核心模块
处理登录限制、IP封禁等安全功能
"""

import time
import logging
from datetime import datetime
from config import MAX_LOGIN_ATTEMPTS, BAN_DURATION, ATTEMPT_WINDOW

# 登录失败跟踪
login_attempts = {}  # {ip: [timestamp1, timestamp2, ...]}
banned_ips = {}  # {ip: ban_timestamp}


def is_ip_banned(ip):
    """检查IP是否被封禁"""
    if ip in banned_ips:
        ban_time = banned_ips[ip]
        if time.time() - ban_time < BAN_DURATION:
            return True
        else:
            # 封禁时间已过，移除封禁
            del banned_ips[ip]
            logging.info(f"IP {ip} 封禁已自动解除")
    return False


def record_login_attempt(ip, success=False):
    """记录登录尝试"""
    current_time = time.time()
    
    if success:
        # 登录成功，清除该IP的失败记录
        if ip in login_attempts:
            del login_attempts[ip]
        logging.info(f"IP {ip} 登录成功")
        return
    
    # 登录失败，记录时间戳
    if ip not in login_attempts:
        login_attempts[ip] = []
    
    login_attempts[ip].append(current_time)
    
    # 清理超出时间窗口的记录
    login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < ATTEMPT_WINDOW]
    
    attempt_count = len(login_attempts[ip])
    logging.warning(f"IP {ip} 登录失败，当前失败次数: {attempt_count}")
    
    # 检查是否需要封禁
    if attempt_count >= MAX_LOGIN_ATTEMPTS:
        banned_ips[ip] = current_time
        logging.error(f"IP {ip} 因登录失败次数过多被封禁 {BAN_DURATION} 秒")
        return True  # 返回True表示已被封禁
    
    return False


def get_remaining_attempts(ip):
    """获取剩余登录尝试次数"""
    if ip not in login_attempts:
        return MAX_LOGIN_ATTEMPTS
    
    current_time = time.time()
    # 清理过期记录
    login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < ATTEMPT_WINDOW]
    
    return max(0, MAX_LOGIN_ATTEMPTS - len(login_attempts[ip]))


def get_ban_remaining_time(ip):
    """获取封禁剩余时间（秒）"""
    if ip in banned_ips:
        elapsed = time.time() - banned_ips[ip]
        remaining = BAN_DURATION - elapsed
        return max(0, int(remaining))
    return 0


def get_banned_ips_info():
    """获取封禁IP信息"""
    current_time = time.time()
    banned_info = []
    
    for ip, ban_time in banned_ips.items():
        remaining = int(BAN_DURATION - (current_time - ban_time))
        if remaining > 0:
            banned_info.append({
                'ip': ip,
                'ban_time': datetime.fromtimestamp(ban_time).strftime('%Y-%m-%d %H:%M:%S'),
                'remaining': remaining
            })
    
    return banned_info


def get_login_attempts_info():
    """获取登录失败信息"""
    current_time = time.time()
    attempt_info = []
    
    for ip, attempts in login_attempts.items():
        # 清理过期记录
        valid_attempts = [t for t in attempts if current_time - t < ATTEMPT_WINDOW]
        if valid_attempts:
            attempt_info.append({
                'ip': ip,
                'count': len(valid_attempts),
                'last_attempt': datetime.fromtimestamp(max(valid_attempts)).strftime('%Y-%m-%d %H:%M:%S'),
                'remaining': max(0, MAX_LOGIN_ATTEMPTS - len(valid_attempts))
            })
    
    return attempt_info


def unban_ip_address(ip, admin_user):
    """手动解封IP"""
    if ip in banned_ips:
        del banned_ips[ip]
        logging.info(f"管理员 {admin_user} 手动解封IP: {ip}")
        return True
    return False


def clear_ip_attempts(ip, admin_user):
    """清除IP的失败记录"""
    if ip in login_attempts:
        del login_attempts[ip]
        logging.info(f"管理员 {admin_user} 清除IP失败记录: {ip}")
        return True
    return False