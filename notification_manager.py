import platform
from plyer import notification
from datetime import datetime
from typing import Optional

class NotificationManager:
    def __init__(self, app_name: str = "PD Signal"):
        """初始化通知管理器"""
        self.app_name = app_name
        self.is_windows = platform.system() == "Windows"
        
    def send_notification(self, title: str, message: str, timeout: int = 10) -> bool:
        """发送系统通知"""
        try:
            if self.is_windows:
                notification.notify(
                    title=title,
                    message=message,
                    app_name=self.app_name,
                    timeout=timeout,
                    app_icon=None  # 可以添加图标路径
                )
                return True
            else:
                # 非Windows系统的通知处理
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout
                )
                return True
        except Exception as e:
            print(f"发送通知失败: {e}")
            return False
    
    def notify_streamer_online(self, username: str, usernick: str, title: str, start_time: str = "") -> bool:
        """通知主播开播"""
        try:
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
            
            notification_title = f"🟢 {username} 开播了！"
            notification_message = f"{usernick}\n{clean_title}{time_info}"
            
            return self.send_notification(notification_title, notification_message)
        except Exception as e:
            print(f"发送开播通知失败: {e}")
            return False
    
    def notify_streamer_offline(self, username: str, usernick: str) -> bool:
        """通知主播下播"""
        try:
            notification_title = f"🔴 {username} 下播了"
            notification_message = f"{usernick}\n直播已结束"
            
            return self.send_notification(notification_title, notification_message)
        except Exception as e:
            print(f"发送下播通知失败: {e}")
            return False
    
    def notify_status_change(self, username: str, usernick: str, old_title: str, new_title: str) -> bool:
        """通知状态变化"""
        try:
            notification_title = f"📝 {username} 状态更新"
            notification_message = f"{usernick}\n{new_title}"
            
            return self.send_notification(notification_title, notification_message, timeout=5)
        except Exception as e:
            print(f"发送状态变化通知失败: {e}")
            return False
    
    def notify_error(self, error_message: str) -> bool:
        """发送错误通知"""
        try:
            return self.send_notification("❌ PD Signal 错误", error_message, timeout=15)
        except Exception as e:
            print(f"发送错误通知失败: {e}")
            return False
    
    def notify_info(self, info_message: str) -> bool:
        """发送信息通知"""
        try:
            return self.send_notification("ℹ️ PD Signal 信息", info_message, timeout=5)
        except Exception as e:
            print(f"发送信息通知失败: {e}")
            return False
