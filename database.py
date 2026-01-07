"""
数据库操作模块
使用SQLite存储视频数据
"""
import sqlite3
from datetime import datetime
import os


class Database:
    def __init__(self, db_path='data.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建视频数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bv_id TEXT NOT NULL,
                title TEXT,
                view INTEGER DEFAULT 0,
                like INTEGER DEFAULT 0,
                coin INTEGER DEFAULT 0,
                favorite INTEGER DEFAULT 0,
                share INTEGER DEFAULT 0,
                online INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bv_timestamp 
            ON video_stats(bv_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print("数据库初始化完成")
    
    def insert_video_data(self, data):
        """
        插入视频数据
        
        Args:
            data: 包含视频数据的字典
            
        Returns:
            bool: 是否插入成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO video_stats 
                (bv_id, title, view, like, coin, favorite, share, online, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('bv_id'),
                data.get('title'),
                data.get('view', 0),
                data.get('like', 0),
                data.get('coin', 0),
                data.get('favorite', 0),
                data.get('share', 0),
                data.get('online', 0),
                data.get('timestamp')
            ))
            
            conn.commit()
            conn.close()
            print(f"数据插入成功: {data.get('timestamp')}")
            return True
            
        except Exception as e:
            print(f"数据插入失败: {e}")
            return False
    
    def get_video_stats(self, bv_id, limit=100):
        """
        获取视频历史数据
        
        Args:
            bv_id: 视频BV号
            limit: 返回的数据条数
            
        Returns:
            list: 历史数据列表
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM video_stats
                WHERE bv_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (bv_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表并反转顺序（时间从早到晚）
            result = [dict(row) for row in rows]
            result.reverse()
            
            return result
            
        except Exception as e:
            print(f"查询数据失败: {e}")
            return []
    
    def get_all_bv_ids(self):
        """
        获取所有已监控的BV号
        
        Returns:
            list: BV号列表
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT bv_id FROM video_stats
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [row['bv_id'] for row in rows]
            
        except Exception as e:
            print(f"查询BV号列表失败: {e}")
            return []
    
    def get_latest_data(self, bv_id):
        """
        获取指定视频的最新数据
        
        Args:
            bv_id: 视频BV号
            
        Returns:
            dict: 最新数据
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM video_stats
                WHERE bv_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (bv_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            print(f"查询最新数据失败: {e}")
            return None
    
    def clear_old_data(self, days=30):
        """
        清理指定天数之前的旧数据
        
        Args:
            days: 保留最近多少天的数据
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM video_stats
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"清理了 {deleted_count} 条旧数据")
            return deleted_count
            
        except Exception as e:
            print(f"清理旧数据失败: {e}")
            return 0
    
    def delete_video_data(self, bv_id=None, start_date=None, end_date=None):
        """
        删除指定条件的数据
        
        Args:
            bv_id: 视频BV号，None表示所有视频
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            int: 删除的记录数
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if bv_id:
                conditions.append('bv_id = ?')
                params.append(bv_id)
            
            if start_date:
                conditions.append("date(timestamp) >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("date(timestamp) <= ?")
                params.append(end_date)
            
            if not conditions:
                # 如果没有任何条件，拒绝删除（安全考虑）
                return 0
            
            where_clause = ' AND '.join(conditions)
            sql = f'DELETE FROM video_stats WHERE {where_clause}'
            
            cursor.execute(sql, params)
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"删除了 {deleted_count} 条数据")
            return deleted_count
            
        except Exception as e:
            print(f"删除数据失败: {e}")
            return 0


if __name__ == '__main__':
    # 测试代码
    db = Database()
    
    # 测试插入数据
    test_data = {
        'bv_id': 'BV1xx411c7XZ',
        'title': '测试视频',
        'view': 10000,
        'like': 500,
        'coin': 200,
        'favorite': 300,
        'share': 100,
        'online': 50,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    db.insert_video_data(test_data)
    
    # 测试查询数据
    stats = db.get_video_stats('BV1xx411c7XZ', limit=10)
    print(f"查询到 {len(stats)} 条数据")
