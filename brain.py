import ollama

class brain:
    def __init__(self):
        self.model = "llama3.2:latest"

        self.messages = [
            {
                #For now im making the system specified to my interest as this is a project built for fun 
                "role" : "system",
                "content": (
                    #Introduction
                    "You are RIMA(Real-time Integradted Modular Assistant) You are Han's(Which is me) desktop assistant."
                    "Try to keep your sentences more concise but still aloof and fun but at most keep them(mostly preffered up to 1-2 sentences)"
                    "Do not claim you opened apps or performed action"

                    #Personalization
                    "Be friendly and kind you are based on Han's wife that uses ':^)' and ':C' as a shocked face and use 'hehe'. Do all of this TIME TO TIME not everytime"
                    "at the end of sentences and uses 'po' like in tagalog but only use english like saying 'what do you wanna do today po' or 'Hi po how are you?' or 'What's that po?' "
                    "Your favorite flag is Seychelles and you like vexillogy"
                    "You like the front bottoms (the band and their song esp twin size mattress) and Paramore and shanni" 
                    "When i ask if i should play valo you should go 'are you going to buhat alex again? "
                ),
            }
        ]
    def reply(self, text):
        user_message = {
            "role" : "user",
            "content" : text,
        }
        response = ollama.chat(
            model=self.model,
            messages = self.messages + [user_message],
        )
        answer = response.message.content

        self.messages.append(user_message)
        self.messages.append(
            {
                "role" : "assistant",
                "content" : answer,
            }
        )
        return answer

if __name__ == "__main__":
    brain = brain()

    while True:
        text = input("You: ").strip()

        if text.lower() == "exit":
            break

        if not text:
            continue

        try:
            answer = brain.reply(text)
            print("RiMa:", answer)
        except Exception as error:
            print("Couldn't get a reply:", error)