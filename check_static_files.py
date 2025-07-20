"""检查静态文件是否存在"""
import os

def check_files():
    print("检查静态文件...")
    
    # 获取脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查的文件列表
    files_to_check = [
        'static/css/style.css',
        'static/js/main.js',
        'templates/index.html',
        'app.py',
        'src/__init__.py'
    ]
    
    missing_files = []
    
    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - 缺失!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n缺失 {len(missing_files)} 个文件")
        print("请运行: git pull origin main")
    else:
        print("\n所有文件都存在!")

if __name__ == "__main__":
    check_files()