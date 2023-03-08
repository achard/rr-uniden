from dataclasses import dataclass


class UnidenBool:
    def __init__(self, value: str | bool):
        if isinstance(value, bool):
            self.value = value
        elif isinstance(value, str):
            if value == "On":
                self.value = True
            if value == "Off":
                self.value = False
            else:
                raise ValueError
        else:
            raise ValueError

    def __str__(self):
        if self.value:
            return "On"
        return "Off"


class UnidenRange:
    def __init__(self, lat: float = 0, long: float = 0, distance: float = 0, shape="Circle"):
        self.latitude = lat
        self.longitude = long
        self.distance = distance
        self.shape = shape

    def __str__(self):
        return f"{self.latitude}\t{self.latitude}\t{self.distance}\t{self.shape}"


class AlertTone:
    def __init__(self, value: tuple[str | int, str | int]):
        self.value, self.volume = value

    @property
    def textvalue(self):
        if self.value == 0:
            return "Off"
        else:
            return str(self.value)

    @property
    def textvolume(self):
        if self.volume == 0:
            return "Auto"
        else:
            return str(self.volume)

    def __str__(self):
        return f"{self.textvalue}\t{self.textvolume}"

    def export(self):
        return self.__str__()


class AlertLight:

    def __init__(self, value: tuple[str, str]):
        colours = ["Off", "Red", "Green", "Blue", "White", "Cyan", "Magenta", "Yellow"]
        states = ["On", "Slow Blink", "Fast Blink"]
        self.colour, self.state = value
        if self.colour not in colours:
            self.colour = "Off"
        if self.state not in states:
            self.state = "On"

    def __str__(self):
        return f"{self.colour}\t{self.state}"

    def __repr__(self):
        return f"{self.state} {self.colour}"

    def export(self):
        return self.__str__()


@dataclass
class UnidenTextType:
    line_prefix = ""
    tabs = 3
    value: str

    def export(self):
        return f"{self.line_prefix}{self.tabs_text}{self.value}\n"

    @property
    def tabs_text(self):
        return "\t" * self.tabs

    @classmethod
    def from_text(cls, text):
        text = text.strip("\n")
        offset = len(cls.line_prefix) + cls.tabs
        if text[:offset] == cls.line_prefix + "\t" * cls.tabs:
            text = text[offset:]
        else:
            raise TypeError(f"Text does not match {cls.__name__} type")
        return cls(text)
