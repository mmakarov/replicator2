# Шрифты для Replicator2

Приложение использует шрифты для наложения текста на видео.

## Опции:

### 1. Без шрифта (рекомендуется для Windows)
Если в этой папке нет шрифтов, приложение автоматически:
- Использует системные шрифты Windows (Segoe UI, Arial)
- Использует встроенный шрифт FFmpeg (если доступен)

### 2. Добавить свой шрифт
1. Скачайте TTF шрифт (например, DejaVu Sans, Liberation Sans, Roboto)
2. Положите файл в эту папку с одним из имен:
   - `DejaVuSans.ttf`
   - `LiberationSans-Regular.ttf`
   - `Arial.ttf`

### Рекомендуемые свободные шрифты:
- **DejaVu Sans**: https://dejavu-fonts.github.io/
- **Liberation Fonts**: https://github.com/liberationfonts/liberation-fonts
- **Roboto**: https://fonts.google.com/specimen/Roboto

## Примечание для сборки
При сборке через GitHub Actions шрифты из этой папки автоматически включаются в exe-файл.
