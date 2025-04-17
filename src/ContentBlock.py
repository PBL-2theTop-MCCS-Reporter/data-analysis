from enum import Enum

class Alignment(Enum):
    LEFT = "Left"
    CENTER = "Center"

class ContentBlock:
    def __init__(self,
                 text,
                 bold=False,
                 underline=False,
                 font_size=10,
                 color=None,
                 indent=False,
                 heading_level=None,
                 alignment=Alignment.LEFT,
                 new_line=False,
                 new_paragraph=False):
        self.text = text
        self.bold = bold
        self.underline = underline
        self.font_size = font_size
        self.color = color
        self.indent = indent
        self.heading_level = heading_level
        self.alignment = alignment
        self.new_line = new_line
        self.new_paragraph = new_paragraph