"""术语修正模块 - 基于术语库进行文本修正"""
from typing import List, Tuple, Dict
import re
from pygtrie import StringTrie
from .term_manager import TermManager

class TermCorrector:
    def __init__(self, term_manager: TermManager):
        self.term_manager = term_manager
        self._build_trie()
        
    def _build_trie(self):
        """构建Trie树以提高匹配效率"""
        self.trie = StringTrie()
        terms = self.term_manager.get_all_terms()
        for original, info in terms.items():
            self.trie[original] = info["correct"]
    
    def correct_text(self, text: str, record_corrections: bool = True) -> Tuple[str, List[Dict]]:
        """修正文本中的术语
        
        Args:
            text: 待修正的文本
            record_corrections: 是否记录修正（用于学习）
            
        Returns:
            (修正后的文本, 修正记录列表)
        """
        corrections = []
        corrected_text = text
        
        # 使用词边界进行匹配，避免部分匹配
        terms = self.term_manager.get_all_terms()
        
        # 按长度降序排序，优先匹配长词
        sorted_terms = sorted(terms.keys(), key=len, reverse=True)
        
        for original in sorted_terms:
            term_info = terms[original]
            correct = term_info["correct"]
            
            # 使用正则表达式进行全词匹配
            pattern = r'\b' + re.escape(original) + r'\b'
            
            if re.search(pattern, corrected_text):
                # 记录修正
                corrections.append({
                    "original": original,
                    "correct": correct,
                    "position": [(m.start(), m.end()) 
                               for m in re.finditer(pattern, corrected_text)]
                })
                
                # 执行替换
                corrected_text = re.sub(pattern, correct, corrected_text)
                
                # 如果需要记录，且这是新的修正
                if record_corrections and original not in terms:
                    self.term_manager.add_correction(
                        original, correct, 
                        context=text[:50],  # 保存部分上下文
                        confidence=0.8
                    )
        
        return corrected_text, corrections
    
    def suggest_corrections(self, text: str, threshold: float = 0.7) -> List[Dict]:
        """建议可能的修正（不直接修改）"""
        suggestions = []
        words = text.split()
        
        for word in words:
            # 检查是否有相似的术语
            similar_terms = self._find_similar_terms(word, threshold)
            if similar_terms:
                suggestions.append({
                    "word": word,
                    "suggestions": similar_terms
                })
        
        return suggestions
    
    def _find_similar_terms(self, word: str, threshold: float) -> List[Dict]:
        """查找相似术语（可以集成编辑距离算法）"""
        # 简单实现：前缀匹配
        similar = []
        prefix_matches = list(self.trie.keys(prefix=word[:3]))
        
        for match in prefix_matches[:5]:  # 最多返回5个建议
            similar.append({
                "term": match,
                "correct": self.trie[match],
                "confidence": 0.8  # 简化的置信度
            })
        
        return similar
    
    def batch_correct(self, texts: List[str]) -> List[Tuple[str, List[Dict]]]:
        """批量修正文本"""
        results = []
        for text in texts:
            results.append(self.correct_text(text))
        return results