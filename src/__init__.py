"""GBaseMeetSub - 日语会议语音识别系统"""

__version__ = "0.1.0"
__author__ = "GBaseMeetSub Contributors"

from .main_pipeline import SpeechProcessingPipeline
from .speech_recognizer import SpeechRecognizer
from .term_manager import TermManager
from .term_corrector import TermCorrector
from .subtitle_generator import SubtitleGenerator
from .accuracy_validator import AccuracyValidator

__all__ = [
    "SpeechProcessingPipeline",
    "SpeechRecognizer",
    "TermManager",
    "TermCorrector",
    "SubtitleGenerator",
    "AccuracyValidator",
]