
from pydantic import BaseModel
from datetime import datetime
 
class ChatMessage(BaseModel):
    role:str
    content:str
    timestamp:datetime

