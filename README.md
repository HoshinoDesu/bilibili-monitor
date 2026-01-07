# Bilibili 视频热度监视器

一个用于监控和可视化 Bilibili 视频数据的完整解决方案，支持多视频对比、实时数据更新和现代化的Web界面。

## ✨ 功能特性

- 📊 **实时数据监控** - 定时抓取视频播放量、点赞、投币、收藏、转发和在线人数
- 📈 **可视化图表** - 基于 Chart.js 的交互式折线图，支持图例筛选和自适应Y轴
- 🔄 **多视频对比** - 同时对比多个视频的各项指标
- 🎨 **现代化UI** - 扁平化设计，支持明亮/暗黑主题切换
- ⚡ **自动刷新** - 每10秒自动更新数据，无需手动刷新
- 💾 **数据持久化** - SQLite数据库存储，支持数据删除和时间范围筛选
- 🛠️ **灵活配置** - 支持自定义监控间隔和视频列表

## 🖼️ 界面预览

### 数据监控
实时查看单个视频的各项数据趋势，支持自定义时间范围和数据点数量。

### 多视频对比
选择多个视频进行指标对比，支持播放量、点赞、投币、收藏、转发和在线人数等维度。

### 设置管理
配置监控间隔、管理监控列表、清理历史数据。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 推荐使用虚拟环境

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/HoshinoDesu/bilibili-monitor.git
cd bilibili-monitor
```

2. **创建虚拟环境**
```bash
python -m venv .venv
```

3. **激活虚拟环境**

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **配置监控列表**

编辑 `monitor.list` 文件，添加要监控的视频BV号（每行一个）：
```
BV1iMvXBhEbe
BV1A6i4BqEn2
BV12qiMBdEcC
```

6. **启动服务**

启动Web服务：
```bash
python app.py
```

启动数据监控（新终端窗口）：
```bash
python monitor.py
```

7. **访问界面**

打开浏览器访问：http://localhost:5000

## 📁 项目结构

```
bilibili-monitor/
├── app.py                 # Flask Web应用
├── monitor.py             # 数据监控脚本
├── bilibili_api.py        # B站API接口
├── database.py            # 数据库操作
├── config.json            # 配置文件
├── monitor.list           # 监控视频列表
├── requirements.txt       # Python依赖
├── templates/
│   └── index.html        # Web界面
└── data.db               # SQLite数据库（自动生成）
```

## ⚙️ 配置说明

### config.json

```json
{
    "fetch_interval_minutes": 10,
    "api_port": 5000
}
```

- `fetch_interval_minutes`: 数据抓取间隔（分钟）
- `api_port`: Web服务端口

### monitor.list

每行一个BV号，支持 `#` 注释：

```
# 主要监控视频
BV1iMvXBhEbe

# 对比视频
BV1A6i4BqEn2
BV12qiMBdEcC
```

## 💻 命令行使用

### 监控脚本选项

```bash
python monitor.py -h              # 查看帮助
python monitor.py --once          # 执行一次抓取后退出
python monitor.py -t 5            # 每5分钟抓取一次
python monitor.py -n 10           # 抓取10次后退出
python monitor.py -t 5 -n 10      # 每5分钟抓取一次，共10次
```

## 📊 数据说明

系统抓取并存储以下数据：

| 字段 | 说明 |
|------|------|
| view | 播放量 |
| like | 点赞数 |
| coin | 投币数 |
| favorite | 收藏数 |
| share | 转发数 |
| online | 实时在线人数 |
| danmaku | 弹幕数 |
| reply | 评论数 |
| timestamp | 抓取时间 |

## 🎨 界面功能

### 数据监控页
- 选择视频和数据点数量
- 交互式折线图展示各项指标
- 点击图例隐藏/显示特定指标
- 自动调整Y轴范围以优化显示
- 自动每10秒刷新数据

### 多视频对比页
- 选择多个视频进行对比
- 切换不同指标维度
- 支持所有数据指标的对比
- 图例点击切换视频显示

### 设置页
- 修改监控间隔
- 编辑监控视频列表
- 删除指定视频或时间范围的数据

## 🔧 技术栈

### 后端
- **Flask** - Web框架
- **SQLite** - 数据库
- **Requests** - HTTP请求
- **Schedule** - 定时任务

### 前端
- **Chart.js 4.4.0** - 图表库
- **原生JavaScript** - 无框架依赖
- **CSS Variables** - 主题系统

## 📝 开发说明

### API接口

#### 获取单视频数据
```
GET /api/video/<bv_id>/stats?limit=50
```

#### 多视频对比数据
```
POST /api/videos/compare
Content-Type: application/json

{
    "bv_ids": ["BV1iMvXBhEbe", "BV1A6i4BqEn2"]
}
```

#### 获取视频信息
```
GET /api/videos/info
```

#### 获取配置
```
GET /api/config
```

#### 更新配置
```
POST /api/config
Content-Type: application/json

{
    "fetch_interval_minutes": 10,
    "monitor_list": ["BV1iMvXBhEbe"]
}
```

#### 删除数据
```
DELETE /api/data/delete?bv_id=xxx&start_time=xxx&end_time=xxx
```

## 🐛 常见问题

### 1. 抓取失败

**原因**：网络问题或B站API限制

**解决**：
- 检查网络连接
- 适当增加抓取间隔
- 确认BV号正确

### 2. 图表不显示

**原因**：没有数据或浏览器兼容性

**解决**：
- 先运行监控脚本抓取数据
- 使用现代浏览器（Chrome/Edge/Firefox）
- 检查浏览器控制台错误

### 3. 端口占用

**原因**：5000端口被占用

**解决**：
- 修改 `config.json` 中的 `api_port`
- 或关闭占用端口的程序

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题或建议，欢迎通过 Issues 反馈。

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！
