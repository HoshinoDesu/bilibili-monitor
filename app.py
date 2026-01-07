"""
Flask Web服务
提供API接口和前端页面
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from database import Database
import json

app = Flask(__name__)
CORS(app)

# 初始化数据库
db = Database()

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/video/<bv_id>/stats')
def get_video_stats(bv_id):
    """
    获取视频历史统计数据
    
    Args:
        bv_id: 视频BV号
        
    Query params:
        limit: 返回的数据条数，默认100
        
    Returns:
        JSON格式的统计数据
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        stats = db.get_video_stats(bv_id, limit)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': str(e),
            'data': None
        }), 500


@app.route('/api/video/<bv_id>/latest')
def get_latest_data(bv_id):
    """
    获取视频最新数据
    
    Args:
        bv_id: 视频BV号
        
    Returns:
        JSON格式的最新数据
    """
    try:
        data = db.get_latest_data(bv_id)
        
        if data:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': data
            })
        else:
            return jsonify({
                'code': 404,
                'message': 'No data found',
                'data': None
            }), 404
            
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': str(e),
            'data': None
        }), 500


@app.route('/api/videos')
def get_all_videos():
    """
    获取所有已监控的视频BV号
    
    Returns:
        JSON格式的BV号列表
    """
    try:
        bv_ids = db.get_all_bv_ids()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': bv_ids
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': str(e),
            'data': None
        }), 500


@app.route('/api/videos/info')
def get_videos_info():
    """
    获取所有有数据的视频信息（含标题）
    
    Returns:
        JSON格式的视频信息列表
    """
    try:
        bv_ids = db.get_all_bv_ids()
        videos_info = []
        
        for bv_id in bv_ids:
            latest = db.get_latest_data(bv_id)
            if latest:
                videos_info.append({
                    'bv_id': bv_id,
                    'title': latest.get('title', bv_id)
                })
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': videos_info
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': str(e),
            'data': None
        }), 500


@app.route('/api/data/delete', methods=['POST', 'DELETE'])
def delete_data():
    """
    删除指定视频或时间段的数据
    
    Query Parameters (for DELETE):
        bv_id: 视频BV号（可选）
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
    
    Request Body (for POST):
        {
            "bv_id": "BV1xx411c7XZ",  // 可选，指定视频
            "start_date": "2026-01-01",  // 可选，开始日期
            "end_date": "2026-01-07"     // 可选，结束日期
        }
    
    Returns:
        JSON格式的操作结果
    """
    try:
        # 支持DELETE方法的查询参数和POST方法的JSON body
        if request.method == 'DELETE':
            bv_id = request.args.get('bv_id')
            start_date = request.args.get('start_time')
            end_date = request.args.get('end_time')
        else:
            data = request.get_json()
            bv_id = data.get('bv_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
        
        deleted_count = db.delete_video_data(bv_id, start_date, end_date)
        
        return jsonify({
            'code': 0,
            'message': f'成功删除 {deleted_count} 条数据',
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500


@app.route('/api/config')
def get_config():
    """
    获取配置信息
    
    Returns:
        JSON格式的配置
    """
    # 重新加载配置以获取最新值
    with open('config.json', 'r', encoding='utf-8') as f:
        current_config = json.load(f)
    
    # 读取监控列表
    monitor_list = []
    try:
        with open('monitor.list', 'r', encoding='utf-8') as f:
            for line in f:
                bv = line.strip()
                if bv and not bv.startswith('#'):
                    monitor_list.append(bv)
    except FileNotFoundError:
        monitor_list = [current_config.get('bv_id', 'BV1xx411c7XZ')]
    
    current_config['monitor_list'] = monitor_list
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': current_config
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """
    更新配置信息
    
    Request Body:
        {
            "fetch_interval_minutes": 10,
            "monitor_list": ["BV1xx411c7XZ", "BV2yy222d8YY"]
        }
    
    Returns:
        JSON格式的操作结果
    """
    try:
        data = request.get_json()
        
        # 加载当前配置
        with open('config.json', 'r', encoding='utf-8') as f:
            current_config = json.load(f)
        
        # 更新抓取间隔
        if 'fetch_interval_minutes' in data:
            interval = int(data['fetch_interval_minutes'])
            if interval < 1:
                return jsonify({
                    'code': -1,
                    'message': '抓取间隔必须大于0',
                    'data': None
                }), 400
            current_config['fetch_interval_minutes'] = interval
        
        # 保存配置
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(current_config, f, indent=2, ensure_ascii=False)
        
        # 更新监控列表
        if 'monitor_list' in data:
            monitor_list = data['monitor_list']
            if not isinstance(monitor_list, list):
                return jsonify({
                    'code': -1,
                    'message': '监控列表必须是数组',
                    'data': None
                }), 400
            
            # 写入 monitor.list
            with open('monitor.list', 'w', encoding='utf-8') as f:
                f.write('# Bilibili视频监控列表\n')
                f.write('# 每行一个BV号，# 开头的行为注释\n\n')
                for bv in monitor_list:
                    if bv and bv.strip():
                        f.write(bv.strip() + '\n')
        
        return jsonify({
            'code': 0,
            'message': '配置更新成功',
            'data': current_config
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'配置更新失败: {str(e)}',
            'data': None
        }), 500


@app.route('/api/videos/compare')
def compare_videos():
    """
    获取多个视频的对比数据
    
    Query params:
        bv_ids: 逗号分隔的BV号列表，如 BV1,BV2,BV3
        limit: 返回的数据条数，默认50
    
    Returns:
        JSON格式的对比数据
    """
    try:
        bv_ids_str = request.args.get('bv_ids', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not bv_ids_str:
            return jsonify({
                'code': -1,
                'message': '请提供BV号列表',
                'data': None
            }), 400
        
        bv_ids = [bv.strip() for bv in bv_ids_str.split(',') if bv.strip()]
        
        # 获取每个视频的数据
        result = {}
        for bv_id in bv_ids:
            stats = db.get_video_stats(bv_id, limit)
            result[bv_id] = stats
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'code': -1,
            'message': str(e),
            'data': None
        }), 500


if __name__ == '__main__':
    port = config.get('api_port', 5000)
    print(f"Flask服务启动在端口 {port}")
    print(f"请访问: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
