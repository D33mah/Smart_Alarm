import time
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import pygame

# المسار المحدد لملف الصوت
SOUND_FILE_PATH = r"C:\Users\adede\Downloads\SmartAlarm\alarm.mp3"

def setup_alarm_sound():
    """تهيئة نظام الصوت باستخدام Pygame"""
    if not pygame.mixer.get_init():
        pygame.mixer.init()

def verify_and_test_audio(sound_file=SOUND_FILE_PATH):
    """التحقق من وجود ملف الصوت وقابليته للتشغيل قبل بدء المنبه"""
    print("=== Sound System Test / اختبار النظام الصوتي ===")
    print(f"Audio Path: {sound_file}\n")

    if not os.path.exists(sound_file):
        print("[Error / خطأ] File not found! لم يتم العثور على ملف الصوت.")
        print("Please check the path and file name.")
        return False

    try:
        setup_alarm_sound()
        pygame.mixer.music.load(sound_file)
        print(" Success: File loaded and ready / تم العثور على الملف الصوتي بنجاح.\n")
        return True
    except Exception as e:
        print(f"\n[Error / خطأ] Failed to load audio: {e}")
        return False

def play_alarm_sound(sound_file=SOUND_FILE_PATH):
    """تشغيل صوت المنبه بتكرار مستمر"""
    try:
        setup_alarm_sound()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play(-1)  # تشغيل بتكرار لا نهائي
        return True
    except Exception as e:
        print(f"\n[Error / خطأ] Could not play sound: {e}")
        return False

def get_riyadh_time():
    """جلب الوقت الحالي وفق توقيت المملكة العربية السعودية (الرياض)"""
    return datetime.now(ZoneInfo("Asia/Riyadh"))

def set_alarm():
    """ضبط وقت المنبه والانتظار حتى موعده"""
    # 1. اختبار النظام الصوتي والملف أولاً
    if not verify_and_test_audio(SOUND_FILE_PATH):
        return

    # 2. أخذ التوقيت المطلوب من المستخدم مع قبول الخيارات المتنوعة
    while True:
        alarm_time_str = input("Enter Time (HH:MM) | أدخل الوقت (مثال 10:25): ").strip()
        period_input = input("Select Period | اختر الفترة [1 = AM (صباحاً) / 2 = PM (مساءً)]: ").strip().upper()

        # قبول الرقم أو الرمز 
        if period_input in ['1', 'AM']:
            period_str = "AM"
        elif period_input in ['2', 'PM']:
            period_str = "PM"
        else:
            print(" Invalid Choice! Enter 1 for AM or 2 for PM (أدخل 1 للصباح أو 2 للمساء).\n")
            continue

        full_time_str = f"{alarm_time_str} {period_str}"

        try:
            parsed_time = datetime.strptime(full_time_str, "%I:%M %p").time()
            break
        except ValueError:
            print(" Invalid format! Use HH:MM format (مثال: 07:00 أو 10:22).\n")

    now_riyadh = get_riyadh_time()
    print(f"\n Current Riyadh Time / الوقت الحالي في الرياض: {now_riyadh.strftime('%I:%M:%S %p')}")
    print(f" Alarm Set For / تم ضبط المنبه على: {parsed_time.strftime('%I:%M %p')}")
    print(" Waiting for alarm time... / البرنامج قيد الانتظار الآن...\n")

    # 3. حلقة الترقب ومقارنة الوقت
    while True:
        current_riyadh_time = get_riyadh_time().time()

        if (current_riyadh_time.hour == parsed_time.hour and 
            current_riyadh_time.minute == parsed_time.minute):
            
            print("\n ALARM RINGING! / حان وقت الاستيقاظ! المنبه يرن الآن!")
            
            # تشغيل الصوت عند حلول الوقت
            if play_alarm_sound(SOUND_FILE_PATH):
                print(" Press (Ctrl + C) in Terminal to stop sound / اضغط Ctrl+C لإيقاف الصوت.")
                try:
                    while pygame.mixer.music.get_busy():
                        time.sleep(1)
                except KeyboardInterrupt:
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                    print("\n Alarm Stopped Successfully / تم إيقاف المنبه بنجاح!")
            break

        time.sleep(1)

if __name__ == "__main__":
    set_alarm()