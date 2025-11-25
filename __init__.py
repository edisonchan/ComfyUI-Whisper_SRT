from .apply_whisper import ApplyWhisperNode
from .add_subtitles_to_frames import AddSubtitlesToFramesNode
from .add_subtitles_to_background import AddSubtitlesToBackgroundNode
from .resize_cropped_subtitles import ResizeCroppedSubtitlesNode
from .save_srt import SaveSRTNode  # 只导入 SaveSRTNode

NODE_CLASS_MAPPINGS = { 
    "Apply Whisper": ApplyWhisperNode,
    "Save SRT": SaveSRTNode,
    "Add Subtitles To Frames": AddSubtitlesToFramesNode,
    "Add Subtitles To Background": AddSubtitlesToBackgroundNode,
    "Resize Cropped Subtitles": ResizeCroppedSubtitlesNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Apply Whisper": "Apply Whisper", 
    "Save SRT": "Save SRT",
    "Add Subtitles To Frames": "Add Subtitles To Frames",
    "Add Subtitles To Background": "Add Subtitles To Background",
    "Resize Cropped Subtitles": "Resize Cropped Subtitles"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
