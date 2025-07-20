"""测试导入是否有问题"""
import sys
import os

print("Python路径:")
for p in sys.path:
    print(f"  {p}")

print("\n当前目录:", os.getcwd())
print("\n尝试导入模块...")

try:
    from src.main_pipeline import SpeechProcessingPipeline
    print("✓ 成功导入 SpeechProcessingPipeline")
except Exception as e:
    print(f"✗ 导入失败: {e}")

try:
    from src.term_manager import TermManager
    print("✓ 成功导入 TermManager")
except Exception as e:
    print(f"✗ 导入失败: {e}")

print("\n检查src目录:")
if os.path.exists('src'):
    print("src目录存在，内容:")
    for f in os.listdir('src'):
        print(f"  {f}")
else:
    print("src目录不存在！")