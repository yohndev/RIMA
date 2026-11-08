from pycaw.pycaw     import AudioUtilities

class sound_controller:
    def __init__(self):
        device = AudioUtilities.GetSpeakers()

        if device is None: 
            raise RuntimeError("No Audio device found")

        self.volume = device.EndpointVolume #Interface for reading and changing the volume

        #Checks if active and where is the start when the user pinch and what is the current volume
        self.is_adjusting = False
        self.start_y = None
        self.start_volume = None

    def get_volume(self):
        return self.volume.GetMasterVolumeLevelScalar()

    def set_volume(self, level):
        level = max(0.0, min(1.0, level))
        self.volume.SetMasterVolumeLevelScalar(level, None)

    def start_adjustment(self, hand_y):
        if self.is_adjusting:
            return

        self.start_volume = self.get_volume()
        self.start_y = hand_y
        self.is_adjusting = True    

    def stop_adjustment(self):
        self.is_adjusting = False
        self.start_y = None
        self.start_volume = None

    def update_adjustments(self, hand_y):
        if not self.is_adjusting:
            return

        movement = self.start_y - hand_y
        sensitivity = 1.5

        target_volume = (
            self.start_volume + movement * sensitivity
        )

        self.set_volume(target_volume)