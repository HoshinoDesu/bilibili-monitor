"""
Bilibili API 接口封装
用于获取视频数据
"""
import requests
import json
from datetime import datetime


class BilibiliAPI:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
    
    def get_video_info(self, bv_id):
        """
        获取视频详细信息
        
        Args:
            bv_id: 视频BV号
            
        Returns:
            dict: 包含视频各项数据的字典
        """
        try:
            # 获取视频基础信息
            url = f'https://api.bilibili.com/x/web-interface/view'
            params = {'bvid': bv_id}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] != 0:
                print(f"API错误: {data.get('message', '未知错误')}")
                return None
            
            video_data = data['data']
            stat = video_data['stat']
            
            result = {
                'bv_id': bv_id,
                'title': video_data['title'],
                'view': stat.get('view', 0),        # 播放量
                'like': stat.get('like', 0),        # 点赞
                'coin': stat.get('coin', 0),        # 投币
                'favorite': stat.get('favorite', 0), # 收藏
                'share': stat.get('share', 0),      # 转发
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 尝试获取实时观看人数（需要从播放页面获取）
            try:
                online = self.get_online_count(bv_id)
                result['online'] = online
            except Exception as e:
                print(f"获取实时观看人数失败: {e}")
                result['online'] = 0
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except Exception as e:
            print(f"解析数据失败: {e}")
            return None
    
    def get_online_count(self, bv_id):
        """
        获取实时观看人数
        
        Args:
            bv_id: 视频BV号
            
        Returns:
            int: 实时观看人数
        """
        try:
            # 获取aid
            url = f'https://api.bilibili.com/x/web-interface/view'
            params = {'bvid': bv_id}
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            
            if data['code'] != 0:
                return 0
                
            aid = data['data']['aid']
            cid = data['data']['cid']
            
            # 获取在线人数
            online_url = 'https://api.bilibili.com/x/player/online/total'
            online_params = {
                'aid': aid,
                'cid': cid,
                'bvid': bv_id
            }
            
            online_response = requests.get(online_url, params=online_params, headers=self.headers, timeout=10)
            online_data = online_response.json()
            
            if online_data['code'] == 0 and 'data' in online_data:
                return online_data['data'].get('total', 0)
            
            return 0
            
        except Exception as e:
            print(f"获取在线人数异常: {e}")
            return 0


if __name__ == '__main__':
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Bilibili视频数据抓取工具')
    parser.add_argument('-bv', '--bvid', type=str, help='视频BV号', required=False)
    
    args = parser.parse_args()
    
    api = BilibiliAPI()
    
    # 如果提供了BV号，抓取该视频
    if args.bvid:
        bv_id = args.bvid
        print(f"正在抓取视频: {bv_id}")
        info = api.get_video_info(bv_id)
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print("获取视频信息失败")
    else:
        # 没有参数时使用默认测试
        print("用法: python bilibili_api.py -bv BV1JHLUz4EUy")
        print("\n使用默认测试BV号...")
        info = api.get_video_info('BV1JHLUz4EUy')
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
