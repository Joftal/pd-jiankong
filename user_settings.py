#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户设置管理模块
负责管理用户设置，包括窗口大小等配置的持久化存储
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class UserSettings:
    def __init__(self, settings_file: str = "usersetting.json"):
        """初始化用户设置管理器"""
        # 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境路径
            app_dir = os.path.dirname(__file__)
        
        self.settings_file = os.path.join(app_dir, settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """加载用户设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"加载用户设置失败: {e}")
                return self._get_default_settings()
        else:
            return self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "window_width": 1400,
            "window_height": 900,
            "maximized": False,  # 是否最大化
            "theme": "dark",
            "last_updated": None
        }
    
    def save_settings(self) -> bool:
        """保存设置到文件"""
        try:
            import datetime
            self.settings["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存用户设置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取设置项"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            self.settings[key] = value
            return self.save_settings()
        except Exception as e:
            print(f"设置配置项失败: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新设置"""
        try:
            self.settings.update(updates)
            return self.save_settings()
        except Exception as e:
            print(f"批量更新设置失败: {e}")
            return False
    
    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        width = self.get("window_width", 1400)
        height = self.get("window_height", 900)
        return (width, height)
    
    def set_window_size(self, width: int, height: int) -> bool:
        """设置窗口大小"""
        return self.update({
            "window_width": width,
            "window_height": height
        })
    
    def is_maximized(self) -> bool:
        """检查是否最大化"""
        return self.get("maximized", False)
    
    def set_maximized(self, maximized: bool) -> bool:
        """设置最大化状态"""
        return self.set("maximized", maximized)
    
    def reset_to_default(self) -> bool:
        """重置为默认设置"""
        try:
            self.settings = self._get_default_settings()
            return self.save_settings()
        except Exception as e:
            print(f"重置设置失败: {e}")
            return False
    
    def export_settings(self, export_path: str) -> bool:
        """导出设置到指定路径"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """从指定路径导入设置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 合并设置，保留默认值
            default_settings = self._get_default_settings()
            default_settings.update(imported_settings)
            self.settings = default_settings
            
            return self.save_settings()
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False
