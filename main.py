import flet as ft
import asyncio
import threading
import time
import logging
import os
from datetime import datetime
from database_manager import DatabaseManager
from notification_manager import NotificationManager
from panda_monitor import PandaLiveMonitor

class PDSignalApp:
    def __init__(self):
        """初始化应用"""
        self.db = DatabaseManager()
        self.notifier = NotificationManager()
        self.monitor = PandaLiveMonitor(self.db, self.notifier)
        
        # 配置logger
        self._setup_logger()
        
        # UI组件
        self.page = None
        self.status_text = None
        self.all_streamers_list = None
        self.online_streamers_list = None
        self.offline_streamers_list = None
        self.cookie_field = None
        self.streamer_id_field = None
        self.streamer_remark_field = None
        self.interval_field = None
        self.main_interval_field = None
        self.streamer_interval_field = None
        self.start_stop_btn = None
        self.log_container = None
        self.theme_btn = None
        
        # 状态
        self.log_messages = []
        self.max_log_messages = 100
        self.is_dark_theme = True  # 默认暗色主题
        
        # 设置监控状态回调
        self.monitor.add_status_callback(self.on_monitor_status_change)
    
    def _setup_logger(self):
        """配置logger"""
        # 创建logger
        self.logger = logging.getLogger('PDSignalApp')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建文件handler
            log_file = os.path.join(os.path.dirname(__file__), 'log.txt')
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 创建控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 创建formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 设置formatter
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler到logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.logger.info("PDSignalApp logger 初始化完成")
    
    def on_monitor_status_change(self, message: str):
        """监控状态变化回调"""
        if self.page:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            
            # 添加到日志列表
            self.log_messages.append(log_message)
            if len(self.log_messages) > self.max_log_messages:
                self.log_messages.pop(0)
            
            # 更新UI
            self.update_log_display()
            self.update_status_display()
            self.update_streamer_list()  # 添加这行来更新主播列表
            self.page.update()
    
    def add_log_message(self, message: str):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # 记录到logger
        self.logger.info(message)
        
        # 添加到日志列表
        self.log_messages.append(log_message)
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages.pop(0)
        
        # 更新UI
        if self.page:
            self.update_log_display()
            self.page.update()
        
        # 同时输出到控制台
        print(log_message)
    
    def update_log_display(self):
        """更新日志显示"""
        if self.log_container:
            colors = self.get_theme_colors()
            self.log_container.controls.clear()
            for message in self.log_messages[-20:]:  # 只显示最近20条
                self.log_container.controls.append(
                    ft.Text(message, size=12, color=colors['text_secondary'])
                )
    
    def update_status_display(self):
        """更新状态显示"""
        if self.status_text:
            status = self.monitor.get_monitoring_status()
            status_color = ft.Colors.GREEN if status['is_running'] else ft.Colors.RED
            status_text = "运行中" if status['is_running'] else "已停止"
            
            self.status_text.value = (
                f"监控状态: {status_text} | "
                f"监控主播: {status['total_watched']} | "
                f"在线: {status['online_count']} | "
                f"离线: {status['offline_count']}"
            )
            self.status_text.color = status_color
    
    def update_streamer_list(self):
        """更新主播列表"""
        self.logger.info(f"更新主播列表: 监控状态={self.monitor.is_running}")
        
        watched_vtbs = self.db.get_all_watched_vtbs()
        self.logger.info(f"获取到 {len(watched_vtbs)} 个监控主播")
        
        # 更新所有监控主播列表（无论监控是否运行都显示）
        if watched_vtbs:
            self._update_streamer_list(self.all_streamers_list, watched_vtbs, "所有监控主播")
        else:
            self._update_streamer_list(self.all_streamers_list, [], "所有监控主播")
        
        # 只有在监控运行时才显示在线/离线数据
        if not self.monitor.is_running:
            self.logger.info("监控未运行，清空在线/离线列表")
            self._clear_online_offline_lists()
            return
        
        if not watched_vtbs:
            self.logger.info("没有监控主播，清空在线/离线列表")
            self._clear_online_offline_lists()
            return
        
        # 分离在线和离线主播
        online_vtbs = [vtb for vtb in watched_vtbs if vtb['liveStatus']]
        offline_vtbs = [vtb for vtb in watched_vtbs if not vtb['liveStatus']]
        
        self.logger.info(f"在线主播: {len(online_vtbs)}, 离线主播: {len(offline_vtbs)}")
        
        # 更新在线主播列表
        self._update_streamer_list(self.online_streamers_list, online_vtbs, "在线主播")
        
        # 更新离线主播列表
        self._update_streamer_list(self.offline_streamers_list, offline_vtbs, "离线主播")
    
    def _clear_all_streamer_lists(self):
        """清空所有主播列表"""
        if self.all_streamers_list:
            self.all_streamers_list.controls.clear()
            self.all_streamers_list.controls.append(
                ft.Container(
                    content=ft.Text("监控未启动", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
        
        if self.online_streamers_list:
            self.online_streamers_list.controls.clear()
            self.online_streamers_list.controls.append(
                ft.Container(
                    content=ft.Text("监控未启动", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
        
        if self.offline_streamers_list:
            self.offline_streamers_list.controls.clear()
            self.offline_streamers_list.controls.append(
                ft.Container(
                    content=ft.Text("监控未启动", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
    
    def _clear_online_offline_lists(self):
        """只清空在线和离线主播列表"""
        if self.online_streamers_list:
            self.online_streamers_list.controls.clear()
            self.online_streamers_list.controls.append(
                ft.Container(
                    content=ft.Text("监控未启动", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
        
        if self.offline_streamers_list:
            self.offline_streamers_list.controls.clear()
            self.offline_streamers_list.controls.append(
                ft.Container(
                    content=ft.Text("监控未启动", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
    
    def _update_streamer_list(self, list_container, vtbs, title):
        """更新单个主播列表"""
        if not list_container:
            return
            
        list_container.controls.clear()
        
        if not vtbs:
            list_container.controls.append(
                ft.Container(
                    content=ft.Text(f"暂无{title}", color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
            return
        
        for vtb in vtbs:
            # 根据列表类型决定显示内容
            if title == "所有监控主播":
                # 所有主播列：显示ID、备注和操作按钮
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(vtb['username'], 
                                       weight=ft.FontWeight.BOLD, size=14),
                                ft.Row([
                                    ft.ElevatedButton(
                                        "编辑备注",
                                        on_click=self._create_edit_remark_handler(vtb['mid']),
                                        bgcolor=self.get_theme_colors()['primary'],
                                        color=ft.Colors.WHITE,
                                        height=25,
                                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=9))
                                    ),
                                    ft.ElevatedButton(
                                        "移除",
                                        on_click=lambda e, mid=vtb['mid']: self.remove_streamer(mid),
                                        bgcolor=self.get_theme_colors()['error'],
                                        color=ft.Colors.WHITE,
                                        height=25,
                                        style=ft.ButtonStyle(text_style=ft.TextStyle(size=9))
                                    )
                                ], spacing=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ] + ([ft.Text(f"备注: {vtb.get('remark', '')}", size=10, color=ft.Colors.BLUE_400)] if vtb.get('remark') else []), spacing=3),
                        padding=8
                    ),
                    margin=ft.margin.only(bottom=3)
                )
            else:
                # 在线/离线主播列：根据列表类型显示不同信息
                status_icon = "[ONLINE]" if vtb['liveStatus'] else "[OFFLINE]"
                status_text = "在线" if vtb['liveStatus'] else "离线"
                
                if title == "离线主播":
                    # 离线主播只显示ID和备注
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"{status_icon} {vtb['username']}", 
                                           weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(status_text, 
                                           color=ft.Colors.RED,
                                           size=12)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ] + ([ft.Text(f"备注: {vtb.get('remark', '')}", size=10, color=ft.Colors.BLUE_400)] if vtb.get('remark') else []), spacing=3),
                            padding=8
                        ),
                        margin=ft.margin.only(bottom=3)
                    )
                else:
                    # 在线主播显示完整信息
                    # 构建主要内容
                    main_content = [
                        ft.Row([
                            ft.Text(f"{status_icon} {vtb['username']}", 
                                   weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(status_text, 
                                   color=ft.Colors.GREEN,
                                   size=12)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"昵称: {vtb['usernick']}", size=11),
                        ft.Text(f"标题: {vtb['title'][:30]}{'...' if len(vtb['title']) > 30 else ''}", 
                               size=10, color=ft.Colors.GREY_400)
                    ]
                    
                    # 添加备注（如果有）
                    if vtb.get('remark'):
                        main_content.append(ft.Text(f"备注: {vtb.get('remark', '')}", size=10, color=ft.Colors.BLUE_400))
                    
                    # 添加播放按钮（在备注之后）
                    main_content.append(ft.Row([
                        ft.ElevatedButton(
                            "[LIVE] 播放直播",
                            on_click=self._create_open_live_handler(vtb['mid']),
                            bgcolor=self.get_theme_colors()['primary'],
                            color=ft.Colors.WHITE,
                            height=25,
                            style=ft.ButtonStyle(text_style=ft.TextStyle(size=9))
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER))
                    
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Column(main_content, spacing=3),
                            padding=8
                        ),
                        margin=ft.margin.only(bottom=3)
                    )
            
            list_container.controls.append(card)
    
    def add_streamer(self, e):
        """添加主播"""
        if not self.streamer_id_field.value.strip():
            self.add_log_message("[ERROR] 添加主播失败: 主播ID为空")
            self.show_snackbar("请输入主播ID", ft.Colors.RED)
            return
        
        mid = self.streamer_id_field.value.strip()
        remark = self.streamer_remark_field.value.strip() if self.streamer_remark_field.value else ""
        self.add_log_message(f"[SEARCH] 正在添加主播: {mid}" + (f" (备注: {remark})" if remark else ""))
        
        # 显示加载状态
        self.show_snackbar("正在添加主播...", ft.Colors.BLUE)
        
        # 在后台线程中运行异步操作
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, message = loop.run_until_complete(self.monitor.add_streamer(mid, remark))
                if success:
                    self.add_log_message(f"[OK] {message}")
                    self.show_snackbar(message, ft.Colors.GREEN)
                    self.streamer_id_field.value = ""
                    self.streamer_remark_field.value = ""
                    self.update_streamer_list()
                    self.page.update()
                else:
                    self.add_log_message(f"[ERROR] {message}")
                    self.show_snackbar(message, ft.Colors.RED)
            except Exception as ex:
                error_msg = f"添加失败: {str(ex)}"
                self.add_log_message(f"[ERROR] {error_msg}")
                self.show_snackbar(error_msg, ft.Colors.RED)
            finally:
                loop.close()
        
        # 在后台线程中运行
        threading.Thread(target=run_async, daemon=True).start()
    
    def remove_streamer(self, mid: str):
        """移除主播"""
        try:
            self.add_log_message(f"[DELETE] 正在移除主播: {mid}")
            success, message = self.monitor.remove_streamer(mid)
            if success:
                self.add_log_message(f"[OK] {message}")
                self.show_snackbar(message, ft.Colors.GREEN)
                self.update_streamer_list()
                self.page.update()
            else:
                self.add_log_message(f"[ERROR] {message}")
                self.show_snackbar(message, ft.Colors.RED)
        except Exception as ex:
            error_msg = f"移除失败: {str(ex)}"
            self.add_log_message(f"[ERROR] {error_msg}")
            self.show_snackbar(error_msg, ft.Colors.RED)
    
    def edit_streamer_remark(self, mid: str):
        """编辑主播备注"""
        print(f"编辑备注被调用: {mid}")  # 调试信息
        self.add_log_message(f"[EDIT] 正在编辑主播 {mid} 的备注")
        
        vtb = self.db.get_vtb_by_mid(mid)
        if not vtb:
            self.add_log_message("[ERROR] 主播不存在")
            self.show_snackbar("主播不存在", ft.Colors.RED)
            return
        
        # 创建编辑对话框
        remark_field = ft.TextField(
            label="备注",
            value=vtb.get('remark', ''),
            multiline=True,
            max_lines=3,
            width=300,
            autofocus=True
        )
        
        def save_remark(e):
            new_remark = remark_field.value.strip()
            success, message = self.monitor.update_streamer_remark(mid, new_remark)
            if success:
                self.add_log_message(f"[OK] {message}")
                self.show_snackbar(message, ft.Colors.GREEN)
                self.update_streamer_list()
            else:
                self.add_log_message(f"[ERROR] {message}")
                self.show_snackbar(message, ft.Colors.RED)
            # 关闭对话框
            dialog.open = False
            self.page.update()
        
        def cancel_edit(e):
            # 关闭对话框
            dialog.open = False
            self.page.update()
        
        # 创建对话框 - 使用更完整的结构
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"编辑主播 {mid} 的备注", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=remark_field,
                padding=ft.padding.all(10)
            ),
            actions=[
                ft.TextButton("取消", on_click=cancel_edit),
                ft.TextButton("保存", on_click=save_remark)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self.add_log_message("对话框已关闭")
        )
        
        # 显示对话框
        try:
            # 将对话框添加到页面的overlay层
            if dialog not in self.page.overlay:
                self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
            self.add_log_message(f"[OK] 编辑对话框已打开")
        except Exception as ex:
            self.add_log_message(f"[ERROR] 打开对话框失败: {str(ex)}")
            self.show_snackbar(f"打开对话框失败: {str(ex)}", ft.Colors.RED)
    
    def _create_edit_remark_handler(self, mid: str):
        """创建编辑备注的事件处理器"""
        def handler(e):
            print(f"编辑备注按钮被点击: {mid}")  # 调试信息
            self.add_log_message(f"[BUTTON] 编辑备注按钮被点击: {mid}")
            try:
                self.edit_streamer_remark(mid)
            except Exception as ex:
                self.add_log_message(f"[ERROR] 编辑备注时出错: {str(ex)}")
                self.show_snackbar(f"编辑备注时出错: {str(ex)}", ft.Colors.RED)
        return handler
    
    def _create_open_live_handler(self, mid: str):
        """创建打开直播链接的事件处理器"""
        def handler(e):
            self.add_log_message(f"[BUTTON] 播放直播按钮被点击: {mid}")
            try:
                self.open_live_stream(mid)
            except Exception as ex:
                self.add_log_message(f"[ERROR] 打开直播时出错: {str(ex)}")
                self.show_snackbar(f"打开直播时出错: {str(ex)}", ft.Colors.RED)
        return handler
    
    def open_live_stream(self, mid: str):
        """打开直播链接"""
        import webbrowser
        live_url = f"https://5721004.xyz/player/pandalive.html?url={mid}"
        self.add_log_message(f"[WEB] 正在打开直播链接: {live_url}")
        try:
            webbrowser.open(live_url)
            self.add_log_message(f"[OK] 直播链接已打开: {mid}")
            self.show_snackbar(f"正在打开主播 {mid} 的直播", ft.Colors.GREEN)
        except Exception as ex:
            error_msg = f"打开直播链接失败: {str(ex)}"
            self.add_log_message(f"[ERROR] {error_msg}")
            self.show_snackbar(error_msg, ft.Colors.RED)
    
    def toggle_monitoring(self, e):
        """切换监控状态"""
        if self.monitor.is_running:
            self.add_log_message("[STOP] 正在停止监控...")
            self.monitor.stop_monitoring()
        else:
            # 检查Cookie
            if not self.monitor.get_cookie() or self.monitor.get_cookie() == "Your Cookie":
                self.add_log_message("[ERROR] 启动监控失败: Cookie未设置")
                self.show_snackbar("请先设置有效的Cookie", ft.Colors.RED)
                return
            
            self.add_log_message("[START] 正在启动监控...")
            self.monitor.start_monitoring()
        
        # 更新按钮状态和状态显示
        self.update_button_state()
        self.update_status_display()  # 更新监控状态显示
        self.update_streamer_list()  # 更新主播列表
        self.page.update()
    
    def save_cookie(self, e):
        """保存Cookie"""
        cookie = self.cookie_field.value.strip()
        if cookie:
            self.monitor.set_cookie(cookie)
            self.add_log_message("[OK] Cookie已保存")
            self.show_snackbar("Cookie已保存", ft.Colors.GREEN)
        else:
            self.add_log_message("[ERROR] Cookie为空，保存失败")
            self.show_snackbar("请输入有效的Cookie", ft.Colors.RED)
    
    def save_intervals(self, e):
        """保存间隔设置"""
        try:
            check_interval = int(self.interval_field.value) if self.interval_field.value else 2
            main_interval = int(self.main_interval_field.value) if self.main_interval_field.value else 60
            streamer_interval = int(self.streamer_interval_field.value) if self.streamer_interval_field.value else 5
            
            self.monitor.set_intervals(check_interval, main_interval, streamer_interval)
            self.add_log_message(f"[SETTINGS] 间隔设置已保存: 检测={check_interval}s, 更新={main_interval}s, 主播间={streamer_interval}s")
            self.show_snackbar("间隔设置已保存", ft.Colors.GREEN)
        except ValueError:
            self.add_log_message("[ERROR] 间隔设置保存失败: 输入格式错误")
            self.show_snackbar("请输入有效的数字", ft.Colors.RED)
    
    def show_snackbar(self, message: str, color):
        """显示消息条"""
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=color
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def toggle_theme(self, e):
        """切换主题"""
        self.is_dark_theme = not self.is_dark_theme
        if self.page:
            self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_theme else ft.ThemeMode.LIGHT
            self.db.set_config("theme", "dark" if self.is_dark_theme else "light")
            
            self.add_log_message(f"[THEME] 主题已切换为: {'暗色' if self.is_dark_theme else '亮色'}")
            
            # 重新构建界面以应用新主题
            self.page.clean()
            self.build_ui(self.page)
            
            # 重新加载数据以恢复状态
            self.load_initial_data()
    
    def load_initial_data(self):
        """加载初始数据"""
        # 恢复Cookie设置
        if self.cookie_field:
            saved_cookie = self.db.get_config("cookie", "")
            self.cookie_field.value = saved_cookie
        
        # 恢复间隔设置
        if self.interval_field:
            saved_check_interval = self.db.get_config("check_interval", "2")
            self.interval_field.value = saved_check_interval
        
        if self.main_interval_field:
            saved_main_interval = self.db.get_config("main_interval", "60")
            self.main_interval_field.value = saved_main_interval
        
        if self.streamer_interval_field:
            saved_streamer_interval = self.db.get_config("streamer_interval", "5")
            self.streamer_interval_field.value = saved_streamer_interval
        
        # 恢复监控状态
        self.update_status_display()
        self.update_streamer_list()
        
        # 恢复日志消息
        for message in self.log_messages:
            self.log_container.controls.append(
                ft.Text(message, size=12, color=self.get_theme_colors()['text_secondary'])
            )
        
        # 更新页面
        if self.page:
            self.page.update()
    
    def get_theme_colors(self):
        """获取当前主题的颜色配置"""
        if self.is_dark_theme:
            return {
                'primary': ft.Colors.BLUE_400,
                'success': ft.Colors.GREEN_400,
                'error': ft.Colors.RED_400,
                'warning': ft.Colors.ORANGE_400,
                'text_primary': ft.Colors.WHITE,
                'text_secondary': ft.Colors.WHITE70,
                'background': ft.Colors.BLACK12,
                'surface': ft.Colors.GREY_900
            }
        else:
            return {
                'primary': ft.Colors.BLUE_600,
                'success': ft.Colors.GREEN_600,
                'error': ft.Colors.RED_600,
                'warning': ft.Colors.ORANGE_600,
                'text_primary': ft.Colors.BLACK87,
                'text_secondary': ft.Colors.BLACK54,
                'background': ft.Colors.WHITE,
                'surface': ft.Colors.GREY_100
            }
    
    def update_button_state(self):
        """更新按钮状态"""
        if self.start_stop_btn:
            colors = self.get_theme_colors()
            if self.monitor.is_running:
                self.start_stop_btn.text = "停止监控"
                self.start_stop_btn.bgcolor = colors['error']
                self.start_stop_btn.color = ft.Colors.WHITE
            else:
                self.start_stop_btn.text = "开始监控"
                self.start_stop_btn.bgcolor = colors['success']
                self.start_stop_btn.color = ft.Colors.WHITE
    
    def clear_logs(self, e):
        """清空日志"""
        self.add_log_message("[DELETE] 日志已清空")
        self.log_messages.clear()
        self.update_log_display()
        self.page.update()
    
    def build_ui(self, page: ft.Page):
        """构建用户界面"""
        self.page = page
        page.title = "PD Signal - PandaLive监控"
        page.window_width = 1400
        page.window_height = 900
        page.window_resizable = True
        page.padding = 0
        
        # 加载配置
        saved_cookie = self.monitor.get_cookie()
        saved_check_interval = self.db.get_config("check_interval", "2")
        saved_main_interval = self.db.get_config("main_interval", "60")
        saved_streamer_interval = self.db.get_config("streamer_interval", "5")
        saved_theme = self.db.get_config("theme", "dark")
        self.is_dark_theme = saved_theme == "dark"
        
        # 设置主题模式（在加载配置后）
        page.theme_mode = ft.ThemeMode.DARK if self.is_dark_theme else ft.ThemeMode.LIGHT
        
        # 获取主题颜色
        colors = self.get_theme_colors()
        
        # ==================== 顶部标题栏 ====================
        header = ft.Container(
            content=ft.Row([
                ft.Text("PD Signal", size=28, weight=ft.FontWeight.BOLD, color=colors['primary']),
                ft.Text("PandaLive 监控系统", size=16, color=colors['text_secondary']),
                ft.Container(expand=True),  # 占位符，推动右侧内容到右边
                ft.ElevatedButton(
                    "[DARK] 暗色" if self.is_dark_theme else "[LIGHT] 亮色",
                    on_click=self.toggle_theme,
                    bgcolor=colors['primary'],
                    color=ft.Colors.WHITE,
                    height=40
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=colors['surface'],
            padding=20,
            border_radius=0
        )
        
        # ==================== 状态栏 ====================
        self.status_text = ft.Text("监控状态: 已停止", size=16, weight=ft.FontWeight.BOLD)
        self.start_stop_btn = ft.ElevatedButton(
            "开始监控",
            on_click=self.toggle_monitoring,
            bgcolor=colors['success'],
            color=ft.Colors.WHITE,
            height=40,
            width=120
        )
        
        status_bar = ft.Container(
            content=ft.Row([
                self.status_text,
                ft.Container(expand=True),
                self.start_stop_btn
            ]),
            bgcolor=colors['background'],
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border=ft.border.only(bottom=ft.border.BorderSide(1, colors['text_secondary']))
        )
        
        # ==================== 配置面板 ====================
        # Cookie设置
        self.cookie_field = ft.TextField(
            label="Cookie",
            hint_text="从浏览器复制PandaLive的Cookie",
            value=saved_cookie,
            password=False,
            expand=True,
            border_radius=8
        )
        
        # 间隔设置
        self.interval_field = ft.TextField(
            label="检测间隔(秒)",
            value=saved_check_interval,
            width=120,
            border_radius=8
        )
        
        self.main_interval_field = ft.TextField(
            label="更新间隔(秒)",
            value=saved_main_interval,
            width=120,
            border_radius=8
        )
        
        self.streamer_interval_field = ft.TextField(
            label="主播间间隔(秒)",
            value=saved_streamer_interval,
            width=120,
            border_radius=8
        )
        
        # 添加主播
        self.streamer_id_field = ft.TextField(
            label="主播ID",
            hint_text="输入要监控的主播ID",
            expand=True,
            border_radius=8
        )
        
        self.streamer_remark_field = ft.TextField(
            label="备注(可选)",
            hint_text="为主播添加备注信息",
            expand=True,
            border_radius=8
        )
        
        config_panel = ft.Container(
            content=ft.Column([
                # Cookie区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("Cookie 设置", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.cookie_field,
                            ft.ElevatedButton("保存", on_click=self.save_cookie, 
                                           bgcolor=colors['primary'], color=ft.Colors.WHITE,
                                           height=40)
                        ], spacing=10)
                    ], spacing=8),
                    bgcolor=colors['surface'],
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(bottom=10)
                ),
                
                # 监控设置区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("监控设置", size=16, weight=ft.FontWeight.BOLD),
                        
                        # 更新间隔设置
                        ft.Column([
                            ft.Row([
                                self.main_interval_field,
                                ft.ElevatedButton("保存", on_click=self.save_intervals,
                                               bgcolor=colors['primary'], color=ft.Colors.WHITE,
                                               height=40)
                            ], spacing=10),
                            ft.Text("更新间隔: 获取所有在线主播列表的间隔时间", 
                                   size=11, color=colors['text_secondary'])
                        ], spacing=5),
                        
                        # 检测间隔设置
                        ft.Column([
                            ft.Row([
                                self.interval_field,
                                ft.ElevatedButton("保存", on_click=self.save_intervals,
                                               bgcolor=colors['primary'], color=ft.Colors.WHITE,
                                               height=40)
                            ], spacing=10),
                            ft.Text("检测间隔: 对监控列表中的所有主播进行一轮检测的间隔时间", 
                                   size=11, color=colors['text_secondary'])
                        ], spacing=5),
                        
                        # 主播间间隔设置
                        ft.Column([
                            ft.Row([
                                self.streamer_interval_field,
                                ft.ElevatedButton("保存", on_click=self.save_intervals,
                                               bgcolor=colors['primary'], color=ft.Colors.WHITE,
                                               height=40)
                            ], spacing=10),
                            ft.Text("主播间间隔: 检测每个主播之间等待的时间", 
                                   size=11, color=colors['text_secondary'])
                        ], spacing=5)
                    ], spacing=15),
                    bgcolor=colors['surface'],
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(bottom=10)
                ),
                
                # 添加主播区域
                ft.Container(
                    content=ft.Column([
                        ft.Text("添加主播", size=16, weight=ft.FontWeight.BOLD),
                        self.streamer_id_field,
                        self.streamer_remark_field,
                        ft.ElevatedButton("添加", on_click=self.add_streamer,
                                       bgcolor=colors['success'], color=ft.Colors.WHITE,
                                       height=40)
                    ], spacing=8),
                    bgcolor=colors['surface'],
                    padding=15,
                    border_radius=10
                )
            ], spacing=0),
            padding=20,
            width=400
        )
        
        # ==================== 监控列表区域 ====================
        self.all_streamers_list = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.online_streamers_list = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.offline_streamers_list = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        # 初始化列表显示
        self._clear_all_streamer_lists()
        
        # 创建监控列表布局（只包含所有主播和在线主播）
        monitor_panel = ft.Container(
            content=ft.Column([
                
                # 所有监控主播行
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("所有监控主播", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            bgcolor=colors['primary'],
                            padding=10,
                            border_radius=ft.border_radius.only(top_left=10, top_right=10)
                        ),
                        ft.Container(
                            content=self.all_streamers_list,
                            height=200,
                            width=400,  # 固定宽度
                            padding=10,
                            bgcolor=colors['surface'],
                            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                            border=ft.border.all(1, colors['text_secondary'])
                        )
                    ], spacing=0),
                    margin=ft.margin.only(bottom=15)
                ),
                
                # 在线主播行（增大显示区域）
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("在线主播", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN_600,
                            padding=10,
                            border_radius=ft.border_radius.only(top_left=10, top_right=10)
                        ),
                        ft.Container(
                            content=self.online_streamers_list,
                            height=350,  # 增大高度从120到350
                            width=400,  # 固定宽度
                            padding=10,
                            bgcolor=colors['surface'],
                            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                            border=ft.border.all(1, colors['text_secondary'])
                        )
                    ], spacing=0)
                )
            ], spacing=0),
            padding=20,
            expand=True
        )
        
        # ==================== 日志区域 ====================
        self.log_container = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        log_panel = ft.Container(
            content=ft.Column([
                # 离线主播区域（移动到日志上方）
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text("离线主播", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED_600,
                            padding=10,
                            border_radius=ft.border_radius.only(top_left=10, top_right=10)
                        ),
                        ft.Container(
                            content=self.offline_streamers_list,
                            height=220,
                            width=400,  # 固定宽度
                            padding=10,
                            bgcolor=colors['surface'],
                            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                            border=ft.border.all(1, colors['text_secondary'])
                        )
                    ], spacing=0),
                    margin=ft.margin.only(bottom=15)
                ),
                
                # 日志区域
                ft.Row([
                    ft.Text("运行日志", size=16, weight=ft.FontWeight.BOLD, color=colors['primary']),
                    ft.Container(expand=True),
                    ft.ElevatedButton("清空日志", on_click=self.clear_logs,
                                   bgcolor=colors['warning'], color=ft.Colors.WHITE,
                                   height=35)
                ]),
                ft.Container(
                    content=self.log_container,
                    height=300,
                    width=400,  # 固定宽度
                    bgcolor=colors['surface'],
                    border_radius=10,
                    padding=15,
                    border=ft.border.all(1, colors['text_secondary'])
                )
            ], spacing=10),
            padding=20,
            width=400
        )
        
        # ==================== 主布局 ====================
        main_content = ft.Row([
            config_panel,  # 左侧配置面板
            monitor_panel,  # 中间监控列表
            log_panel      # 右侧日志面板
        ], spacing=0, expand=True)
        
        # 整体布局
        page.add(
            ft.Column([
                header,      # 顶部标题栏
                status_bar,  # 状态栏
                ft.Container(
                    content=main_content,
                    expand=True
                )
            ], spacing=0, expand=True)
        )
        
        # 初始化状态显示
        self.update_status_display()
        self.update_button_state()
        self.update_streamer_list()  # 初始化主播列表显示
        
        # 添加初始化日志
        self.add_log_message("[START] PD Signal 应用已启动")
        self.add_log_message(f"[STATS] 数据库路径: {self.db.db_path}")
        self.add_log_message(f"[THEME] 当前主题: {'暗色' if self.is_dark_theme else '亮色'}")
        
        # 检查Cookie状态
        cookie = self.monitor.get_cookie()
        if cookie and cookie != "Your Cookie":
            self.add_log_message("[OK] Cookie已设置")
        else:
            self.add_log_message("[WARNING] 请设置PandaLive Cookie")
        
        # 检查监控列表
        watched_count = len(self.db.get_all_watched_vtbs())
        self.add_log_message(f"[LIST] 当前监控主播数量: {watched_count}")
        
        page.update()
    
    def run(self):
        """运行应用"""
        ft.app(target=self.build_ui)

def main():
    """主函数"""
    app = PDSignalApp()
    app.run()

if __name__ == "__main__":
    main()
