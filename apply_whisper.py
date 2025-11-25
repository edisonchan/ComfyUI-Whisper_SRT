import whisper
import os
import folder_paths
import uuid
import torchaudio
import torch
import logging

import comfy.model_management as mm
import comfy.model_patcher

WHISPER_MODEL_SUBDIR = os.path.join("stt", "whisper")

logger = logging.getLogger(__name__)

WHISPER_PATCHER_CACHE = {}

class WhisperModelWrapper(torch.nn.Module):
    """
    A torch.nn.Module wrapper for Whisper models.
    This allows ComfyUI's model management to treat Whisper models like any other
    torch module, enabling device placement and memory management.
    """
    def __init__(self, model_name, download_root):
        super().__init__()
        self.model_name = model_name
        self.download_root = download_root
        self.whisper_model = None
        self.model_loaded_weight_memory = 0

    def load_model(self, device):
        """Load the Whisper model from disk to the specified device"""
        self.whisper_model = whisper.load_model(
            self.model_name,
            download_root=self.download_root,
            device=device
        )
        # Estimate model size for memory management
        model_size = sum(p.numel() * p.element_size() for p in self.whisper_model.parameters())
        self.model_loaded_weight_memory = model_size

class WhisperPatcher(comfy.model_patcher.ModelPatcher):
    """
    Custom ModelPatcher for Whisper models that integrates with ComfyUI's
    model management system for proper loading/offloading.
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

    def patch_model(self, device_to=None, *args, **kwargs):
        """
        This method is called by ComfyUI's model manager when it's time to load
        the model onto the target device (usually the GPU). Our responsibility here
        is to ensure the model weights are loaded from disk if they haven't been already.
        """
        target_device = self.load_device

        if self.model.whisper_model is None:
            logger.info(f"Loading Whisper model '{self.model.model_name}' to {target_device}...")
            self.model.load_model(target_device)
            self.size = self.model.model_loaded_weight_memory
        else:
            logger.info(f"Whisper model '{self.model.model_name}' already in memory.")

        return super().patch_model(device_to=target_device, *args, **kwargs)

    def unpatch_model(self, device_to=None, unpatch_weights=True, *args, **kwargs):
        """
        Offload the Whisper model to free up VRAM.
        """
        if unpatch_weights:
            logger.info(f"Offloading Whisper model '{self.model.model_name}' to {device_to}...")
            self.model.whisper_model = None
            self.model.model_loaded_weight_memory = 0
            mm.soft_empty_cache()
        return super().unpatch_model(device_to, unpatch_weights, *args, **kwargs)

def format_timestamp(seconds):
    """将秒数转换为 SRT 时间格式: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    milliseconds = int((seconds_remainder - int(seconds_remainder)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"

def segments_to_srt(segments):
    """将 Whisper 分段转换为 SRT 格式字符串"""
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['value'].strip()
        
        # 确保文本不为空
        if not text:
            continue
            
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(text)
        srt_content.append("")  # 空行分隔
        
    return "\n".join(srt_content)

def words_to_srt(words_alignment):
    """将单词级时间戳转换为 SRT 格式字符串"""
    srt_content = []
    index = 1
    
    # 将单词按句子分组
    current_sentence = []
    current_start = None
    current_end = 0
    
    for word in words_alignment:
        word_text = word['value'].strip()
        if not word_text:
            continue
            
        if current_start is None:
            current_start = word['start']
        
        current_sentence.append(word_text)
        current_end = word['end']
        
        # 如果单词以标点结尾，则认为句子结束
        if word_text and word_text[-1] in '.!?。！？':
            sentence_text = ' '.join(current_sentence)
            if sentence_text:
                start_time = format_timestamp(current_start)
                end_time = format_timestamp(current_end)
                
                srt_content.append(f"{index}")
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(sentence_text)
                srt_content.append("")
                
                index += 1
            
            current_sentence = []
            current_start = None
    
    # 处理最后一个不完整的句子
    if current_sentence:
        sentence_text = ' '.join(current_sentence)
        if sentence_text:
            start_time = format_timestamp(current_start)
            end_time = format_timestamp(current_end)
            
            srt_content.append(f"{index}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(sentence_text)
    
    return "\n".join(srt_content)

class ApplyWhisperNode:
    languages_by_name = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "model": (['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo'],),
            },
            "optional": {
                "language": (
                    ["auto"] +
                    [s.capitalize() for s in sorted(list(whisper.tokenizer.LANGUAGES.values())) ],
                ),
                "prompt": ("STRING", {"default":""}),
                "use_word_level_srt": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "whisper_alignment", "whisper_alignment", "STRING")
    RETURN_NAMES = ("text", "segments_alignment", "words_alignment", "srt_text")
    FUNCTION = "apply_whisper"
    CATEGORY = "whisper"
    OUTPUT_NODE = True

    def apply_whisper(self, audio, model, language="auto", prompt="", use_word_level_srt=False):
        # save audio bytes from VHS to file
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        audio_save_path = os.path.join(temp_dir, f"{uuid.uuid1()}.wav")
        torchaudio.save(audio_save_path, audio['waveform'].squeeze(
            0), audio["sample_rate"])

        cache_key = model
        if cache_key not in WHISPER_PATCHER_CACHE:
            load_device = mm.get_torch_device()
            download_root = os.path.join(folder_paths.models_dir, WHISPER_MODEL_SUBDIR)
            logger.info(f"Creating Whisper ModelPatcher for {model} on device {load_device}")
            
            model_wrapper = WhisperModelWrapper(model, download_root)
            patcher = WhisperPatcher(
                model=model_wrapper,
                load_device=load_device,
                offload_device=mm.unet_offload_device(),
                size=0  # Will be set when model loads
            )
            WHISPER_PATCHER_CACHE[cache_key] = patcher

        patcher = WHISPER_PATCHER_CACHE[cache_key]

        mm.load_model_gpu(patcher)
        whisper_model = patcher.model.whisper_model

        if whisper_model is None:
            logger.error("Whisper model failed to load. Please check logs for errors.")
            raise RuntimeError(f"Failed to load Whisper model: {model}")

        transcribe_args = {"initial_prompt": prompt}

        if language != "auto":
            if ApplyWhisperNode.languages_by_name is None:
                ApplyWhisperNode.languages_by_name = {v.lower(): k for k, v in whisper.tokenizer.LANGUAGES.items()}
            transcribe_args['language'] = ApplyWhisperNode.languages_by_name[language.lower()]
        
        # 添加调试信息
        print(f"开始Whisper转录，语言: {language}, 提示: {prompt}")
        
        result = whisper_model.transcribe(audio_save_path, word_timestamps=True, **transcribe_args)

        segments = result['segments']
        segments_alignment = []
        words_alignment = []

        # 添加调试信息
        print(f"Whisper返回了 {len(segments)} 个段落")
        
        for segment in segments:
            # create segment alignments
            segment_dict = {
                'value': segment['text'].strip(),
                'start': segment['start'],
                'end': segment['end']
            }
            segments_alignment.append(segment_dict)

            # 添加调试信息
            print(f"段落 {len(segments_alignment)}: '{segment['text'].strip()}' ({segment['start']:.2f}-{segment['end']:.2f})")

            # create word alignments
            if "words" in segment:
                for word in segment["words"]:
                    word_dict = {
                        'value': word["word"].strip(),
                        'start': word["start"],
                        'end': word['end']
                    }
                    words_alignment.append(word_dict)

        # 生成 SRT 文本
        if use_word_level_srt and words_alignment:
            print("使用单词级时间戳生成SRT")
            srt_text = words_to_srt(words_alignment)
        else:
            print("使用段落级时间戳生成SRT")
            srt_text = segments_to_srt(segments_alignment)

        # 添加调试信息
        print(f"生成的SRT内容:")
        print("=" * 50)
        print(srt_text)
        print("=" * 50)
        print(f"SRT字符数: {len(srt_text)}")

        return (result["text"].strip(), segments_alignment, words_alignment, srt_text)
