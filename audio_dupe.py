import speech_recognition as sr
import os
import pygame
import pyautogui
import time
from openai import OpenAI 
from datetime import datetime

#Console object for Rich Text
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from brain import brain as RimaBrain

console = Console()


# Plan is 3 panels 
# 1st panel shows status history
# 2nd panel shows voice histor
# 3rd panel on top shows rima
class CompAudioController:
    APP_ALIASES = {
        #Essentials
        "chrome": "chrome",
        "google chrome": "chrome",
        "microsoft edge": "msedge",
        "calculator": "calc",
        "vs code": "code",
        "cmd" : "cmd", 
        #Entertainment
        
        "discord": "discord",
        "steam": "steam:",
        "spotify": "spotify:",
        "my playlist" : "https://open.spotify.com/playlist/6102vJGaN9JXHyvvCRX4sE?si=cad5102178aa409c",
    }
    screenshot_path = r"C:\Users\YOHAN\OneDrive\Pictures\Screenshots"

    def __init__(self,language="en-US"):
        pygame.mixer.init()

        self.brain = RimaBrain()
        self.recognizer = sr.Recognizer()
        self.language = language
        self.is_running = True

        #Vars for stats 
        self.current_status = "Starting Rima..."
        self.last_transcript = "None"
        self.command_history = []

    def add_history_task(self, text: str, status: str = "Executed"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.command_history.append((timestamp, text, status))

        # Keep the last 5 in the array then remove the older ones
        if len(self.command_history) > 5:
            self.command_history.pop(0)


    def play_spotify_playlist(self, uri):
        os.system(f'start "" "{uri}"')

    def take_screenshot(self):
        folder_path = os.path.dirname(self.screenshot_path)
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        file_path = os.path.join(folder_path, filename)

        time.sleep(0.3)
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)

        print(f"[RIMA]: saved screeshot to {file_path}")

            
    def text_to_process_upd(self, text):
        app = text.replace("open  ", " ").strip()

        pyautogui.press("win")
        time.sleep(0.3)

        pyautogui.write(app, interval=0.5)

        pyautogui.press("enter")



    def text_to_process(self, text):
        #fun commands/quick paths
        text = text.lower()
        if "rima" in text:
            if "wake up" in text:
                image_path = r"C:\Users\YOHAN\Downloads\ironman.jpg"
                image_path2 = r"C:\Users\YOHAN\Downloads\ironman2.jpg"
                audio_path1 = r"C:\Users\YOHAN\Downloads\Recording 2026-08-05 121654.mp3"
                audio_path2 = r"C:\Users\YOHAN\Downloads\The Clash - Should I Stay or Should I Go (Official Audio).mp3"

                sound1 = pygame.mixer.Sound(audio_path1)
                sound1.set_volume(1)  
                sound1.play(loops=0)


                sound2 = pygame.mixer.Sound(audio_path2)
                sound2.set_volume(0.3) 
                sound2.play(loops=-1)
                os.system("start spotify:")
                os.system("start chrome")
                #os.system("start ")
                os.startfile(image_path)
                os.startfile(image_path2)

                self.add_history(text, "Wake Up Executed")

            #simple commands
            elif any(
                phrase in text
                for phrase in [
                    "take a screenshot",
                    "screenshot",
                    "capture screen",
                ]
            ):
                self.take_screenshot()
                return
            
            elif "shut down" in text or "shutdown" in text:
                self.add_history(text, "Shutdown Initiated")
                os.system("shutdown /s /t 0")
            
            elif "close application" in text:
                self.add_history(text, "Exited current App")
                pyautogui.hotkey("alt","f4")
                return
            
            elif "space" in text or "play song" in text or "stop song" in text:
                pyautogui.press("space")


            #Main Processor
            elif "open " in text or "play " in text:
                if "open " in text:
                    target = text.split("open ", 1)[1].strip()
                else:
                    target = text.split("play ", 1)[1].strip()

                target_app = self.APP_ALIASES.get(target, target)

                if "spotify:playlist" in target_app or "spotify:track:" in target_app:
                    self.play_spotify_playlist(target_app)
                elif ":" in target_app:
                    os.system(f'start "" "{target_app}"')
                else:
                    try:
                        os.startfile(target_app)
                    except FileNotFoundError:
                        os.system(f'start "" "{target_app}"')
            else:
                self.current_status = "RIMA is thinking..."
                answer = self.brain.reply(text)
                self.add_history_task(text, answer)
                self.current_status = "Listening..."   
        else:
            pass                 

        
        
    def listening_loop(self):

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("The audio is listening")
            while self.is_running:
                try:
                    audio = self.recognizer.listen(
                            source, timeout=4, phrase_time_limit=5
                        )

                    
                    text = self.recognizer.recognize_google(
                    audio, language=self.language
                    ).lower()

                    self.last_transcript = text 
                    print(text)

                    self.text_to_process(text)

                    if "stop" in text or "exit" in text:
                        print("RIMA: Exiting")
                        self.is_running = False

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Error was: {e}")
                    break
                

if __name__ == "__main__":

    RIMA_BANNER = r"""
    ===============================================
    ______   _____  ___ ___    _   
    |  _  \ |_   _| |  \/  |  /_\  
    | |_) |   | |   | .  . | / _ \ 
    |  _ <    | |   | |\/|  / /_\ \
    |_| \_\  _|_|_  |_|  |_/_/   \_\
    ================================================

    Welcome Han!
    """
    print(RIMA_BANNER)

    audio = CompAudioController()
    audio.listening_loop()