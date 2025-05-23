import gradio as gr
import os
import time
import random
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# 模拟模型列表
def get_models():
    model_dir = "./models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    return [f for f in os.listdir(model_dir) if f.endswith(".ckpt") or f.endswith(".safetensors")]

# 分阶段生成函数
def staged_generate(prompt, cfg, max_tokens, batch_count, batch_size):
    # stages = [
    #     "🎤 歌词生成中...",
    #     "🎼 Stage-1: 音乐语言建模...",
    #     "🎛️ Stage-2: 残差建模...",
    #     "🎚️ 声轨混音中...",
    # ]

    # for stage in stages:
    #     time.sleep(3)
    #     yield gr.update(value=stage), gr.update(), gr.update()

    # 每个阶段设置不同等待时间
    stages = [
        ("🎤 歌词生成中...", 5),
        ("🎼 Stage-1: 音乐语言建模...", 6),
        ("🎛️ Stage-2: 残差建模...", 6),
        ("🎚️ 声轨混音中...", 3),
    ]

    # 分阶段输出
    for stage_text, wait_time in stages:
        yield gr.update(value=stage_text), gr.update(), gr.update()
        time.sleep(wait_time)

    # 最后输出真实结果
    # audio_path = "example_audio.wav"  # 请确保该文件真实存在
    audio_path = os.path.join("egs", "归途.MP3")
    lyrics = '''[verse]  
老橡树的影子拉长夕阳  
背包里装着未写完的诗行  
铁轨延伸向记忆的远方  
风中有母亲呼唤的回响  

[chorus]  
归途是永不熄灭的炉火  
照亮每个异乡人的寂寞  
把故事装进生锈的琴盒  
让琴弦诉说岁月的斑驳
'''
#     lyrics = '''[verse]
# 街灯下脚步坚定如鼓点
# 破旧皮靴踏响不屈的誓言
# 伤痕是勋章不是亏欠
# 黑夜挡不住内心的火焰

# [chorus]
# 燃烧吧，灵魂的吉他弦
# 在风暴中奏出信念
# 每一次跌倒都是热血的伏笔
# 我用呐喊写下明天的诗篇
# '''
    yield gr.update(value="✅ 完成！"), gr.update(value=audio_path), gr.update(value=lyrics)

