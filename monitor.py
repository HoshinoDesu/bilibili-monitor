"""
定时监控程序
定时抓取Bilibili视频数据并存储到数据库
"""
import schedule
import time
import json
import argparse
from datetime import datetime
from bilibili_api import BilibiliAPI
from database import Database


class VideoMonitor:
    def __init__(self, config_file='config.json', list_file='monitor.list'):
        # 加载配置
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.interval = self.config.get('fetch_interval_minutes', 10)
        self.list_file = list_file
        
        # 初始化API和数据库
        self.api = BilibiliAPI()
        self.db = Database()
        
        # 读取监控列表
        self.bv_list = self.load_monitor_list()
        
        print("=" * 60)
        print("Bilibili视频热度监视器")
        print("=" * 60)
        print(f"监控视频数量: {len(self.bv_list)}")
        for bv in self.bv_list:
            print(f"  - {bv}")
        print(f"抓取间隔: {self.interval} 分钟")
        print("=" * 60)
    
    def load_monitor_list(self):
        """从 monitor.list 文件读取BV号列表"""
        import os
        
        if not os.path.exists(self.list_file):
            # 如果文件不存在，创建默认文件
            with open(self.list_file, 'w', encoding='utf-8') as f:
                f.write('# Bilibili视频监控列表\n')
                f.write('# 每行一个BV号，# 开头的行为注释\n')
                f.write('# 示例：\n')
                f.write('# BV1xx411c7XZ\n')
            return []
        
        bv_list = []
        with open(self.list_file, 'r', encoding='utf-8') as f:
            for line in f:
                bv = line.strip()
                if bv and not bv.startswith('#'):  # 忽略空行和注释
                    bv_list.append(bv)
        
        return bv_list
    
    def fetch_and_save(self):
        """抓取并保存所有视频数据"""
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取数据...")
            
            # 重新加载监控列表（以支持动态更新）
            self.bv_list = self.load_monitor_list()
            
            # 遍历所有BV号
            for idx, bv_id in enumerate(self.bv_list, 1):
                print(f"\n[{idx}/{len(self.bv_list)}] 抓取 {bv_id}...")
                
                # 获取视频信息
                video_info = self.api.get_video_info(bv_id)
                
                if video_info:
                    # 显示数据
                    print(f"  标题: {video_info.get('title', 'N/A')}")
                    print(f"  播放: {video_info.get('view', 0):,} | "
                          f"点赞: {video_info.get('like', 0):,} | "
                          f"投币: {video_info.get('coin', 0):,}")
                    
                    # 处理在线人数（可能是字符串或整数）
                    online = video_info.get('online', 0)
                    online_str = str(online) if isinstance(online, str) else f"{online:,}"
                    print(f"  收藏: {video_info.get('favorite', 0):,} | "
                          f"转发: {video_info.get('share', 0):,} | "
                          f"在线: {online_str}")
                    
                    # 保存到数据库
                    success = self.db.insert_video_data(video_info)
                    
                    if success:
                        print(f"  ✓ 数据保存成功")
                    else:
                        print(f"  ✗ 数据保存失败")
                else:
                    print(f"  ✗ 获取视频信息失败")
                
                # 避免请求过快
                if idx < len(self.bv_list):
                    time.sleep(1)
                
        except Exception as e:
            print(f"✗ 发生错误: {e}")
    
    def start(self):
        """启动监控"""
        # 立即执行一次
        self.fetch_and_save()
        
        # 设置定时任务
        schedule.every(self.interval).minutes.do(self.fetch_and_save)
        
        print(f"\n监控已启动，每 {self.interval} 分钟抓取一次数据")
        next_time = datetime.now().timestamp() + self.interval * 60
        next_time_str = datetime.fromtimestamp(next_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"⏰ 下次抓取时间: {next_time_str}")
        print("按 Ctrl+C 停止监控\n")
        
        # 运行调度器
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n监控已停止")
    
    def run_once(self):
        """仅运行一次（用于测试）"""
        self.fetch_and_save()
    
    def run_continuous(self, count):
        """连续抓取指定次数，无时间间隔"""
        print(f"\n📊 连续抓取模式，共 {count} 次")
        print("按 Ctrl+C 可提前停止\n")
        
        try:
            for i in range(count):
                print(f"\n{'='*60}")
                print(f"第 {i+1}/{count} 次抓取")
                print(f"{'='*60}")
                
                self.fetch_and_save()
                
                # 如果不是最后一次，等待一下避免请求过快
                if i < count - 1:
                    print(f"\n⏳ 等待2秒后继续...")
                    time.sleep(2)
            
            print(f"\n✅ 已完成全部 {count} 次抓取，程序退出")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  已手动停止（已完成 {i+1}/{count} 次抓取）")
    
    def run_continuous(self, count):
        """连续抓取指定次数，无时间间隔"""
        print(f"\n📊 连续抓取模式，共 {count} 次")
        print("按 Ctrl+C 可提前停止\n")
        
        try:
            for i in range(count):
                print(f"\n{'='*60}")
                print(f"第 {i+1}/{count} 次抓取")
                print(f"{'='*60}")
                
                self.fetch_and_save()
                
                # 如果不是最后一次，等待一下避免请求过快
                if i < count - 1:
                    print(f"\n⏳ 等待2秒后继续...")
                    time.sleep(2)
            
            print(f"\n✅ 已完成全部 {count} 次抓取，程序退出")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  已手动停止（已完成 {i+1}/{count} 次抓取）")
    
    def run_with_limit(self, interval, count):
        """运行指定次数后退出"""
        print(f"\n开始定时抓取，间隔 {interval} 分钟，共 {count} 次")
        print("按 Ctrl+C 可提前停止\n")
        
        try:
            for i in range(count):
                print(f"\n{'='*60}")
                print(f"第 {i+1}/{count} 次抓取")
                print(f"{'='*60}")
                
                self.fetch_and_save()
                
                # 如果不是最后一次，等待下次抓取
                if i < count - 1:
                    next_time = datetime.now().timestamp() + interval * 60
                    next_time_str = datetime.fromtimestamp(next_time).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n⏰ 下次抓取时间: {next_time_str}")
                    print(f"等待 {interval} 分钟...")
                    time.sleep(interval * 60)
            
            print(f"\n✅ 已完成全部 {count} 次抓取，程序退出")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  已手动停止（已完成 {i+1}/{count} 次抓取）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Bilibili视频热度监视器 - 定时抓取视频数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  %(prog)s                     # 使用配置文件中的间隔循环抓取
  %(prog)s -t 5                # 每5分钟抓取一次，循环运行
  %(prog)s -n 3                # 连续抓取3次后退出（无时间间隔）
  %(prog)s -t 10 -n 3          # 每10分钟抓取一次，共3次后退出
  %(prog)s --once              # 立即抓取一次后退出
        ''')
    
    parser.add_argument('-t', '--interval', type=int, metavar='分钟',
                        help='设置抓取间隔（分钟），如: -t 5 表示每5分钟抓取一次')
    parser.add_argument('-n', '--count', type=int, metavar='次数',
                        help='设置抓取次数，单独使用时连续抓取，配合-t使用时按间隔抓取')
    parser.add_argument('--once', action='store_true',
                        help='立即抓取一次后退出')
    
    args = parser.parse_args()
    
    monitor = VideoMonitor()
    
    # 处理命令行参数
    if args.once:
        # 立即执行一次
        print("📌 单次执行模式")
        monitor.run_once()
    elif args.count and not args.interval:
        # 仅有 -n 参数：连续抓取多次，无时间间隔
        monitor.run_continuous(args.count)
    elif args.interval and args.count:
        # 同时有 -t 和 -n：按间隔抓取指定次数
        print(f"📊 定时抓取模式: 每 {args.interval} 分钟抓取一次，共抓取 {args.count} 次")
        monitor.run_with_limit(args.interval, args.count)
    elif args.interval:
        # 仅有 -t 参数：按间隔循环抓取
        print(f"🔄 循环抓取模式: 每 {args.interval} 分钟抓取一次，持续运行")
        monitor.interval = args.interval
        monitor.start()
    else:
        # 默认模式：使用配置文件的设置
        monitor.start()


if __name__ == '__main__':
    main()
