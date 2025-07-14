from typing import override
import PyImGui
from Py4GWCoreLib import ImGui
from Py4GWCoreLib.Py4GWcorelib import Utils


class StyleVar:
    def __init__(self, img_style_enum: ImGui.ImGuiStyleVar, value1: float, value2: float | None = None):
        self.img_style_enum: ImGui.ImGuiStyleVar = img_style_enum
        self.value1: float = value1
        self.value2: float | None = value2
        
    def apply(self):
        if self.value2 is not None:
            PyImGui.push_style_var2(self.img_style_enum, self.value1, self.value2)
        else:
            PyImGui.push_style_var(self.img_style_enum, self.value1)        
        
class StyleColor:
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
                
        self.rgb_tuple = (r, g, b, a)
        self.color_tuple = r / 255.0, g / 255.0, b / 255.0, a / 255.0  # Convert to RGBA float
        self.color_int = Utils.RGBToColor(r, g, b, a)    
            
    def __add__(self, value: int) -> "StyleColor":
        return StyleColor(
            min(255, max(0, self.r + value)),
            min(255, max(0, self.g + value)),
            min(255, max(0, self.b + value)),
            self.a
        )

    def __radd__(self, value: int) -> "StyleColor":
        return self.__add__(value)
    
    def copy(self,  img_color_enum: PyImGui.ImGuiCol = PyImGui.ImGuiCol.Text) -> "StyleColor":
        return StyleColor(
            self.r,
            self.g,
            self.b,
            self.a
        )        
        
class ImGuiStyleColor(StyleColor):
    def __init__(self, img_color_enum : PyImGui.ImGuiCol, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
        self.img_color_enum : PyImGui.ImGuiCol = img_color_enum
        
        self.rgb_tuple = (r, g, b, a)
        self.color_tuple = r / 255.0, g / 255.0, b / 255.0, a / 255.0  # Convert to RGBA float
        self.color_int = Utils.RGBToColor(r, g, b, a)    
    
    def apply(self):
        PyImGui.push_style_color(self.img_color_enum, self.color_tuple)
        
    def __add__(self, value: int) -> "ImGuiStyleColor":
        return ImGuiStyleColor(
            self.img_color_enum,
            min(255, max(0, self.r + value)),
            min(255, max(0, self.g + value)),
            min(255, max(0, self.b + value)),
            self.a
        )

    def __radd__(self, value: int) -> "ImGuiStyleColor":
        return self.__add__(value)
    
    def copy(self, img_color_enum : PyImGui.ImGuiCol = PyImGui.ImGuiCol.Text) -> "ImGuiStyleColor":
        return ImGuiStyleColor(
            img_color_enum,
            self.r,
            self.g,
            self.b,
            self.a
        )
    
class Style:
    instance = None
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Style, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance
    
    def __init__(self, reset: bool = False):
        if self._initialized and not reset:
            return
        
        self._initialized = True
        
        
        self.Text : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.Text, 255, 255, 255, 255)
        self.Button : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.Button, 29, 62, 106, 100)
        self.ButtonHovered : ImGuiStyleColor = self.Button.copy(PyImGui.ImGuiCol.ButtonHovered) + 100
        self.ButtonActive : ImGuiStyleColor = self.Button.copy(PyImGui.ImGuiCol.ButtonActive) + 40
        
        self.Tab : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.Tab, 29, 62, 106, 100)
        self.TabHovered : ImGuiStyleColor = self.Tab.copy(PyImGui.ImGuiCol.TabHovered) + 150
        self.TabActive : ImGuiStyleColor = self.Tab.copy(PyImGui.ImGuiCol.TabActive) + 100
        
        self.SliderGrab : ImGuiStyleColor = self.Button.copy(PyImGui.ImGuiCol.SliderGrab)
        self.SliderGrabActive : ImGuiStyleColor = self.ButtonActive.copy(PyImGui.ImGuiCol.SliderGrabActive)
        
        self.TitleBg : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.TitleBg, 0, 0, 0, 150)
        self.TitleBgActive : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.TitleBgActive, 0, 0, 0, 200)
        self.TitleBgCollapsed : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.TitleBgCollapsed, 0, 0, 0, 225)
        
        self.Border : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.Border, 255, 255, 255, 50)
        self.ScrollbarBg : ImGuiStyleColor = ImGuiStyleColor(PyImGui.ImGuiCol.ScrollbarBg, 0, 0, 0, 150)
        
        self.TabRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.TabRounding, 0.0)
        self.GrabRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.GrabRounding, 0.0)
        self.ChildRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.ChildRounding, 0.0)
        self.FrameRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.FrameRounding, 0.0)
        self.PopupRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.PopupRounding, 0.0)
        self.WindowRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.WindowRounding, 0.0)
        self.ScrollbarRounding: StyleVar = StyleVar(ImGui.ImGuiStyleVar.ScrollbarRounding, 0.0)
        
        self.Info_Icon : StyleColor = StyleColor(245, 172, 47, 255)
        self.Selected_Item : StyleColor = StyleColor(100, 100, 100, 150)
        self.Hovered_Item : StyleColor = StyleColor(128, 128, 128, 100)
        
        self.Selected_Colored_Item : StyleColor = StyleColor(255, 204, 85, 100)
        self.Hovered_Colored_Item : StyleColor = StyleColor(255, 204, 85, 25)               
        
        self.Rare_Weapons_Text : StyleColor = StyleColor(251, 62, 141, 255)
        self.Rare_Weapons_Frame : StyleColor = StyleColor(251, 62, 141, 75)
        self.Rare_Weapons_Frame_Hovered : StyleColor = StyleColor(251, 62, 141, 125)
        
        self.Low_Req_Weapons_Text : StyleColor = StyleColor(242, 136, 22, 255)
        self.Low_Req_Weapons_Frame : StyleColor = StyleColor(242, 136, 22, 75)
        self.Low_Req_Weapons_Frame_Hovered : StyleColor = StyleColor(242, 136, 22, 125)
        
    
    def push_style(self):
        for attr in dir(self):
            if isinstance(getattr(self, attr), ImGuiStyleColor):
                style_color : ImGuiStyleColor = getattr(self, attr)
                style_color.apply()
            
            elif isinstance(getattr(self, attr), StyleVar):
                style_var : StyleVar = getattr(self, attr)
                style_var.apply()
        
    def pop_style(self):
        color_pop_amount = 0
        style_pop_amount = 0
        
        for attr in dir(self):
            if isinstance(getattr(self, attr), ImGuiStyleColor):
                color_pop_amount += 1
            
            elif isinstance(getattr(self, attr), StyleVar):
                style_pop_amount += 1        
        
        if color_pop_amount > 0:
            PyImGui.pop_style_color(color_pop_amount)
            
        if style_pop_amount > 0:
            PyImGui.pop_style_var(style_pop_amount)