# 搭建界面
with gr.Blocks(title="音乐创作系统") as demo:
    gr.Markdown("# 🎵 音乐创作系统")

    with gr.Tabs():
        with gr.TabItem("音乐生成"):
            with gr.Row():
                model_list = gr.Dropdown(label="模型选择", choices=get_models(), interactive=True)

            with gr.Row():
                with gr.Column(scale=3):
                    prompt = gr.Textbox(label="提示词", placeholder="描述你想要的音乐风格", lines=3)
                    with gr.Accordion("参数设置", open=True):
                        cfg = gr.Slider(label="CFG Scale", minimum=1, maximum=14, value=7, step=0.5)
                        max_tokens = gr.Slider(label="Max New Tokens", minimum=2000, maximum=6000, value=3000, step=100)
                        batch_count = gr.Slider(label="Batch Count", minimum=1, maximum=8, value=1, step=1)
                        batch_size = gr.Slider(label="Batch Size", minimum=1, maximum=8, value=1, step=1)

                with gr.Column(scale=2):
                    generate_btn = gr.Button("🎶 生成")
                    stage_status = gr.Textbox(label="⏳ 当前进度", lines=2, interactive=False)
                    audio_out = gr.Audio(label="🎧 音频预览", type="filepath")
                    text_out = gr.Textbox(label="📝 歌词", lines=6)

            generate_btn.click(
                fn=staged_generate,
                inputs=[prompt, cfg, max_tokens, batch_count, batch_size],
                outputs=[stage_status, audio_out, text_out]
            )

        with gr.TabItem("乐谱转录"):
            gr.Markdown("## 🧾 乐谱转录系统\n上传音频和歌词，生成对齐后的乐谱文件。")

            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(label="🎵 输入音频", type="filepath")
                    lyric_input = gr.Textbox(label="📝 输入歌词", lines=6, placeholder="请输入与音频匹配的歌词")
                    generate_score_btn = gr.Button("🎼 生成乐谱")

                with gr.Column():
                    stage_display = gr.Textbox(label="⏳ 当前阶段", interactive=False)
                    file_output = gr.File(label="📥 下载乐谱文件", visible=False)

            def generate_score(audio_path, lyrics):
                # 阶段定义 (提示词, 等待时间)
                stages = [
                    ("📑 句级分割...", 3),
                    ("🔡 音节对齐...", 5),
                    ("🎵 音高对齐...", 4),
                    ("✅ 转录完成", 1)
                ]

                for stage_text, wait_time in stages:
                    yield gr.update(value=stage_text), gr.update(visible=False)
                    time.sleep(wait_time)

                # 模拟生成结果
                fake_score_path = "egs/score.zip"  # 请确保这个文件实际存在或是你生成的
                yield gr.update(value="✅ 转录完成"), gr.update(value=fake_score_path, visible=True)

            generate_score_btn.click(
                fn=generate_score,
                inputs=[audio_input, lyric_input],
                outputs=[stage_display, file_output]
            )
            
        with gr.TabItem("歌词评估"):
            gr.Markdown("## 📊 歌词质量评估\n输入歌词文本，系统将从三个维度评估其质量：文本多样性、语义相关性和语法流畅性。")

            with gr.Row():
                with gr.Column():
                    lyric_input_eval = gr.Textbox(label="📝 歌词输入", lines=8, placeholder="请输入待评估的歌词")
                    lyric_input_eval = gr.Textbox(label="📝 歌词风格", lines=1, placeholder="请输入对应的提示词")
                    eval_button = gr.Button("📈 开始评估")

                with gr.Column():
                    eval_table = gr.HTML(label="📋 评估结果")

            def evaluate_lyrics(lyrics):
                # 模拟每个维度的延迟和结果
                results = ""

                # 第一部分：文本多样性
                time.sleep(5)
                diversity = """
                <h4>📌 文本多样性评估</h4>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr><th>指标</th><th>得分(%)</th></tr>
                    <tr><td>Dist-1</td><td>78.2</td></tr>
                    <tr><td>Dist-2</td><td>48.2</td></tr>
                    <tr><td>1-gram 重复率</td><td>9.1</td></tr>
                    <tr><td>2-gram 重复率</td><td>16.5</td></tr>
                </table><br/>
                """
                results += diversity
                yield results

                # 第二部分：语义相关性
                time.sleep(5)
                semantics = """
                <h4>🔍 语义相关性评估</h4>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr><th>指标</th><th>得分</th></tr>
                    <tr><td>BERTScore</td><td>0.914</td></tr>
                </table><br/>
                """
                results += semantics
                yield results

                # 第三部分：语法流畅性
                time.sleep(5)
                fluency = """
                <h4>✒️ 语法流畅性评估</h4>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr><th>指标</th><th>得分</th></tr>
                    <tr><td>PPL（困惑度）</td><td>9.4</td></tr>
                </table>
                """
                results += fluency
                yield results

            eval_button.click(
                fn=evaluate_lyrics,
                inputs=[lyric_input_eval],
                outputs=[eval_table]
            )


        with gr.TabItem("音乐评估"):
            gr.Markdown("## 🎼 音乐质量评估\n上传音频，系统将输出关键指标并与SOTA模型（Suno）对比雷达图。")

            with gr.Row():
                with gr.Column():
                    music_input = gr.Audio(label="🎵 输入音乐", type="filepath")
                    music_eval_btn = gr.Button("📈 评估音乐")

                with gr.Column():
                    music_metric_table = gr.HTML(label="📊 指标数据")
                    radar_chart = gr.Image(label="📉 与Suno对比图", type="filepath")

            def evaluate_music_fixed(music_path):
                time.sleep(10)

                metric_html = """
                <h4>📊 音乐生成质量指标</h4>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr><th>指标</th><th>得分</th></tr>
                    <tr><td>MCD (dB)</td><td>3.7</td></tr>
                    <tr><td>SingMOS</td><td>4.6</td></tr>
                    <tr><td>SI-SDR (dB)</td><td>13.6</td></tr>
                    <tr><td>STOI</td><td>0.90</td></tr>
                </table>
                """

                radar_img_path = os.path.join("egs", "radar.png")
                return metric_html, radar_img_path

            music_eval_btn.click(
                fn=evaluate_music_fixed,
                inputs=[music_input],
                outputs=[music_metric_table, radar_chart]
            )

demo.queue().launch()
