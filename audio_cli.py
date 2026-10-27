import speech_recognition as sr
import os
import pygame
import pyautogui
import time
import threading
from datetime import datetime

#Console object for Rich Text
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

console = Console()

RIMA_BANNER = r"""===============================================
______   _____  ___ ___    _   
|  _  \ |_   _| |  \/  |  /_\  
| |_) |   | |   | .  . | / _ \ 
|  _ <    | |   | |\/|  / /_\ \
|_| \_\  _|_|_  |_|  |_/_/   \_\
===============================================

Welcome Han!"""

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
        
        self.recognizer = sr.Recognizer()
        self.language = language
        self.is_running = True

        #Vars for stats 
        self.current_status = "Starting Rima..."
        self.last_transcript = "None"
        self.command_history = []
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0

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
        #simple commands
        if any(
            phrase in text
            for phrase in [
                "take a screenshot",
                "screenshot",
                "capture screen",
            ]
        ):
            self.add_history_task(text, "Screen Shot Taken")
            self.take_screenshot()
            return
        elif "hi" in text:
            self.add_history_task(text, "Hi Han !!")
            return
        
        elif "shut down" in text or "shutdown" in text:
            self.add_history_task(text, "Shutdown Initiated")
            os.system("shutdown /s /t 0")
        
        elif "close application" in text:
            self.add_history_task(text, "Exited current App")
            pyautogui.hotkey("alt","f4")
            return
        
        elif "space" in text or "play song" in text or "stop song" in text:
            pyautogui.press("space")

        elif "alex" in text:
            self.add_history_task(text, "Kys Alex")
            return


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
                self.add_history_task(text, f"Opened: {target}")
            else:
                try:
                    self.add_history_task(text, f"Opened: {target}")
                    os.startfile(target_app)
                except FileNotFoundError:
                    os.system(f'start "" "{target_app}"')


    def audio_listener_worker(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.current_status = "Listening for audio..."

            while self.is_running:
                try:
                    self.current_status = "Listening..."
                    audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=5)
                    
                    self.current_status = "Recognizing speech..."
                    text = self.recognizer.recognize_google(audio, language=self.language).lower()

                    if "stop" in text or "exit" in text:
                        self.current_status = "Stopping..."
                        self.add_history_task(text, "Exit Command")
                        self.is_running = False
                        break

                    self.text_to_process(text)

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    self.current_status = f"Error: {e}"
                    time.sleep(1)

    def generate_layout(self) -> Layout:
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=11),
            Layout(name="body")
        )

        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )

        header_text = Text(RIMA_BANNER, style="bold cyan")
        
        centered_banner = Align.center(header_text)
        
        header_panel = Panel(centered_banner, border_style="cyan")
        layout["header"].update(header_panel)

        self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
        spinner = self.spinner_frames[self.spinner_idx]

        monitor_text = Text()
        monitor_text.append("Status: ", style="bold white")
        monitor_text.append(f"{spinner} {self.current_status}\n\n", style="bold yellow")
        
        monitor_text.append("Last Heard:\n", style="bold white")
        monitor_text.append(f"\"{self.last_transcript}\"\n\n", style="italic cyan")

        monitor_text.append("Commands:\n", style="bold white")
        monitor_text.append("• Terminate One Eyed Man\n", style="dim white")
        monitor_text.append("• open ______(Any Existing app)\n", style="dim white")
        monitor_text.append("• play my playlist\n", style="dim white")
        monitor_text.append("• take screenshot\n", style="dim white")
        monitor_text.append("• wake up\n", style="dim white")
        monitor_text.append("• exit / stop\n", style="dim red")

        left_panel = Panel(monitor_text, title="[bold blue]Monitor[/bold blue]", border_style="blue")
        layout["left"].update(left_panel)

        history_table = Table(expand=True, border_style="bright_black")
        history_table.add_column("Time", style="dim white", width=10)
        history_table.add_column("Voice Command", style="bold white")
        history_table.add_column("Result Status", style="green")

        for entry in reversed(self.command_history):
            history_table.add_row(entry[0], entry[1], entry[2])

        right_panel = Panel(history_table, title="[bold magenta]Activity Log[/bold magenta]", border_style="magenta")
        layout["right"].update(right_panel)

        return layout
    
    def listening_loop(self):
        listener_thread = threading.Thread(target=self.audio_listener_worker, daemon=True)
        listener_thread.start()

        console.clear()
        with Live(self.generate_layout(), refresh_per_second=10, console=console) as live:
            while self.is_running:
                time.sleep(0.1)
                live.update(self.generate_layout())

        console.print("[bold red][RIMA]: Shutdown complete.[/bold red]")


if __name__ == "__main__":
    print(RIMA_BANNER)
    time.sleep(1.5) 

    audio = CompAudioController()
    audio.listening_loop()