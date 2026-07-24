import requests
import json
import threading
import time
from datetime import datetime
import logging
from typing import Optional, Dict, List
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class Ledong:
    """抢票器类"""
    
    def __init__(self, thread_count: int = 5):
        """
        初始化抢票器
        
        Args:
            thread_count: 并发线程数，默认10个
        """
        self.thread_count = thread_count
        self.is_running = False
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        
        # 请求配置
        self.url = "https://stmember.styd.cn/v2/reserve/submit?"
        
        # 基础headers
        self.base_headers = {
            "Host": "stmember.styd.cn",
            "Connection": "keep-alive",
            "client-timezone": "+0800",
            "brand-code": "n9Lk2rX52Nz",
            "xweb_xhr": "1",
            "shop-id": "3691365947604836",
            "theme-compatible": "1",
            "mina-version": "independent",
            "Content-Type": "application/json",
            "app-id": "mina",
            "wx-token": "gVIsckNTWFUCsktsrkI5HrDqcfLglTft",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://servicewechat.com/wx28e6b769802e5485/3/page-frame.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,  q=0.9",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/132.0.0.0 Safari/537.36 "
                "MicroMessenger/7.0.20.1781(0x6700143B) "
                "NetType/WIFI "
                "MiniProgramEnv/Windows "
                "WindowsWechat/WMPF "
                "WindowsWechat(0x63090a13) "
                "UnifiedPCWindowsWechat(0xf2541923) "
                "XWEB/19823"
            )
        }
        
        # 基础payload
        self.base_payload = {
            "schedule_id": 0,
            "coach_id": 0,
            "course_id": 0,
            "seat": [],
            "consume_type": "wechat",
            "consume_id": "wechat",
            "current_reservation_num": 1,
            "reserve_type": "venues",
            "remark": "",
            "venues_id": "3692708846239935",
            "venues_date": "2026/07/01",
            "venues_site_time": [
                {
                    "site_id": 3692729935134806,
                    "site_name": "1号场",
                    "start_time": "18:00",
                    "start_timestamp": 1782900000,
                    "end_timestamp": 1782903600,
                    "end_time": "19:00",
                    "times": "1",
                    "price": "130"
                }
            ],
            "activity_id": 0
        }
        
        # 如果需要cookies
        self.cookies = {
            "acw_tc": "76b20f7917813716813476352ee9a040256bf5f5acd73910263119f965270c"
        }
    
    def update_token(self, new_token: str):
        """更新微信token"""
        self.base_headers["wx-token"] = new_token
        logger.info(f"Token已更新: {new_token[:20]}...")
    
    def update_venue_info(self, venue_id: str, date: str, site_id: int, 
                          site_name: str, start_time: str, end_time: str,
                          start_timestamp: int, end_timestamp: int, price: str):
        """更新场地信息"""
        self.base_payload["venues_id"] = venue_id
        self.base_payload["venues_date"] = date
        self.base_payload["venues_site_time"] = [
            {
                "site_id": site_id,
                "site_name": site_name,
                "start_time": start_time,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "end_time": end_time,
                "times": "1",
                "price": price
            }
        ]
        logger.info(f"场地信息已更新: {site_name} {start_time}-{end_time}")
    
    def submit_reservation(self, thread_id: int) -> Optional[Dict]:
        """
        提交预约请求
        
        Args:
            thread_id: 线程ID
            
        Returns:
            响应JSON或None
        """
        try:
            # 每个线程使用独立的session
            session = requests.Session()
            
            # 添加轻微随机延迟，避免所有请求同时到达
            time.sleep(random.uniform(0.001, 0.01))
            
            response = session.post(
                self.url,
                headers=self.base_headers,
                cookies=self.cookies,
                data=json.dumps(self.base_payload),
                timeout=3000,  # 3秒超时
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                with self.lock:
                    self.success_count += 1
                    logger.info(f"线程{thread_id} 请求成功!")
                    logger.info(f"响应: {json.dumps(result, ensure_ascii=False)}")
                return result
            else:
                with self.lock:
                    self.fail_count += 1
                    logger.warning(f"线程{thread_id} 请求失败, 状态码: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            with self.lock:
                self.fail_count += 1
                logger.error(f"线程{thread_id} 请求超时")
            return None
        except Exception as e:
            with self.lock:
                self.fail_count += 1
                logger.error(f"线程{thread_id} 请求异常: {str(e)}")
            return None
    
    def worker(self, thread_id: int):
        """工作线程函数"""
        logger.info(f"线程{thread_id} 启动，等待零点时刻...")
        
        # 等待到零点
        while self.is_running:
            now = datetime.now()
            # 检查是否为零点零分零秒 (精确到秒)
            if now.hour == 0 and now.minute == 0 and now.second == 0:
                logger.info(f"线程{thread_id} 到达零点，开始抢票!")
                self.submit_reservation(thread_id)
                # 抢完后等待1秒，避免重复提交
                time.sleep(1)
            else:
                # 计算到下一个零点的秒数
                next_midnight = datetime(now.year, now.month, now.day + 1, 0, 0, 0)
                wait_seconds = (next_midnight - now).total_seconds()
                
                # 如果还没到零点，等待一段时间再检查
                if wait_seconds > 60:
                    # 每10秒检查一次，减少CPU占用
                    time.sleep(10)
                else:
                    # 接近零点时，每秒检查一次
                    time.sleep(0.001)
    
    def start_grabbing(self):
        """启动抢票"""
        if self.is_running:
            logger.warning("抢票已经在运行中!")
            return
        
        self.is_running = True
        self.success_count = 0
        self.fail_count = 0
        
        logger.info(f"启动抢票，线程数: {self.thread_count}")
        
        # 创建并启动线程
        threads = []
        for i in range(self.thread_count):
            thread = threading.Thread(
                target=self.worker,
                args=(i,),
                name=f"Grabber-{i}",
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # 主线程监控
        try:
            while self.is_running:
                with self.lock:
                    logger.info(f"状态: 成功={self.success_count}, 失败={self.fail_count}, "
                              f"总计={self.success_count + self.fail_count}")
                
                # 检查是否所有线程还在运行
                alive_count = sum(1 for t in threads if t.is_alive())
                if alive_count == 0 and self.is_running:
                    logger.warning("所有线程已停止，重新启动...")
                    threads = []
                    for i in range(self.thread_count):
                        thread = threading.Thread(
                            target=self.worker,
                            args=(i,),
                            name=f"Grabber-{i}",
                            daemon=True
                        )
                        threads.append(thread)
                        thread.start()
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止抢票...")
            self.stop_grabbing()
    
    def stop_grabbing(self):
        """停止抢票"""
        self.is_running = False
        logger.info("抢票已停止")
    
    def test_submit(self):
        """测试提交（不等待零点，立即执行一次）"""
        logger.info("执行测试提交...")
        result = self.submit_reservation(0)
        if result:
            logger.info(f"测试成功: {json.dumps(result, ensure_ascii=False)}")
        else:
            logger.error("测试失败")
        return result


def main():
    """主函数"""
    # 创建抢票器实例
    grabber = Ledong(thread_count=10)  # 10个线程并发
    
    # 如果需要更新场地信息，可以在这里配置
    # grabber.update_venue_info(
    #     venue_id="3692708846239935",
    #     date="2026/06/24",
    #     site_id=3692729935134806,
    #     site_name="1号场",
    #     start_time="18:00",
    #     end_time="19:00",
    #     start_timestamp=1782295200,
    #     end_timestamp=1782298800,
    #     price="130"
    # )
    
    # 如果需要更新token
    # grabber.update_token("新的token")
    
    # 先测试一下
    # grabber.test_submit()
    
    # 开始抢票（等待零点）
    try:
        grabber.start_grabbing()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    finally:
        grabber.stop_grabbing()


if __name__ == "__main__":
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()