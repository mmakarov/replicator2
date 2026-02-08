import subprocess
import sys
import os

def check_ffmpeg():
    """Проверить наличие и работоспособность FFmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg успешно установлен")
            version_line = result.stdout.split('\n')[0]
            print(f"Версия FFmpeg: {version_line}")
            return True
        else:
            print("❌ FFmpeg не работает корректно")
            print(f"Ошибка: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg не найден в системе")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при проверке FFmpeg")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке FFmpeg: {e}")
        return False

def check_ffprobe():
    """Проверить наличие и работоспособность FFprobe"""
    try:
        result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFprobe успешно установлен")
            version_line = result.stdout.split('\n')[0]
            print(f"Версия FFprobe: {version_line}")
            return True
        else:
            print("❌ FFprobe не работает корректно")
            print(f"Ошибка: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ FFprobe не найден в системе")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Таймаут при проверке FFprobe")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке FFprobe: {e}")
        return False

def check_python_packages():
    """Проверить установку Python-пакетов"""
    required_packages = ['streamlit', 'PIL', 'proglog', 'natsort']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
            print(f"✅ {package} успешно импортирован")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_basic_functionality():
    """Тестировать базовую функциональность приложения"""
    try:
        # Проверим, можем ли мы создать рабочую директорию
        work_dir = os.path.abspath("temp_video_test")
        os.makedirs(work_dir, exist_ok=True)
        print("✅ Создание рабочей директории работает")
        
        # Проверим, можем ли мы создать простой текстовый файл
        test_file = os.path.join(work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        print("✅ Запись в файлы работает")
        
        # Удалим тестовые файлы
        os.remove(test_file)
        os.rmdir(work_dir)
        print("✅ Удаление файлов работает")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка при тестировании базовой функциональности: {e}")
        return False

def main():
    print("=== Диагностика зависимостей для Video Maker ===\n")
    
    print("1. Проверка FFmpeg...")
    ffmpeg_ok = check_ffmpeg()
    
    print("\n2. Проверка FFprobe...")
    ffprobe_ok = check_ffprobe()
    
    print("\n3. Проверка Python-пакетов...")
    packages_ok = check_python_packages()
    
    print("\n4. Тестирование базовой функциональности...")
    basic_ok = test_basic_functionality()
    
    print("\n=== Результаты диагностики ===")
    print(f"FFmpeg: {'✅ OK' if ffmpeg_ok else '❌ ОШИБКА'}")
    print(f"FFprobe: {'✅ OK' if ffprobe_ok else '❌ ОШИБКА'}")
    print(f"Python-пакеты: {'✅ OK' if packages_ok else '❌ ОШИБКА'}")
    print(f"Базовая функциональность: {'✅ OK' if basic_ok else '❌ ОШИБКА'}")
    
    if ffmpeg_ok and ffprobe_ok and packages_ok and basic_ok:
        print("\n🎉 Все зависимости установлены правильно! Приложение должно работать.")
        return True
    else:
        print("\n⚠️  Обнаружены проблемы с зависимостями. Проверьте вывод выше для деталей.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)