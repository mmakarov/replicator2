import os
import subprocess
import shutil
import re
import math
import streamlit as st
from PIL import Image


# === КОНСТАНТЫ ===
WORK_DIR = os.path.abspath("temp_video")


# === ФУНКЦИИ ===
def get_font_path():
    """Получить путь к шрифту"""
    fonts = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Arial.ttf",  # macOS
    ]
    for font in fonts:
        if os.path.exists(font):
            return font
    return "Sans"


def escape_text(text):
    """Экранировать текст для FFmpeg"""
    return str(text).replace("\\", "\\\\").replace("'", "'\\''").replace(":", "\\:")


def get_duration(filepath):
    """Получить длительность видео"""
    try:
        filepath = os.path.abspath(filepath)
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except:
        return 0.0


def run_ffmpeg(cmd):
    """Запустить FFmpeg команду"""
    cmd = [os.path.abspath(c) if os.path.isfile(c) or (isinstance(c, str) and c.endswith(('.mp4', '.mp3', '.png', '.txt'))) else c for c in cmd]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORK_DIR)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")
    return result


def create_overlay():
    """Создать оверлей из корня проекта"""
    overlay_path = os.path.join(WORK_DIR, "overlay.png")
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Проверяем наличие оверлея в корне проекта
    root_overlay = "overlay.png"
    if os.path.exists(root_overlay):
        # Копируем оверлей из корня проекта
        shutil.copy2(root_overlay, overlay_path)
    else:
        # Fallback: создаем пустой прозрачный оверлей
        img = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
        img.save(overlay_path)
    
    return overlay_path


def clean_video_dir():
    """Очистить директорию с видео"""
    video_dir = os.path.join(WORK_DIR, "video")
    if os.path.exists(video_dir):
        for f in os.listdir(video_dir):
            try:
                os.remove(os.path.join(video_dir, f))
            except:
                pass


def find_videos():
    """Найти все source*.mp4 файлы"""
    video_dir = os.path.join(WORK_DIR, "video")
    os.makedirs(video_dir, exist_ok=True)
    
    files = []
    if os.path.exists(video_dir):
        files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.startswith("source") and f.endswith(".mp4")]
    
    files.sort(key=lambda x: int(re.findall(r'\d+', os.path.basename(x))[0]) if re.findall(r'\d+', os.path.basename(x)) else 0)
    return files


def process_videos(heading, name1, name2, datetext, progress_callback):
    """Основная обработка видео"""
    
    # Создаём директории
    for folder in ["video", "audio", "temp_parts"]:
        os.makedirs(os.path.join(WORK_DIR, folder), exist_ok=True)
    
    # Получаем видео файлы
    files = find_videos()
    if not files:
        raise Exception("Нет видеофайлов!")
    
    font = get_font_path()
    temp_dir = os.path.join(WORK_DIR, "temp_parts")
    overlay = create_overlay()
    temp_files = []
    
    # 1. Обработка каждого видео
    for i, fpath in enumerate(files):
        progress_callback(f"Обработка {i+1}/{len(files)}...")
        out = os.path.join(temp_dir, f"part_{i:03d}.mp4")
        
        fpath = os.path.abspath(fpath)
        out = os.path.abspath(out)
        overlay_abs = os.path.abspath(overlay)
        
        filter_str = (
            f"[0:v]scale=1280:720,setsar=1[bg];"  # <--- ДОБАВЛЕНО setsar=1
            f"[1:v]scale=1280:720,setsar=1[ovr];" # <--- ДОБАВЛЕНО setsar=1
            f"[bg][ovr]overlay=0:0:shortest=1,"
            f"drawtext=fontfile='{font}':text='{escape_text(heading)}':fontcolor=white:fontsize=68:x=(w-text_w)/2:y=150,"
            f"drawtext=fontfile='{font}':text='{escape_text(name1)}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=250,"
            f"drawtext=fontfile='{font}':text='{escape_text(name2)}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=300,"
            f"drawtext=fontfile='{font}':text='{escape_text(datetext)}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=400"
        )

        
        run_ffmpeg([
            "ffmpeg", "-y", "-i", fpath, "-loop", "1", "-i", overlay_abs,
            "-filter_complex", filter_str, "-c:a", "copy", out
        ])
        temp_files.append(out)
    
    # 2. Склейка
    progress_callback("Склейка видео...")
    list_txt = os.path.join(WORK_DIR, "list.txt")
    with open(list_txt, "w") as f:
        for tf in temp_files:
            f.write(f"file '{os.path.abspath(tf)}'\n")
    
    medium = os.path.join(WORK_DIR, "medium.mp4")
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.abspath(list_txt),
        "-c", "copy", os.path.abspath(medium)
    ])
    os.remove(list_txt)
    
    # 3. Добавляем аудио
    audio_path = os.path.join(WORK_DIR, "audio", "voice.mp3")
    final_out = os.path.join(WORK_DIR, "youtube_ready.mp4")
    
    if os.path.exists(audio_path):
        progress_callback("Добавляю звук...")
        a_dur = get_duration(audio_path)
        v_dur = get_duration(medium)
        loop = math.ceil(a_dur/v_dur) if v_dur > 0 else 1
        
        silent = os.path.join(WORK_DIR, "silent.mp4")
        if loop > 1:
            run_ffmpeg([
                "ffmpeg", "-y", "-stream_loop", str(loop-1),
                "-i", os.path.abspath(medium), "-c", "copy", os.path.abspath(silent)
            ])
        else:
            shutil.copy(os.path.abspath(medium), os.path.abspath(silent))
        
        run_ffmpeg([
            "ffmpeg", "-y", "-i", os.path.abspath(silent), "-i", os.path.abspath(audio_path),
            "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-c:a", "aac", "-shortest", os.path.abspath(final_out)
        ])
        os.remove(silent)
    else:
        shutil.move(os.path.abspath(medium), os.path.abspath(final_out))
    
    # Чистим временные файлы
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return final_out


