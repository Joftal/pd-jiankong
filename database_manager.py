import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "pd_signal.db"):
        """初始化数据库管理器"""
        # 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境路径
            app_dir = os.path.dirname(__file__)
        
        # 确保数据库文件在可执行文件所在目录
        if not os.path.isabs(db_path):
            self.db_path = os.path.join(app_dir, db_path)
        else:
            self.db_path = db_path
            
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建vtbs表（主播信息表）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vtbs (
                mid TEXT NOT NULL,
                username TEXT NOT NULL,
                usernick TEXT,
                liveStatus TEXT DEFAULT NULL,
                title TEXT,
                platform TEXT DEFAULT 'panda',
                hls TEXT,
                remark TEXT DEFAULT '',
                PRIMARY KEY (mid, username)
            )
        ''')
        
        # 创建watch表（监控表）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mid TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建config表（配置表）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查并添加remark字段（数据库迁移）
        try:
            cursor.execute("ALTER TABLE vtbs ADD COLUMN remark TEXT DEFAULT ''")
            conn.commit()
        except sqlite3.OperationalError:
            # 字段已存在，忽略错误
            pass
        
        conn.commit()
        conn.close()
    
    def add_vtb_to_watch(self, mid: str, username: str, usernick: str = "", 
                        live_status: str = "", title: str = "", platform: str = "panda", hls: str = "", remark: str = "") -> bool:
        """添加主播到监控列表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查主播是否已存在
            cursor.execute('SELECT * FROM vtbs WHERE mid = ?', (mid,))
            if not cursor.fetchone():
                # 添加主播信息
                cursor.execute('''
                    INSERT INTO vtbs (mid, username, usernick, liveStatus, title, platform, hls, remark)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (mid, username, usernick, live_status, title, platform, hls, remark))
            
            # 检查是否已在监控列表中
            cursor.execute('SELECT * FROM watch WHERE mid = ?', (mid,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO watch (mid) VALUES (?)', (mid,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加主播失败: {e}")
            return False
    
    def get_vtb_by_mid(self, mid: str) -> Optional[Dict]:
        """根据mid获取主播信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM vtbs WHERE mid = ?', (mid,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'mid': row[0],
                    'username': row[1],
                    'usernick': row[2],
                    'liveStatus': row[3],
                    'title': row[4],
                    'platform': row[5],
                    'hls': row[6],
                    'remark': row[7] if len(row) > 7 else ''
                }
            return None
        except Exception as e:
            print(f"获取主播信息失败: {e}")
            return None
    
    def get_all_watched_vtbs(self) -> List[Dict]:
        """获取所有监控的主播"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.* FROM vtbs v 
                INNER JOIN watch w ON v.mid = w.mid
                ORDER BY v.username
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'mid': row[0],
                'username': row[1],
                'usernick': row[2],
                'liveStatus': row[3],
                'title': row[4],
                'platform': row[5],
                'hls': row[6],
                'remark': row[7] if len(row) > 7 else ''
            } for row in rows]
        except Exception as e:
            print(f"获取监控列表失败: {e}")
            return []
    
    def update_vtb_remark(self, mid: str, remark: str) -> bool:
        """更新主播备注"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE vtbs SET remark = ? WHERE mid = ?', (remark, mid))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新主播备注失败: {e}")
            return False
    
    def update_vtb_column(self, column: str, value: str, mid: str) -> bool:
        """更新主播的某个字段"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE vtbs SET {column} = ? WHERE mid = ?', (value, mid))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新主播信息失败: {e}")
            return False
    
    def remove_from_watch(self, mid: str) -> bool:
        """从监控列表中移除主播"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM watch WHERE mid = ?', (mid,))
            
            # 如果没有其他监控该主播，则删除主播信息
            cursor.execute('SELECT * FROM watch WHERE mid = ?', (mid,))
            if not cursor.fetchone():
                cursor.execute('DELETE FROM vtbs WHERE mid = ?', (mid,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"移除监控失败: {e}")
            return False
    
    def set_config(self, key: str, value: str) -> bool:
        """设置配置项"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
    
    def get_config(self, key: str, default: str = "") -> str:
        """获取配置项"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else default
        except Exception as e:
            print(f"获取配置失败: {e}")
            return default
    
    def get_all_configs(self) -> Dict[str, str]:
        """获取所有配置"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM config')
            rows = cursor.fetchall()
            conn.close()
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"获取所有配置失败: {e}")
            return {}
