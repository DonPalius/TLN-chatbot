import speech_recognition as sr
class SpeechToText:
    
    def getSpeech(self,check):
        r = sr.Recognizer()
        m = sr.Microphone()
        self.response = None
        self.check = check
        
        try:
            print("A moment of silence, please...")
            with m as source: r.adjust_for_ambient_noise(source)
            print("Set minimum energy threshold to {}".format(r.energy_threshold))
            print("Say something!")
            with m as source: audio = r.listen(source,timeout=5, phrase_time_limit=5)
            print("Got it! Now to recognize it...")
            try:
                
                # recognize speech using Google Speech Recognition
                self.response = r.recognize_google(audio)
                print(f"{self.response} response registered")
                return self.response
                
                
            except sr.UnknownValueError:
                print("Oops! Didn't catch that")
            except sr.RequestError as e:
                print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

        except sr.WaitTimeoutError:
            print("You took to long to answer!")
            return None
        except KeyboardInterrupt:
            return  self.response

        return   self.response