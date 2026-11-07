import threading
import cv2
import pyautogui

from rich.live import Live

from audio_cli import CompAudioController, console
from vision import CompVisionController

def main():
    audio = CompAudioController()
    camera = None
    listener = None

    try:
        camera = CompVisionController()
        
        listener = threading.Thread(
        target=audio.audio_listener_worker,
        daemon=True,
        )
        listener.start()    

        with Live(
            audio.generate_layout(),
            console=console,
            refresh_per_second=10,
        ) as dashboard:

            while audio.is_running:
                 #Stop if error occurs for microphone
                if not listener.is_alive():
                      break

                frame, landmarks = camera.get_frame()

                
                if frame is None:
                    console.print("Camera disconnected or unavailable.")
                    break

                cv2.imshow("RIMA Camera — Q to quit", frame)
                dashboard.update(audio.generate_layout())
            
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

    except pyautogui.FailSafeException:
        console.print("RIMA emergency stop activated.")
    except KeyboardInterrupt:
        console.print("Stopping RIMA...")

    finally:
        audio.is_running = False

        try:
            if camera is not None:
                camera.release()
        finally:
            cv2.destroyAllWindows()

            if listener is not None:
                listener.join(timeout=2)

            console.print("RIMA Shutting down.")


if __name__ == "__main__":
    main()