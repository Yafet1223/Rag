class Rulelayer:
    def __init__(self):
        self.rules=[
            "i  studied",
            "i slept",
            "i worked",
            "today i",
            "yesterday i"
        ]
        self.profile=[
            "i prefer",
            "i usually",
            "i always",
            "i struggle with",
            "i am good at"

        ]
        self.ignore=[
            "ok",
            "lol",
            "haha",
            "nice",
            "cool"
 ]
def normalize(self,message:str):
    return message.lower().strip()
def is_event(self,message:str):
    for signal in self.rules:
        if signal in self.rules:
            return True
        return False
def is_profile(Self,message:str):
    for signal in self.profile:
        if signal  in self.profile:
            return True
        return False
def is_ignore(Self,message:Str):
    for signal in self.ignore:
        if signal in self.ignore:
            return True
        return False
def classify(self, message:str):
    message = self.normalize(message):
    if self.is_ignore(message):
        return "ignore"
    
     
        