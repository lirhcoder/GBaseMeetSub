"""术语管理模块 - 自动积累和管理专用术语"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import threading

class TermManager:
    def __init__(self, term_file: str = "data/terms.json", 
                 log_file: str = "data/corrections_log.json"):
        self.term_file = term_file
        self.log_file = log_file
        self.terms: Dict[str, Dict] = self._load_terms()
        self.corrections_log: List[Dict] = self._load_log()
        self._lock = threading.Lock()
        
    def _load_terms(self) -> Dict:
        """加载术语库"""
        if os.path.exists(self.term_file):
            with open(self.term_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_log(self) -> List:
        """加载纠正记录"""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_terms(self):
        """保存术语库"""
        os.makedirs(os.path.dirname(self.term_file), exist_ok=True)
        with open(self.term_file, 'w', encoding='utf-8') as f:
            json.dump(self.terms, f, ensure_ascii=False, indent=2)
    
    def _save_log(self):
        """保存纠正记录"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.corrections_log, f, ensure_ascii=False, indent=2)
    
    def add_correction(self, original: str, corrected: str, 
                      context: Optional[str] = None, confidence: float = 1.0):
        """记录一次纠正并自动添加到术语库"""
        with self._lock:
            # 记录纠正
            correction_entry = {
                "timestamp": datetime.now().isoformat(),
                "original": original,
                "corrected": corrected,
                "context": context,
                "confidence": confidence
            }
            self.corrections_log.append(correction_entry)
            self._save_log()
            
            # 自动添加到术语库
            if original not in self.terms:
                self.terms[original] = {
                    "correct": corrected,
                    "frequency": 1,
                    "contexts": [context] if context else [],
                    "confidence": confidence,
                    "created_at": datetime.now().isoformat(),
                    "auto_learned": True
                }
            else:
                # 更新频率和置信度
                self.terms[original]["frequency"] += 1
                self.terms[original]["confidence"] = max(
                    self.terms[original]["confidence"], 
                    confidence
                )
                if context and context not in self.terms[original]["contexts"]:
                    self.terms[original]["contexts"].append(context)
            
            self._save_terms()
    
    def get_term(self, word: str) -> Optional[Dict]:
        """获取术语信息"""
        return self.terms.get(word)
    
    def get_all_terms(self) -> Dict:
        """获取所有术语"""
        return self.terms.copy()
    
    def get_high_frequency_terms(self, min_frequency: int = 3) -> Dict:
        """获取高频术语"""
        return {k: v for k, v in self.terms.items() 
                if v.get("frequency", 0) >= min_frequency}