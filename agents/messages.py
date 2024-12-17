from dataclasses import dataclass

@dataclass
class Message:
	content: str = ""
	data: str = "{}"