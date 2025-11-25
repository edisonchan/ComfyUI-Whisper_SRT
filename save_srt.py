import os
import folder_paths

class SaveSRTNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "srt_text": ("STRING", {"forceInput": True}),
                "filename": ("STRING", {"default": "subtitles"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("srt_text",)
    FUNCTION = "save_srt"
    CATEGORY = "whisper"
    OUTPUT_NODE = True

    def save_srt(self, srt_text, filename):
        # 确保文件名有效且以 .srt 结尾
        if not filename or filename == "False" or filename == "false":
            filename = "subtitles"
            
        if not filename.lower().endswith('.srt'):
            filename += '.srt'

        # 保存到输出目录
        output_dir = folder_paths.get_output_directory()
        file_path = os.path.join(output_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(srt_text)
            
            # 计算字幕段数
            segments_count = srt_text.strip().count('\n\n') + 1 if srt_text.strip() else 0
            
            # 返回成功信息
            result_text = f"SRT文件已保存: {filename}\n共{segments_count}段字幕\n\n{srt_text}"
            
            return {
                "ui": {
                    "text": [result_text]
                },
                "result": (srt_text,)
            }
        except Exception as e:
            error_msg = f"保存SRT文件时出错: {e}"
            return {
                "ui": {
                    "text": [error_msg]
                },
                "result": (srt_text,)
            }
