import configparser
import os
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AudioConfig:
    samplerate: int = 16000
    record_seconds: int = 3
    chunk_duration: float = 0.1
    energy_threshold: float = 0.01
    silence_timeout: int = 5

@dataclass
class WhisperConfig:
    model_size: str = "base"
    device: str = "cuda"
    compute_type: str = "float16"
    beam_size: int = 5
    vad_filter: bool = True
    task: str = "transcribe"

@dataclass
class TextProcessorConfig:
    similarity_threshold: float = 0.7
    overlap_threshold: float = 0.6
    max_buffer_size: int = 50
    max_keywords: int = 8
    min_word_length: int = 3
    
@dataclass
class UIConfig:
    min_width: int = 400
    max_width: int = 1200
    min_height: int = 150
    expanded_height: int = 700
    
    default_width: int = 450
    default_height: int = 300
    
    info_section_min_height: int = 500
    text_section_min_height: int = 250
    
    animation_duration: int = 250
    queue_check_interval: int = 100
    remember_position: bool = True


class AppConfig:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            self.create_default_config()
        self.config.read(config_file, encoding='utf-8')
        
        self.audio = self._load_audio_config()
        self.whisper = self._load_whisper_config()
        self.text_processor = self._load_text_processor_config()
        self.ui = self._load_ui_config()
    

    def _load_audio_config(self) -> AudioConfig:
        audio_section = self.config['Audio']
        return AudioConfig(
            samplerate=audio_section.getint('samplerate', 16000),
            record_seconds=audio_section.getint('record_seconds', 3),
            chunk_duration=audio_section.getfloat('chunk_duration', 0.1),
            energy_threshold=audio_section.getfloat('energy_threshold', 0.01),
            silence_timeout=audio_section.getint('silence_timeout', 5)
        )
    
    def _load_whisper_config(self) -> WhisperConfig:
        whisper_section = self.config['Whisper']
        return WhisperConfig(
            model_size=whisper_section.get('model_size', 'base'),
            device=whisper_section.get('device', 'cuda'),
            compute_type=whisper_section.get('compute_type', 'float16'),
            beam_size=whisper_section.getint('beam_size', 5),
            vad_filter=whisper_section.getboolean('vad_filter', True),
            task=whisper_section.get('task', 'transcribe')
        )
    
    def _load_text_processor_config(self) -> TextProcessorConfig:
        if 'TextProcessor' in self.config:
            tp_section = self.config['TextProcessor']
            return TextProcessorConfig(
                similarity_threshold=tp_section.getfloat('similarity_threshold', 0.7),
                overlap_threshold=tp_section.getfloat('overlap_threshold', 0.6),
                max_buffer_size=tp_section.getint('max_buffer_size', 50),
                max_keywords=tp_section.getint('max_keywords', 8),
                min_word_length=tp_section.getint('min_word_length', 3)
            )
        return TextProcessorConfig()
    
    def _load_ui_config(self) -> UIConfig:
        if 'UI' in self.config:
            ui_section = self.config['UI']
            return UIConfig(
                min_width=ui_section.getint('min_width', 400),
                max_width=ui_section.getint('max_width', 1200),
                min_height=ui_section.getint('min_height', 150),
                expanded_height=ui_section.getint('expanded_height', 700),
                default_width=ui_section.getint('default_width', 450),
                default_height=ui_section.getint('default_height', 300),
                info_section_min_height=ui_section.getint('info_section_min_height', 500),
                text_section_min_height=ui_section.getint('text_section_min_height', 250),
                animation_duration=ui_section.getint('animation_duration', 250),
                queue_check_interval=ui_section.getint('queue_check_interval', 100),
                remember_position=ui_section.getboolean('remember_position', True)
            )
        return UIConfig()
    
    def create_default_config(self):
        """Create default configuration file with all sections."""
        config = configparser.ConfigParser()
        
        config['Audio'] = {
            'samplerate': '16000', 'record_seconds': '3', 'chunk_duration': '0.1',
            'energy_threshold': '0.01', 'silence_timeout': '5'
        }
        
        config['Whisper'] = {
            'model_size': 'base', 'device': 'cuda', 'compute_type': 'float16',
            'beam_size': '5', 'vad_filter': 'True', 'task': 'transcribe'
        }
        
        config['TextProcessor'] = {
            'similarity_threshold': '0.7', 'overlap_threshold': '0.6',
            'max_buffer_size': '50', 'max_keywords': '8', 'min_word_length': '3'
        }

        config['UI'] = {
            'min_width': '400', 'max_width': '1200', 'min_height': '150', 'expanded_height': '700',
            'default_width': '450', 'default_height': '300',
            'info_section_min_height': '500', 'text_section_min_height': '250',
            'animation_duration': '250', 'queue_check_interval': '100', 'remember_position': 'True'
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Created default {self.config_file}")
        
    def save_config(self):
        self.config['Audio'] = {str(k): str(v) for k, v in self.audio.__dict__.items()}
        self.config['Whisper'] = {str(k): str(v) for k, v in self.whisper.__dict__.items()}
        self.config['TextProcessor'] = {str(k): str(v) for k, v in self.text_processor.__dict__.items()}
        self.config['UI'] = {str(k): str(v) for k, v in self.ui.__dict__.items()}
        
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
    
    def get_window_geometry(self) -> Tuple[int, int, int, int]:
        if 'WindowGeometry' in self.config:
            geo = self.config['WindowGeometry']
            return (geo.getint('x', 100), geo.getint('y', 100),
                    geo.getint('width', self.ui.default_width),
                    geo.getint('height', self.ui.default_height))
        return None
    
    def save_window_geometry(self, x: int, y: int, width: int, height: int):
        if 'WindowGeometry' not in self.config:
            self.config.add_section('WindowGeometry')
        
        self.config['WindowGeometry'] = {'x': str(x), 'y': str(y), 'width': str(width), 'height': str(height)}