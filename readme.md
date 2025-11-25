# ComfyUI Whisper SRT

基于 [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper) 开发的字幕生成插件，支持 SRT 格式字幕文件输出。

## 📋 许可证声明

本项目基于 [ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper) 开发，
遵循 [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

### ✅ 允许的行为
- 自由使用、修改和分发本软件
- 用于个人、教育或非商业项目
- 在注明原作者的情况下分享您的修改

### ❌ 禁止的行为  
- 将本软件用于商业目的
- 销售或直接通过本软件盈利
- 更改本软件的许可证条款

### 📝 使用要求
- 保留原始作者的版权声明
- 在衍生作品中采用相同的许可证
- 明确标注基于原项目开发

## 功能特性

- 🎯 基于 OpenAI Whisper 的音频转录
- 📝 自动生成带时间轴的 SRT 字幕文件
- 🌍 支持多语言转录（中文、英文、日文等）
- ⚡ 多种 Whisper 模型选择（tiny 到 large）
- 🎨 灵活的字幕样式和位置设置
- 💾 直接保存 SRT 文件，支持自定义文件名

## 安装方法

### 通过 ComfyUI Manager 安装
1. 打开 ComfyUI
2. 进入 Manager 界面
3. 搜索 "ComfyUI-Whisper_SRT"
4. 点击安装

## 快速开始

1. 下载示例工作流：[whisper_video_srt.json](https://github.com/edisonchan/ComfyUI-Whisper_SRT/blob/master/example_workflows/whisper_video_srt.json)
2. 在 ComfyUI 中加载工作流
3. 连接音频输入节点
4. 运行工作流生成字幕

## 核心节点

### Apply Whisper
音频转录核心节点，支持：
- 多语言识别（自动检测或手动指定）
- 提示词引导转录
- 单词级时间戳提取
- 直接输出 SRT 格式字幕

**输出端口：**
- `text` - 纯文本转录结果
- `srt_text` - 格式化的 SRT 字幕内容
- `segments_alignment` - 段落时间对齐数据
- `words_alignment` - 单词时间对齐数据

### Save SRT
字幕文件保存节点：
- 支持自定义文件名
- 自动添加 .srt 扩展名
- 保存到 ComfyUI 输出目录
- 实时预览字幕内容

### Add Subtitles To Frames
视频帧字幕叠加节点：
- 自定义字体、颜色、大小
- 灵活定位（居中或指定坐标）
- 生成字幕蒙版和裁剪区域

## 模型支持

支持所有 Whisper 模型：
- `tiny` / `tiny.en` - 轻量级，快速转录
- `base` / `base.en` - 平衡速度与精度
- `small` / `small.en` - 推荐用于一般用途
- `medium` / `medium.en` - 高质量转录
- `large-v1` / `large-v2` / `large-v3` - 最高精度
- `turbo` - 优化速度版本

模型自动下载到：`ComfyUI/models/stt/whisper/`

## 使用示例

### 基础字幕生成
音频文件 → Apply Whisper → Save SRT

### 视频字幕叠加
视频帧 → Add Subtitles To Frames → 输出视频
Apply Whisper (提供时间戳)

### 高级工作流
完整的工作流示例请参考 [示例文件](https://github.com/edisonchan/ComfyUI-Whisper_SRT/blob/master/example_workflows/whisper_video_srt.json)

## 技术特点

- **内存优化**：集成 ComfyUI 模型管理系统，智能加载/卸载模型
- **时间精度**：支持毫秒级时间戳，符合 SRT 标准格式
- **格式兼容**：生成的 SRT 文件兼容主流视频播放器和编辑软件
- **灵活配置**：所有参数均可通过节点界面调整

## 更新记录

### v1.0.0
- 基于 ComfyUI-Whisper 开发
- 新增 SRT 字幕文件输出功能
- 添加 Save SRT 保存节点
- 优化模型加载和内存管理

## 致谢

本项目基于 [yuvraj108c/ComfyUI-Whisper](https://github.com/yuvraj108c/ComfyUI-Whisper) 开发，
特别感谢原作者的优秀工作和开源贡献。

---

*本项目遵循 CC BY-NC-SA 4.0 许可证，仅供非商业用途使用*
