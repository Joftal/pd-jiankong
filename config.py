import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        """初始化配置管理器"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "cookie": "",
            "check_interval": 2,
            "main_interval": 60,
            "notification_enabled": True,
            "auto_start": False,
            "window_width": 1200,
            "window_height": 800,
            "theme": "dark",
            "max_log_lines": 100,
            "database_path": "pd_signal.db"
        }
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            self.config[key] = value
            return self.save_config()
        except Exception as e:
            print(f"设置配置项失败: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置"""
        try:
            self.config.update(updates)
            return self.save_config()
        except Exception as e:
            print(f"批量更新配置失败: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定路径"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定路径导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 合并配置，保留默认值
            default_config = self._get_default_config()
            default_config.update(imported_config)
            self.config = default_config
            
            return self.save_config()
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
