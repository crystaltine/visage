from element import Element
from utils import fcode, convert_to_chars
from typing import List, Unpack
from globalvars import Globals
from logger import Logger

class Div(Element):
    """
    A general div class with customizable styling options.
    """
    
    class Attributes(Element.Attributes):
        id: str | None
        class_str: str | None
        style_str: str | None
        children: List["Element"]
    
    class StyleProps(Element.StyleProps):
        """ A schema of style options for divs. """
        position: str
        visible: bool
        left: str
        top: str
        width: str
        height: str
        right: str
        bottom: str
        padding_top: int
        padding_right: int
        padding_bottom: int
        padding_left: int
        padding: int
        bg_color: str | tuple
    
    SUPPORTS_CHILDREN = True
    DEFAULT_STYLE: "Div.StyleProps" = {
        "position": "relative",
        "visible": True,
        "left": "0%",
        "top": "0%",
        "width": "100%",
        "height": "100%",
        "right": None, # calculated from "left" and "width"
        "bottom": None, # calculated from "top" and "height"
        "padding_top": 0,
        "padding_right": 0,
        "padding_bottom": 0,
        "padding_left": 0,
        "padding": 0,
        "bg_color": (255, 255, 255), # can be hex code, rgb tuple, or 'transparent'
    }

    def __init__(self, **attrs: Unpack["Attributes"]):
        """ Keyword arguments: see `Div.Attributes`.
        Note: For style options that conflict, such as "top"/"bottom" and "height", the ones listed higher
        in the default dict above take precedence. Specifically, for dimensions/positioning, here are the rules:
        
        - if both top and bottom are provided, height is completely ignored.
        - if one of top or bottom, and height, are provided, the other top/bottom position is calculated from the height.
        - this is true for left/right/width as well.
        - therefore, at least two of the three positioning params for each dimension must be not None.
        
        (don't worry about not setting options, they have default values. Just don't set more than one of the
        position options (height/top/bottom, width/left/right) explicitly to None.
        
        Provide either percents or characters for the dimension values.
        Percents must be expressed as strings, e.g. '50%'. Characters can
        be either raw numbers or strings ending in 'ch', e.g. 50 or '50ch'.
        """
        
        super().__init__(**attrs) # should ignore any unknown attributes that are provided
        
        # assert that ONE of left/right and ONE of top/bottom is provided
        assert (self.style.get("left") is not None or self.style.get("right") is not None), "[Div]: At least one of left or right must not be None."
        assert (self.style.get("top") is not None or self.style.get("bottom") is not None), "[Div]: At least one of top or bottom must not be None."
        
        self.children: List["Element"] = attrs.get("children", [])
        self._bg_fcode = fcode(background=self.style.get("bg_color")) if self.style.get("bg_color") != "transparent" else None
        #Logger.log(f"{self}'s children on init: {self.children}")
    
    def render(self, container_left: int = None, container_top: int = None, container_right: int = None, container_bottom: int = None):

        Logger.log(f"<BEGIN DIV render func>")
        Logger.log(f"Div render params: {container_left=} {container_top=} {container_right=} {container_bottom=}")
        container_left, container_top, container_right, container_bottom = self.get_true_container_edges(container_left, container_top, container_right, container_bottom)
        
        container_width = container_right - container_left
        container_height = container_bottom - container_top
        
        self.client_top = container_top + (convert_to_chars(container_height, self.style.get("top")) if self.style.get("top") is not None
            else container_bottom - convert_to_chars(container_height, self.style.get("bottom")) - convert_to_chars(container_height, self.style.get("height")))
        self.client_bottom = (container_bottom - convert_to_chars(container_height, self.style.get("bottom")) if self.style.get("bottom") is not None
            else container_top + convert_to_chars(container_height, self.style.get("top")) + convert_to_chars(container_height, self.style.get("height")))
        
        self.client_left = container_left + (convert_to_chars(container_width, self.style.get("left")) if self.style.get("left") is not None
            else container_right - convert_to_chars(container_width, self.style.get("right")) - convert_to_chars(container_width, self.style.get("width")))
        self.client_right = (container_right - convert_to_chars(container_width, self.style.get("right")) if self.style.get("right") is not None
            else container_left + convert_to_chars(container_width, self.style.get("left")) + convert_to_chars(container_width, self.style.get("width")))
        
        self.client_width = self.client_right - self.client_left 
        self.client_height = self.client_bottom - self.client_top
        
        Logger.log(f"Div (id={self.id}) given top: {self.style.get('top')}, bottom: {self.style.get('bottom')}, height: {self.style.get('height')}, calced client_top={self.client_top}, client_bottom={self.client_bottom}, client_height={self.client_height}")
        Logger.log(f"^ container top: {container_top}, bottom: {container_bottom}, height: {container_height}")
        
        if not self.style.get("visible"): return
        
        # draw the rectangle IF it is not transparent.
        if self._bg_fcode:
            for i in range(self.client_top, self.client_bottom):
                with Globals.__vis_document__.term.hidden_cursor():
                    #Logger.log(f"drawing strip of div (id={self.id}) at y={i}")
                    print(Globals.__vis_document__.term.move_xy(self.client_left, i) + self._bg_fcode + " " * self.client_width, end="")
                    
        # render children
        for child in self.children:
            
            if self is child: continue # ??? - for some reason using this func adds a self pointer to its own children. try fixing later
            
            Logger.log(f"Div rendering children: cli_left, cli_top, cli_right, cli_bottom: {self.client_left=} {self.client_top=} {self.client_right=} {self.client_bottom=}")
            
            general_padding = convert_to_chars(container_width, self.style.get("padding")) if self.style.get("padding") is not None else 0
            
            child.render(
                self.client_left + convert_to_chars(container_width, self.style.get("padding_left")) or general_padding,
                self.client_top + convert_to_chars(container_height, self.style.get("padding_top")) or general_padding,
                self.client_right - convert_to_chars(container_width, self.style.get("padding_right")) or general_padding,
                self.client_bottom - convert_to_chars(container_height, self.style.get("padding_bottom")) or general_padding
            )
             
    def add_child(self, child: "Element", index: int = None):
        """
        Adds a child div at the specified index, which means where on the component tree it will be placed.
        If index is None, it will be added to the end of the list of children.
        
        @TODO - for some reason, this leads to a recursion error because objects get added all over the document. IDK why!!
        (probably pointer/inheritance issue)
        """
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
            
        #Logger.log(f"Added child to {self}: {child}")