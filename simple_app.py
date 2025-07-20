"""最简单的Flask应用 - 用于测试"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Simple App Home Page</h1>'

@app.route('/test')
def test():
    return '<h1>Test Route Works!</h1>'

if __name__ == '__main__':
    print("\n" + "="*50)
    print("运行最简单的Flask应用")
    print("="*50)
    print("访问: http://localhost:6000/")
    print("访问: http://localhost:6000/test")
    print("="*50 + "\n")
    
    # 使用不同的端口避免冲突
    app.run(debug=True, port=6000, host='127.0.0.1')