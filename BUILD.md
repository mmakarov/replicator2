# Сборка Replicator2 для Windows

## Автоматическая сборка через GitHub Actions (рекомендуется)

### Как собрать приложение:

1. **Запушь код на GitHub:**
   ```bash
   git add .
   git commit -m "Подготовка к сборке Windows-приложения"
   git push origin main
   ```

2. **Запусти сборку:**
   - Открой репозиторий на GitHub
   - Перейди во вкладку **Actions**
   - Выбери workflow **"Build Windows Desktop App"**
   - Нажми **"Run workflow"** → **"Run workflow"**

3. **Скачай готовый файл:**
   - Дождись завершения сборки (5-10 минут)
   - Перейди в последний успешный run
   - В разделе **Artifacts** скачай `Replicator2-Windows`
   - Это zip-архив с `Replicator2.exe`

### Автоматический релиз (опционально):

Создай тег для автоматического создания релиза:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions автоматически создаст релиз с exe-файлом.

---

## Что изменилось для Windows-сборки

### 1. Автоматическая загрузка FFmpeg
- Используется библиотека `imageio-ffmpeg`
- FFmpeg скачивается автоматически при первом запуске (~40MB)
- Не требуется ручная установка

### 2. Работа со шрифтами
- Приложение ищет шрифты в папке `fonts/`
- Если шрифт не найден — использует системный (Windows) или встроенный FFmpeg
- На этапе сборки автоматически скачивается DejaVu Sans

### 3. Структура проекта
```
replicator2/
├── app.py                 # Основное приложение
├── requirements.txt       # Зависимости (+imageio-ffmpeg)
├── fonts/                 # Шрифты (создается автоматически)
│   └── README.md
└── .github/workflows/
    └── build-windows.yml  # Конфигурация сборки
```

---

## Ручная сборка (если есть Windows)

Если есть доступ к Windows-машине:

```bash
# 1. Установи зависимости
pip install -r requirements.txt
pip install streamlit-desktop-app

# 2. Собери приложение
streamlit-desktop-app build app.py --name Replicator2

# 3. Найди результат в папке dist/
```

---

## Примечания

- Размер итогового exe-файла: ~150-200MB (включает Python, Streamlit, FFmpeg)
- При первом запуске потребуется интернет для загрузки FFmpeg
- Последующие запуски работают офлайн