# === UI ===
st.set_page_config(page_title="Video Maker", layout="wide")

# Инициализируем директории
os.makedirs(os.path.join(WORK_DIR, "video"), exist_ok=True)
os.makedirs(os.path.join(WORK_DIR, "audio"), exist_ok=True)

col1, col2 = st.columns(2)

with col1:
    st.header("1. Файлы")
    
    # Видео
    videos = st.file_uploader("Видео (MP4)", type=["mp4"], accept_multiple_files=True)
    if videos:
        # ОЧИЩАЕМ старые файлы перед загрузкой новых
        clean_video_dir()
        
        for i, v in enumerate(videos):
            path = os.path.join(WORK_DIR, "video", f"source{i+1}.mp4")
            with open(path, "wb") as f:
                f.write(v.getbuffer())
        st.success(f"Загружено {len(videos)} видео")
    
    # Аудио
    audio = st.file_uploader("Аудио (MP3)", type=["mp3"])
    if audio:
        path = os.path.join(WORK_DIR, "audio", "voice.mp3")
        with open(path, "wb") as f:
            f.write(audio.getbuffer())
        st.success("Аудио загружено")

with col2:
    st.header("2. Текст")
    h = st.text_input("Заголовок", "HELLO")
    n1 = st.text_input("Строка 1", "Name")
    n2 = st.text_input("Строка 2", "Place")
    d = st.text_input("Дата", "2026")

st.divider()

if st.button("🚀 СОЗДАТЬ ВИДЕО", type="primary", use_container_width=True):
    videos = find_videos()
    if not videos:
        st.error("Загрузите видео!")
    else:
        status = st.empty()
        try:
            final = process_videos(h, n1, n2, d, lambda m: status.info(m))
            status.success("✅ Готово!")
            
            # Проверяем, что файл существует перед показом кнопки
            if os.path.exists(final):
                with open(final, "rb") as f:
                    data = f.read()
                
                # Улучшенная кнопка скачивания
                st.subheader("📥 Скачать видео:")
                st.download_button(
                    label="📥 Скачать готовое видео",
                    data=data,
                    file_name="video.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    help="Скачайте готовое видео в формате MP4"
                )
                
                # Информация о файле
                file_size = os.path.getsize(final) / (1024 * 1024)  # в МБ
                st.caption(f"Размер файла: {file_size:.1f} МБ")
            else:
                status.error("❌ Файл не найден. Видео не было создано.")
                
        except Exception as e:
            status.error(f"❌ Ошибка: {e}")
