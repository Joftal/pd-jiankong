import asyncio
import json
import time
import requests
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Callable
import threading
from database_manager import DatabaseManager
from notification_manager import NotificationManager

class PandaLiveMonitor:
    def __init__(self, db_manager: DatabaseManager, notification_manager: NotificationManager):
        """初始化PandaLive监控器"""
        self.db = db_manager
        self.notifier = notification_manager
        self.is_running = False
        self.monitor_thread = None
        self.cookie = ""
        self.check_interval = int(self.db.get_config("check_interval", "2"))  # 检测间隔（秒）
        self.main_interval = int(self.db.get_config("main_interval", "60"))  # 获取列表间隔（秒）
        self.streamer_interval = int(self.db.get_config("streamer_interval", "5"))  # 主播间检测间隔（秒）
        self.batch_size = 96  # 一次获取的数据量
        self.cached_data = {}
        self.status_callbacks = []  # 状态回调函数列表
        
        # 代理设置
        self.proxy_enabled = self.db.get_config("proxy_enabled", "false").lower() == "true"
        self.proxy_url = self.db.get_config("proxy_url", "")
        
        # 配置logger
        self._setup_logger()
    
    def _setup_logger(self):
        """配置logger"""
        # 创建logger
        self.logger = logging.getLogger('PandaLiveMonitor')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 获取可执行文件所在目录
            if getattr(sys, 'frozen', False):
                # PyInstaller打包后的路径
                app_dir = os.path.dirname(sys.executable)
            else:
                # 开发环境路径
                app_dir = os.path.dirname(__file__)
            
            # 创建文件handler
            log_file = os.path.join(app_dir, 'log.txt')
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
        
        self.logger.info(f"PandaLiveMonitor logger 初始化完成，日志文件: {log_file}")
        
    def set_cookie(self, cookie: str):
        """设置Cookie"""
        self.cookie = cookie
        self.db.set_config("cookie", cookie)
    
    def get_cookie(self) -> str:
        """获取Cookie"""
        if not self.cookie:
            self.cookie = self.db.get_config("cookie", "")
        return self.cookie
    
    def set_intervals(self, check_interval: int = 2, main_interval: int = 60, streamer_interval: int = 5):
        """设置监控间隔"""
        self.check_interval = max(1, check_interval)
        self.main_interval = max(30, main_interval)
        self.streamer_interval = max(1, streamer_interval)
        self.db.set_config("check_interval", str(self.check_interval))
        self.db.set_config("main_interval", str(self.main_interval))
        self.db.set_config("streamer_interval", str(self.streamer_interval))
    
    def set_proxy(self, enabled: bool, proxy_url: str = ""):
        """设置代理"""
        old_enabled = self.proxy_enabled
        old_url = self.proxy_url
        
        self.proxy_enabled = enabled
        self.proxy_url = proxy_url.strip()
        self.db.set_config("proxy_enabled", "true" if enabled else "false")
        self.db.set_config("proxy_url", self.proxy_url)
        
        # 记录代理设置变更
        if old_enabled != enabled or old_url != self.proxy_url:
            if enabled and self.proxy_url:
                self._notify_status_change(f"[PROXY] 代理设置已更新: 启用代理 {self.proxy_url}")
            else:
                self._notify_status_change("[PROXY] 代理设置已更新: 禁用代理，使用直连")
    
    def get_proxy_config(self) -> dict:
        """获取代理配置"""
        if self.proxy_enabled and self.proxy_url:
            # 确保代理URL以http://开头
            if not self.proxy_url.startswith(('http://', 'https://')):
                self.proxy_url = f"http://{self.proxy_url}"
            return {
                'http': self.proxy_url,
                'https': self.proxy_url
            }
        return {}
    
    def add_status_callback(self, callback: Callable):
        """添加状态回调函数"""
        self.status_callbacks.append(callback)
    
    def _notify_status_change(self, message: str):
        """通知状态变化"""
        for callback in self.status_callbacks:
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"回调函数执行失败: {e}")
    
    async def fetch_json(self, offset: int, limit: int) -> Optional[Dict]:
        """获取PandaLive API数据"""
        try:
            url = "https://api.pandalive.co.kr/v1/live"
            params = {
                'offset': offset,
                'limit': limit,
                'orderBy': 'hot',
                'onlyNewBj': 'N'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'cookie': self.get_cookie()
            }
            
            self._notify_status_change(f"[WEB] 正在请求API: offset={offset}, limit={limit}")
            start_time = time.time()
            
            # 获取代理配置
            proxies = self.get_proxy_config()
            if proxies:
                self._notify_status_change(f"[PROXY] 使用代理请求API: {self.proxy_url}")
            else:
                self._notify_status_change("[PROXY] 使用直连请求API")
            
            response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=5)
            response.raise_for_status()
            
            request_time = time.time() - start_time
            self._notify_status_change(f"[OK] API请求成功: 耗时{request_time:.2f}秒, 状态码={response.status_code}")
            
            data = response.json()
            if data and data.get('result'):
                list_count = len(data.get('list', []))
                self._notify_status_change(f"[LIST] 解析数据成功: 获取到{list_count}个主播信息")
            else:
                self._notify_status_change("[WARNING] API返回数据为空或格式异常")
            
            return data
        except Exception as e:
            error_msg = f"获取API数据失败: {e}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
            return None
    
    async def fetch_streamer_info(self, mid: str) -> Optional[Dict]:
        """获取单个主播信息"""
        try:
            url = "https://api.pandalive.co.kr/v1/member/bj"
            data = {
                'userId': mid,
                'info': 'media'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'x-device-info': '{"t":"webPc","v":"1.0","ui":24631221}'
            }
            
            self._notify_status_change(f"[SEARCH] 正在获取主播 {mid} 的详细信息")
            start_time = time.time()
            
            # 获取代理配置
            proxies = self.get_proxy_config()
            if proxies:
                self._notify_status_change(f"[PROXY] 使用代理请求主播信息: {self.proxy_url}")
            else:
                self._notify_status_change("[PROXY] 使用直连请求主播信息")
            
            response = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=5)
            response.raise_for_status()
            
            request_time = time.time() - start_time
            self._notify_status_change(f"[OK] 主播信息请求成功: {mid}, 耗时{request_time:.2f}秒")
            
            result = response.json()
            if result and result.get('result'):
                self._notify_status_change(f"[LIST] 主播 {mid} 信息解析成功")
            else:
                self._notify_status_change(f"[WARNING] 主播 {mid} 信息为空或格式异常")
            
            return result
        except Exception as e:
            error_msg = f"获取主播信息失败 {mid}: {e}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
            return None
    
    async def update_all_streamers_data(self):
        """更新所有在线主播数据"""
        try:
            cookie = self.get_cookie()
            if not cookie or cookie == "Your Cookie":
                self._notify_status_change("[WARNING] 请设置有效的Cookie")
                return
            
            self._notify_status_change("🔄 开始更新所有主播数据...")
            start_time = time.time()
            
            # 获取第一页数据
            json_data = await self.fetch_json(0, self.batch_size)
            if not json_data or not json_data.get('result'):
                self._notify_status_change("[ERROR] 获取列表失败")
                return
            
            total = json_data.get('page', {}).get('total', 0)
            first_page_count = len(json_data.get('list', []))
            self._notify_status_change(f"[STATS] 在线主播总数: {total} | 第一页获取: {first_page_count}个主播")
            
            # 如果在线主播数超过batch_size，获取更多页面
            if total > self.batch_size:
                remaining = total - self.batch_size
                page = 2
                total_pages = (total + self.batch_size - 1) // self.batch_size
                self._notify_status_change(f"📄 需要获取 {total_pages} 页数据，开始获取剩余页面...")
                
                while remaining > 0:
                    self._notify_status_change(f"📄 正在获取第{page}页 (剩余{remaining}个主播)")
                    offset = (page - 1) * self.batch_size
                    limit = min(self.batch_size, remaining)
                    
                    json2 = await self.fetch_json(offset, limit)
                    if json2 and json2.get('list'):
                        # 合并数据，避免重复
                        existing_codes = {item.get('code') for item in json_data.get('list', [])}
                        new_items = [item for item in json2.get('list', []) 
                                   if item.get('code') not in existing_codes]
                        json_data['list'].extend(new_items)
                        self._notify_status_change(f"[OK] 第{page}页合并成功: 新增{len(new_items)}个主播")
                        remaining -= self.batch_size
                        page += 1
                    else:
                        self._notify_status_change(f"[WARNING] 第{page}页获取失败，停止获取")
                        break
            
            # 保存数据到缓存
            self.cached_data = json_data
            total_time = time.time() - start_time
            final_count = len(json_data.get('list', []))
            self._notify_status_change(f"[OK] 数据更新完成: 总计{final_count}个主播, 耗时{total_time:.2f}秒")
            
        except Exception as e:
            error_msg = f"更新数据失败: {str(e)}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
    
    async def check_watched_streamers(self):
        """检查监控的主播状态"""
        watched_vtbs = self.db.get_all_watched_vtbs()
        if not watched_vtbs:
            self._notify_status_change("[LIST] 没有需要监控的主播")
            return
        
        if not self.cached_data or not self.cached_data.get('list'):
            self._notify_status_change("[WARNING] 缓存数据为空，跳过主播状态检查")
            return
        
        self._notify_status_change(f"[SEARCH] 开始检查 {len(watched_vtbs)} 个监控主播的状态...")
        start_time = time.time()
        online_count = 0
        offline_count = 0
        
        # 处理每个监控的主播
        for i, vtb in enumerate(watched_vtbs, 1):
            try:
                self._notify_status_change(f"[SEARCH] [{i}/{len(watched_vtbs)}] 检查主播: {vtb['mid']}")
                
                # 在缓存数据中查找该主播
                streamer_data = None
                for item in self.cached_data.get('list', []):
                    if item.get('userId') == vtb['mid']:
                        streamer_data = item
                        break
                
                if streamer_data:
                    # 主播在线
                    await self._process_online_streamer(vtb, streamer_data)
                    online_count += 1
                    self._notify_status_change(f"[ONLINE] [{i}/{len(watched_vtbs)}] {vtb['mid']}: 在线")
                    self.logger.info(f"{vtb['mid']}: online")
                else:
                    # 主播离线
                    await self._process_offline_streamer(vtb)
                    offline_count += 1
                    self._notify_status_change(f"[OFFLINE] [{i}/{len(watched_vtbs)}] {vtb['mid']}: 离线")
                    self.logger.info(f"{vtb['mid']}: offline")
                
                # 检查间隔
                if i < len(watched_vtbs):  # 不是最后一个主播
                    self._notify_status_change(f"⏱️ 等待 {self.streamer_interval} 秒后检查下一个主播...")
                    await asyncio.sleep(self.streamer_interval)
                
            except Exception as e:
                error_msg = f"检查主播 {vtb['mid']} 时出错: {e}"
                self.logger.error(error_msg)
                self._notify_status_change(f"[ERROR] {error_msg}")
        
        total_time = time.time() - start_time
        self._notify_status_change(f"[OK] 主播状态检查完成: 在线{online_count}个, 离线{offline_count}个, 耗时{total_time:.2f}秒")
    
    async def _process_online_streamer(self, vtb: Dict, streamer_data: Dict):
        """处理在线主播"""
        start_time = streamer_data.get('startTime', '')
        title = streamer_data.get('title', '')
        usernick = streamer_data.get('userNick', '')
        
        # 构建标题标识
        live_type = "🎥" if streamer_data.get('liveType') == "rec" else ""
        is_pw = "🔒" if streamer_data.get('isPw') else ""
        is_adult = "🔞" if streamer_data.get('isAdult') else ""
        fan_type = "💰" if streamer_data.get('type') == "fan" else ""
        full_title = f"{live_type}{fan_type}{is_pw}{is_adult}{title}"
        
        # 检查是否有变化
        status_changed = False
        went_online = False
        
        if usernick != vtb['usernick']:
            self.db.update_vtb_column('usernick', usernick, vtb['mid'])
            status_changed = True
        
        if full_title != vtb['title']:
            self.db.update_vtb_column('title', full_title, vtb['mid'])
            status_changed = True
        
        if start_time != vtb['liveStatus']:
            self.db.update_vtb_column('liveStatus', start_time, vtb['mid'])
            
            # 检查是否从离线变为在线
            if vtb['liveStatus'] == '' or vtb['liveStatus'] is None:
                went_online = True
                # 发送开播通知
                self.notifier.notify_streamer_online(
                    vtb['username'], usernick, full_title, start_time
                )
                self._notify_status_change(f"[ONLINE] 主播 {vtb['mid']} 开播了！")
            
            status_changed = True
        
        # 更新内存中的数据
        vtb.update({
            'usernick': usernick,
            'title': full_title,
            'liveStatus': start_time
        })
        
        # 如果状态发生变化，通知UI更新
        if status_changed:
            self._notify_status_change(f"[UPDATE] 主播 {vtb['mid']} 信息已更新")
    
    async def _process_offline_streamer(self, vtb: Dict):
        """处理离线主播"""
        if vtb['liveStatus'] and vtb['liveStatus'] != '':
            # 从在线变为离线
            self.db.update_vtb_column('liveStatus', '', vtb['mid'])
            self.notifier.notify_streamer_offline(vtb['username'], vtb['usernick'])
            self._notify_status_change(f"[OFFLINE] 主播 {vtb['mid']} 下播了！")
            vtb['liveStatus'] = ''
    
    def start_monitoring(self):
        """启动监控"""
        if self.is_running:
            self._notify_status_change("[WARNING] 监控已在运行中")
            return False
        
        self._notify_status_change("[START] 正在启动监控系统...")
        self._notify_status_change(f"[SETTINGS] 监控配置: 检测间隔={self.check_interval}秒, 主循环间隔={self.main_interval}秒, 主播间间隔={self.streamer_interval}秒")
        
        # 记录代理使用状态
        if self.proxy_enabled and self.proxy_url:
            self._notify_status_change(f"[PROXY] 代理已启用: {self.proxy_url}")
        else:
            self._notify_status_change("[PROXY] 代理未启用，使用直连")
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self._notify_status_change("[OK] 监控系统启动成功")
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_running:
            self._notify_status_change("[WARNING] 监控未在运行")
            return
            
        self._notify_status_change("[STOP] 正在停止监控系统...")
        self.is_running = False
        
        # 强制将所有主播状态改为离线
        self._force_all_streamers_offline()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            if self.monitor_thread.is_alive():
                self._notify_status_change("[WARNING] 监控线程未能在5秒内停止")
            else:
                self._notify_status_change("[OK] 监控线程已安全停止")
        
        self._notify_status_change("[STOP] 监控系统已完全停止")
    
    def _force_all_streamers_offline(self):
        """强制将所有主播状态改为离线"""
        try:
            watched_vtbs = self.db.get_all_watched_vtbs()
            if not watched_vtbs:
                self._notify_status_change("[OFFLINE] 没有需要设置为离线的主播")
                return
            
            offline_count = 0
            self._notify_status_change(f"[OFFLINE] 正在强制设置 {len(watched_vtbs)} 个主播为离线状态...")
            
            for vtb in watched_vtbs:
                if vtb['liveStatus'] and vtb['liveStatus'] != '':
                    # 只有当前在线的才需要设置为离线
                    self.db.update_vtb_column('liveStatus', '', vtb['mid'])
                    offline_count += 1
                    self._notify_status_change(f"[OFFLINE] 主播 {vtb['mid']} 已设置为离线")
            
            if offline_count > 0:
                self._notify_status_change(f"[OK] 已强制设置 {offline_count} 个主播为离线状态")
            else:
                self._notify_status_change("[OK] 所有主播已经是离线状态")
                
        except Exception as e:
            error_msg = f"强制设置主播离线状态失败: {str(e)}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
    
    def _monitoring_loop(self):
        """监控主循环"""
        async def async_monitoring_loop():
            update_cycle_count = 0
            check_cycle_count = 0
            last_update_time = 0
            last_check_time = 0
            
            # 程序启动时立即进行一次数据更新
            self._notify_status_change("[START] 程序启动，正在获取初始数据...")
            await self.update_all_streamers_data()
            last_update_time = time.time()
            self.logger.info(f"初始数据更新完成，时间戳: {last_update_time}")
            
            while self.is_running:
                try:
                    current_time = time.time()
                    
                    # 检查是否需要更新在线主播列表（更新间隔）
                    if current_time - last_update_time >= self.main_interval:
                        update_cycle_count += 1
                        self._notify_status_change(f"🔄 开始第 {update_cycle_count} 轮数据更新...")
                        self.logger.info(f"触发数据更新，第 {update_cycle_count} 轮")
                        
                        await self.update_all_streamers_data()
                        last_update_time = current_time
                        self._notify_status_change(f"[OK] 数据更新完成")
                        self.logger.info(f"数据更新完成，下次更新时间: {last_update_time}")
                    
                    # 检查是否需要检测监控主播（检测间隔）
                    if current_time - last_check_time >= self.check_interval:
                        check_cycle_count += 1
                        self._notify_status_change(f"[SEARCH] 开始第 {check_cycle_count} 轮主播检测...")
                        self.logger.info(f"触发主播检测，第 {check_cycle_count} 轮")
                        
                        await self.check_watched_streamers()
                        last_check_time = current_time
                        self._notify_status_change(f"[OK] 主播检测完成")
                        self.logger.info(f"主播检测完成，下次检测时间: {last_check_time}")
                    
                    # 简单等待1秒后重新检查
                    await asyncio.sleep(1)
                        
                except Exception as e:
                    error_msg = f"监控循环出错: {str(e)}"
                    self.logger.error(error_msg)
                    self._notify_status_change(f"[ERROR] {error_msg}")
                    self._notify_status_change("⏳ 出错后等待30秒再继续...")
                    await asyncio.sleep(30)  # 出错后等待30秒再继续
        
        # 运行异步循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_monitoring_loop())
    
    async def add_streamer(self, mid: str, remark: str = "") -> tuple:
        """添加主播到监控列表"""
        try:
            self._notify_status_change(f"[SEARCH] 开始添加主播 {mid} 到监控列表...")
            
            # 检查是否已在监控列表中
            existing = self.db.get_vtb_by_mid(mid)
            if existing and self.db.get_all_watched_vtbs():
                watched_mids = [vtb['mid'] for vtb in self.db.get_all_watched_vtbs()]
                if mid in watched_mids:
                    self._notify_status_change(f"[WARNING] 主播 {mid} 已在监控列表中")
                    return False, f"主播 {mid} 已在监控列表中"
            
            self._notify_status_change(f"📡 正在获取主播 {mid} 的详细信息...")
            
            # 获取主播信息
            streamer_info = await self.fetch_streamer_info(mid)
            if not streamer_info or not streamer_info.get('result'):
                self._notify_status_change(f"[ERROR] 无法获取主播 {mid} 的信息")
                return False, f"无法获取主播 {mid} 的信息"
            
            media_data = streamer_info.get('media', {})
            start_time = media_data.get('startTime', '')
            title = media_data.get('title', '')
            usernick = media_data.get('userNick', '')
            
            self._notify_status_change(f"[LIST] 主播 {mid} 信息获取成功: 昵称={usernick}, 标题={title[:30]}...")
            
            # 构建完整标题
            live_type = "🎥" if media_data.get('liveType') == "rec" else ""
            is_pw = "🔒" if media_data.get('isPw') else ""
            is_adult = "🔞" if media_data.get('isAdult') else ""
            fan_type = "💰" if media_data.get('type') == "fan" else ""
            full_title = f"{live_type}{fan_type}{is_pw}{is_adult}{title}"
            
            self._notify_status_change(f"💾 正在将主播 {mid} 添加到数据库...")
            
            # 添加到数据库
            success = self.db.add_vtb_to_watch(
                mid=mid,
                username=mid,
                usernick=usernick,
                live_status=start_time,
                title=full_title,
                platform="panda",
                hls="",
                remark=remark
            )
            
            if success:
                self._notify_status_change(f"[OK] 主播 {mid} 添加成功")
                return True, f"成功添加主播 {mid}"
            else:
                self._notify_status_change(f"[ERROR] 主播 {mid} 添加到数据库失败")
                return False, f"添加主播 {mid} 失败"
                
        except Exception as e:
            error_msg = f"添加主播时出错: {str(e)}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def remove_streamer(self, mid: str) -> tuple:
        """从监控列表中移除主播"""
        try:
            self._notify_status_change(f"[DELETE] 开始移除主播 {mid} 从监控列表...")
            
            vtb = self.db.get_vtb_by_mid(mid)
            if not vtb:
                self._notify_status_change(f"[WARNING] 主播 {mid} 不存在于监控列表中")
                return False, f"主播 {mid} 不存在"
            
            self._notify_status_change(f"💾 正在从数据库中移除主播 {mid}...")
            
            success = self.db.remove_from_watch(mid)
            if success:
                self._notify_status_change(f"[OK] 主播 {mid} 移除成功")
                return True, f"成功移除主播 {mid}"
            else:
                self._notify_status_change(f"[ERROR] 主播 {mid} 从数据库移除失败")
                return False, f"移除主播 {mid} 失败"
                
        except Exception as e:
            error_msg = f"移除主播时出错: {str(e)}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def update_streamer_remark(self, mid: str, remark: str) -> tuple:
        """更新主播备注"""
        try:
            self._notify_status_change(f"[EDIT] 开始更新主播 {mid} 的备注...")
            
            vtb = self.db.get_vtb_by_mid(mid)
            if not vtb:
                self._notify_status_change(f"[WARNING] 主播 {mid} 不存在于监控列表中")
                return False, f"主播 {mid} 不存在"
            
            success = self.db.update_vtb_remark(mid, remark)
            if success:
                self._notify_status_change(f"[OK] 主播 {mid} 备注更新成功")
                return True, f"成功更新主播 {mid} 的备注"
            else:
                self._notify_status_change(f"[ERROR] 主播 {mid} 备注更新失败")
                return False, f"更新主播 {mid} 备注失败"
                
        except Exception as e:
            error_msg = f"更新主播备注时出错: {str(e)}"
            self.logger.error(error_msg)
            self._notify_status_change(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def get_monitoring_status(self) -> Dict:
        """获取监控状态"""
        watched_vtbs = self.db.get_all_watched_vtbs()
        
        # 只有在监控运行时才计算在线/离线数量
        if self.is_running:
            online_count = len([vtb for vtb in watched_vtbs if vtb['liveStatus']])
            offline_count = len(watched_vtbs) - online_count
        else:
            # 监控未运行时，不显示在线/离线数量（因为数据可能过时）
            online_count = 0
            offline_count = 0
        
        return {
            'is_running': self.is_running,
            'total_watched': len(watched_vtbs),
            'online_count': online_count,
            'offline_count': offline_count,
            'check_interval': self.check_interval,
            'main_interval': self.main_interval,
            'streamer_interval': self.streamer_interval,
            'has_cookie': bool(self.get_cookie() and self.get_cookie() != "Your Cookie"),
            'proxy_enabled': self.proxy_enabled,
            'proxy_url': self.proxy_url
        }
