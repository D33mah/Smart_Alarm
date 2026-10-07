import time
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import urllib.request
import cv2
import numpy as np
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
    """تشغيل صوت المنبه بتكرار مستمر دون توقف"""
    try:
        setup_alarm_sound()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play(-1)
        return True
    except Exception as e:
        print(f"\n[Error / خطأ] Could not play sound: {e}")
        return False

def get_riyadh_time():
    """جلب الوقت الحالي وفق توقيت المملكة العربية السعودية (الرياض)"""
    return datetime.now(ZoneInfo("Asia/Riyadh"))

def get_cascade_classifier(filename, url):
    """جلب وتحميل ملفات التصنيف بأمان لمنع خطأ empty assertion error"""
    if not os.path.exists(filename):
        print(f"Downloading required cascade file: {filename}...")
        try:
            urllib.request.urlretrieve(url, filename)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return None
    
    cascade = cv2.CascadeClassifier(filename)
    if cascade.empty():
        print(f"[Error] Failed to load cascade classifier from {filename}")
        return None
    return cascade

def start_smart_camera_verification():
    """فتح الكاميرا والتحقق من وجود الوجه والعينين المفتوحتين لإيقاف المنبه"""
    print("\n Opening Smart Camera... / جاري فتح الكاميرا الذكية...")

    # روابط تحميل ملفات Haar Cascade الاحتياطية المضمونة
    FACE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    EYE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml"

    face_cascade = get_cascade_classifier("haarcascade_frontalface_default.xml", FACE_URL)
    eye_cascade = get_cascade_classifier("haarcascade_eye.xml", EYE_URL)

    if face_cascade is None or eye_cascade is None:
        print("[Error / خطأ] تعذر تحميل نموذج التعرف على الوجه والعيون.")
        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[Error / خطأ] Cannot access camera! تعذر الوصول للكاميرا.")
        return

    REQUIRED_CONSECUTIVE_FRAMES = 10  # استمرار فتح العينين لعدد إطارات متتالية
    frame_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error / خطأ] Failed to grab frame.")
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. البحث عن الوجه
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

        status_text = "Looking for Face..."
        status_color = (0, 0, 255) # أحمر

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                # اقتطاع منطقة الوجه لبحث العينين بداخلها فقط
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                # 2. الكشف عن العينين المفتوحتين داخل الوجه
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))

                if len(eyes) >= 2: # تم الكشف عن عينين مفتوحتين
                    frame_counter += 1
                    status_text = f"Eyes Open! Keep looking ({frame_counter}/{REQUIRED_CONSECUTIVE_FRAMES})"
                    status_color = (0, 255, 255) # أصفر
                    box_color = (0, 255, 0) # أخضر

                    # رسم مربعات العيون
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)

                    if frame_counter >= REQUIRED_CONSECUTIVE_FRAMES:
                        status_text = "Awake Confirmed! Stopping Alarm..."
                        status_color = (0, 255, 0)
                        
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        cv2.putText(frame, status_text, (30, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
                        cv2.imshow("Smart Alarm - Face & Eye Detection", frame)
                        cv2.waitKey(1000)
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                        print("\n[SUCCESS] Eyes detected open! Alarm turned off and camera closed.")
                        return
                else:
                    frame_counter = 0
                    status_text = "Eyes Closed or Looking Away!"
                    status_color = (0, 0, 255)
                    box_color = (0, 0, 255)

                # رسم المربع (Bounding Box) حول الوجه
                cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
                cv2.putText(frame, "USER FACE", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
        else:
            frame_counter = 0

        cv2.putText(frame, status_text, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

        cv2.imshow("Smart Alarm - Face & Eye Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.music.stop()
    pygame.mixer.quit()

def set_alarm():
    """ضبط وقت المنبه والانتظار حتى موعده"""
    if not verify_and_test_audio(SOUND_FILE_PATH):
        return

    while True:
        alarm_time_str = input("Enter Time (HH:MM) | أدخل الوقت (مثال 10:25): ").strip()
        period_input = input("Select Period | اختر الفترة [1 = AM (صباحاً) / 2 = PM (مساءً)]: ").strip().upper()

        if period_input in ['1', 'AM']:
            period_str = "AM"
        elif period_input in ['2', 'PM']:
            period_str = "PM"
        else:
            print(" Invalid Choice! Enter 1 for AM or 2 for PM.\n")
            continue

        full_time_str = f"{alarm_time_str} {period_str}"

        try:
            parsed_time = datetime.strptime(full_time_str, "%I:%M %p").time()
            break
        except ValueError:
            print(" Invalid format! Use HH:MM format.\n")

    now_riyadh = get_riyadh_time()
    print(f"\n Current Riyadh Time: {now_riyadh.strftime('%I:%M:%S %p')}")
    print(f" Alarm Set For: {parsed_time.strftime('%I:%M %p')}")
    print(" Waiting for alarm time...\n")

    while True:
        current_riyadh_time = get_riyadh_time().time()

        if (current_riyadh_time.hour == parsed_time.hour and 
            current_riyadh_time.minute == parsed_time.minute):
            
            print("\n ALARM RINGING! / المنبه يرن الآن!")
            
            if play_alarm_sound(SOUND_FILE_PATH):
                print("\n" + "="*50)
                while True:
                    ans = input("هل تريد فتح الكاميرا الآن لإثبات الاستيقاظ؟ [y/n]: ").strip().lower()
                    if ans in ['y', 'yes', 'نعم']:
                        start_smart_camera_verification()
                        break
                    elif ans in ['n', 'no', 'لا']:
                        print("المنبه مستمر بالرنين... اكتب 'y' عندما تكون جاهزاً لفتح الكاميرا.")
                    else:
                        print("خيار غير صحيح، يرجى كتابة y للموافقة أو n للرفض.")
            break

        time.sleep(1)

if __name__ == "__main__":
    set_alarm()