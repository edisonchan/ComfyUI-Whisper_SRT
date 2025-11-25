import os
import folder_paths

class SaveSRTNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "srt_text": ("STRING", {"forceInput": True}),
                "filename": ("STRING", {"default": "subtitles"}),
            },
            "optional": {
                "segments_alignment": ("whisper_alignment",),
                "words_alignment": ("whisper_alignment",),
                "use_word_level": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("srt_text",)
    FUNCTION = "save_srt"
    CATEGORY = "whisper"
    OUTPUT_NODE = True

    def save_srt(self, srt_text, filename, segments_alignment=None, words_alignment=None, use_word_level=False):
        # 如果提供了对齐数据但没有SRT文本，则生成SRT
        if not srt_text and segments_alignment:
            from .apply_whisper import segments_to_srt, words_to_srt
            if use_word_level and words_alignment:
                srt_text = words_to_srt(words_alignment)
            else:
                srt_text = segments_to_srt(segments_alignment)

        # 确保文件名以 .srt 结尾
        if not filename.lower().endswith('.srt'):
            filename += '.srt'

        # 保存到输出目录
        output_dir = folder_paths.get_output_directory()
        file_path = os.path.join(output_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(srt_text)
            print(f"SRT文件已保存: {file_path}")
        except Exception as e:
            print(f"保存SRT文件时出错: {e}")

        return (srt_text,)

class PreviewSRTNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "srt_text": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "max_lines": ("INT", {"default": 10, "min": 1, "max": 50}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("srt_preview",)
    FUNCTION = "preview_srt"
    CATEGORY = "whisper"

    def preview_srt(self, srt_text, max_lines=10):
        # 生成预览文本（前N行）
        lines = srt_text.split('\n')
        preview_lines = lines[:min(max_lines * 4, len(lines))]  # 每段字幕占4行
        preview_text = '\n'.join(preview_lines)
        
        if len(lines) > len(preview_lines):
            preview_text += f"\n\n... (共{len(lines)//4}段字幕，已显示前{len(preview_lines)//4}段)"
        
        return (preview_text,)
