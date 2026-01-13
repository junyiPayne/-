# Gunicorn 配置文件
# 用于生产环境部署

import multiprocessing
import os

# 服务器配置
bind = os.environ.get('BIND', '0.0.0.0:5001')
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# 日志配置
accesslog = os.environ.get('ACCESS_LOG', 'logs/access.log')
errorlog = os.environ.get('ERROR_LOG', 'logs/error.log')
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'bs-system'

# 服务器钩子
def on_starting(server):
    """服务器启动时的钩子"""
    server.log.info("BS系统正在启动...")

def on_reload(server):
    """重载时的钩子"""
    server.log.info("BS系统正在重载...")

def when_ready(server):
    """服务器就绪时的钩子"""
    server.log.info("BS系统已就绪，开始接受连接")

def worker_int(worker):
    """工作进程中断时的钩子"""
    worker.log.info("工作进程收到中断信号")

def pre_fork(server, worker):
    """fork工作进程前的钩子"""
    pass

def post_fork(server, worker):
    """fork工作进程后的钩子"""
    server.log.info(f"工作进程 {worker.pid} 已启动")

def post_worker_init(worker):
    """工作进程初始化后的钩子"""
    worker.log.info(f"工作进程 {worker.pid} 初始化完成")

def worker_abort(worker):
    """工作进程异常退出时的钩子"""
    worker.log.info(f"工作进程 {worker.pid} 异常退出")

# 性能调优
max_requests = 1000  # 每个工作进程处理的最大请求数，达到后重启工作进程
max_requests_jitter = 50  # 随机抖动，避免所有工作进程同时重启
preload_app = False  # 预加载应用，可以提高性能但会增加内存使用

# SSL配置（如果使用HTTPS，取消注释并配置）
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'
