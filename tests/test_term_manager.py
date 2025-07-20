"""术语管理模块测试"""
import unittest
import tempfile
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.term_manager import TermManager

class TestTermManager(unittest.TestCase):
    def setUp(self):
        """创建临时文件用于测试"""
        self.temp_dir = tempfile.mkdtemp()
        self.term_file = os.path.join(self.temp_dir, "test_terms.json")
        self.log_file = os.path.join(self.temp_dir, "test_log.json")
        self.manager = TermManager(self.term_file, self.log_file)
    
    def test_add_correction(self):
        """测试添加纠正"""
        self.manager.add_correction("AI", "人工知能", "技術会議", 0.9)
        
        # 验证术语已添加
        term = self.manager.get_term("AI")
        self.assertIsNotNone(term)
        self.assertEqual(term["correct"], "人工知能")
        self.assertEqual(term["frequency"], 1)
        self.assertEqual(term["confidence"], 0.9)
        
    def test_frequency_update(self):
        """测试频率更新"""
        self.manager.add_correction("AI", "人工知能", "会議1", 0.8)
        self.manager.add_correction("AI", "人工知能", "会議2", 0.9)
        
        term = self.manager.get_term("AI")
        self.assertEqual(term["frequency"], 2)
        self.assertEqual(term["confidence"], 0.9)  # 应该是最高值
        self.assertEqual(len(term["contexts"]), 2)
    
    def test_high_frequency_terms(self):
        """测试高频术语获取"""
        # 添加不同频率的术语
        for i in range(5):
            self.manager.add_correction("高频词", "高頻度単語", f"context{i}")
        
        for i in range(2):
            self.manager.add_correction("低频词", "低頻度単語", f"context{i}")
        
        high_freq = self.manager.get_high_frequency_terms(min_frequency=3)
        self.assertIn("高频词", high_freq)
        self.assertNotIn("低频词", high_freq)
    
    def test_persistence(self):
        """测试持久化"""
        self.manager.add_correction("テスト", "测试", "単体テスト")
        
        # 创建新实例，应该能读取之前的数据
        new_manager = TermManager(self.term_file, self.log_file)
        term = new_manager.get_term("テスト")
        self.assertIsNotNone(term)
        self.assertEqual(term["correct"], "测试")

if __name__ == "__main__":
    unittest.main()