import platform
import os
import logging
import traceback
from plyer import notification
from datetime import datetime
from typing import Optional

# 尝试导入win10toast以获得更好的Windows通知支持
try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    WIN10TOAST_AVAILABLE = False

class NotificationManager:
    def __init__(self, app_name: str = "PD Signal"):
        """初始化通知管理器"""
        self.app_name = app_name
        self.is_windows = platform.system() == "Windows"
        
        # 配置logger
        self.logger = logging.getLogger(__name__)
        
        # 图标路径
        self.icon_path = self._get_icon_path()
        
        # 通知设置
        self.online_notification_enabled = True
        self.offline_notification_enabled = True
        
        # 初始化win10toast（如果可用）
        if self.is_windows and WIN10TOAST_AVAILABLE:
            try:
                self.toaster = ToastNotifier()
                self.logger.info("已启用win10toast通知支持")
            except Exception as e:
                self.logger.error(f"win10toast初始化失败: {e}")
                self.toaster = None
        else:
            self.toaster = None
    
    def _get_icon_path(self) -> Optional[str]:
        """获取图标文件路径"""
        # 尝试多个可能的图标路径
        possible_paths = [
            "pandatv.ico",
            os.path.join(os.getcwd(), "pandatv.ico"),
            os.path.join(os.path.dirname(__file__), "pandatv.ico"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "pandatv.ico")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"找到图标文件: {path}")
                return path
        
        self.logger.warning("未找到 pandatv.ico 图标文件")
        return None
        
    def send_notification(self, title: str, message: str, timeout: int = 10, icon_path: Optional[str] = None) -> bool:
        """发送系统通知"""
        try:
            # 使用传入的图标路径或默认图标路径
            icon_to_use = icon_path or self.icon_path
            
            if self.is_windows and self.toaster:
                # 使用win10toast发送通知
                result = self.toaster.show_toast(
                    title=title,
                    msg=message,
                    duration=timeout,
                    threaded=False,  # 改为False以便同步等待
                    icon_path=icon_to_use  # 添加图标支持
                )
                return result
            elif self.is_windows:
                # 使用plyer发送通知
                notification.notify(
                    title=title,
                    message=message,
                    app_name=self.app_name,
                    timeout=timeout,
                    app_icon=icon_to_use  # 使用图标路径
                )
                return True
            else:
                # 非Windows系统的通知处理
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout,
                    app_icon=icon_to_use  # 非Windows系统也尝试使用图标
                )
                return True
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_streamer_online(self, username: str, usernick: str, title: str, start_time: str = "") -> bool:
        """通知主播开播"""
        try:
            # 检查是否启用在线主播通知
            if not self.online_notification_enabled:
                self.logger.debug(f"在线主播通知已禁用，跳过 {username} 的开播通知")
                return False
            
            # 清理标题中的特殊字符
            clean_title = title.replace('[].-_()', '') if title else "直播中"
            
            # 格式化时间
            time_info = ""
            if start_time:
                try:
                    # 假设时间格式需要转换
                    time_info = f"\n开播时间: {start_time}"
                except:
                    time_info = ""
            
            notification_title = f"🟢 [ONLINE] {username} 开播了！"
            notification_message = f"{usernick}\n{clean_title}{time_info}"
            
            return self.send_notification(notification_title, notification_message)
        except Exception as e:
            self.logger.error(f"发送开播通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_streamer_offline(self, username: str, usernick: str) -> bool:
        """通知主播下播"""
        try:
            # 检查是否启用离线主播通知
            if not self.offline_notification_enabled:
                self.logger.debug(f"离线主播通知已禁用，跳过 {username} 的下播通知")
                return False
            
            notification_title = f"🔴 [OFFLINE] {username} 下播了"
            notification_message = f"{usernick}\n直播已结束"
            
            return self.send_notification(notification_title, notification_message)
        except Exception as e:
            self.logger.error(f"发送下播通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_status_change(self, username: str, usernick: str, old_title: str, new_title: str) -> bool:
        """通知状态变化"""
        try:
            notification_title = f"📝 [EDIT] {username} 状态更新"
            notification_message = f"{usernick}\n{new_title}"
            
            return self.send_notification(notification_title, notification_message, timeout=5)
        except Exception as e:
            self.logger.error(f"发送状态变化通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_error(self, error_message: str) -> bool:
        """发送错误通知"""
        try:
            return self.send_notification("❌ [ERROR] PD Signal 错误", error_message, timeout=15)
        except Exception as e:
            self.logger.error(f"发送错误通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_info(self, info_message: str) -> bool:
        """发送信息通知"""
        try:
            return self.send_notification("ℹ️ PD Signal 信息", info_message, timeout=5)
        except Exception as e:
            self.logger.error(f"发送信息通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_success(self, success_message: str) -> bool:
        """发送成功通知"""
        try:
            return self.send_notification("✅ PD Signal 成功", success_message, timeout=5)
        except Exception as e:
            self.logger.error(f"发送成功通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def notify_warning(self, warning_message: str) -> bool:
        """发送警告通知"""
        try:
            return self.send_notification("⚠️ PD Signal 警告", warning_message, timeout=8)
        except Exception as e:
            self.logger.error(f"发送警告通知失败: {e}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def set_notification_settings(self, online_enabled: bool, offline_enabled: bool):
        """设置通知开关"""
        self.online_notification_enabled = online_enabled
        self.offline_notification_enabled = offline_enabled
        self.logger.info(f"通知设置已更新: 在线通知={'启用' if online_enabled else '禁用'}, 离线通知={'启用' if offline_enabled else '禁用'}")
    
    def is_online_notification_enabled(self) -> bool:
        """检查是否启用在线主播通知"""
        return self.online_notification_enabled
    
    def is_offline_notification_enabled(self) -> bool:
        """检查是否启用离线主播通知"""
        return self.offline_notification_enabled
