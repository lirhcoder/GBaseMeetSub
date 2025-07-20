"""简单的Flask测试应用"""
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>测试页面</title>
    </head>
    <body>
        <h1>Flask测试页面</h1>
        <p>如果您能看到这个页面，说明Flask正在工作</p>
        <p>当前工作目录: """ + os.getcwd() + """</p>
        <p>脚本目录: """ + os.path.dirname(os.path.abspath(__file__)) + """</p>
        <h2>目录检查:</h2>
        <ul>
            <li>templates目录存在: """ + str(os.path.exists('templates')) + """</li>
            <li>static目录存在: """ + str(os.path.exists('static')) + """</li>
            <li>static/css目录存在: """ + str(os.path.exists('static/css')) + """</li>
            <li>static/js目录存在: """ + str(os.path.exists('static/js')) + """</li>
        </ul>
    </body>
    </html>
    """

if __name__ == '__main__':
    print(f"启动测试服务器...")
    print(f"当前目录: {os.getcwd()}")
    print(f"访问: http://localhost:5001")
    app.run(debug=True, port=5001)