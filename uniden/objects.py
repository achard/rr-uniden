from dataclasses import dataclass, field
from typing import TextIO

from .base_classes import *


class ServiceType:
    """
    Stores a map of the Uniden service types with their respective indexes. Makes it easy to find them by either name or
    the arbitrary number Uniden assigned for storing in their config files.
    """
    indexes = {
        "15": "Aircraft",
        "17": "Business",
        "37": "Corrections",
        "29": "Emergency Ops",
        "4": "EMS Dispatch",
        "9": "EMS-Tac",
        "25": "EMS-Talk",
        "16": "Federal",
        "3": "Fire Dispatch",
        "8": "Fire-Tac",
        "24": "Fire-Talk",
        "13": "Ham",
        "12": "Hospitak",
        "11": "Interop",
        "2": "Law Dispatch",
        "7": "Law-Tac",
        "23": "Law-Talk",
        "31": "Media",
        "30": "Military",
        "1": "Multi-Dispatch",
        "6": "Multi-Tac",
        "22": "Multi-Talk",
        "21": "Other",
        "14": "Public Works",
        "20": "Railroad",
        "32": "Schools",
        "33": "Security",
        "26": "Transportation",
        "34": "Utilities",
        "216": "Racing Officials",
        "217": "Racing Teams",
        "208": "Custom 1",
        "209": "Custom 2",
        "210": "Custom 3",
        "211": "Custom 4",
        "212": "Custom 5",
        "213": "Custom 6",
        "214": "Custom 7",
        "215": "Custom 8"
    }
    services = {value: key for key, value in enumerate(indexes)}

    def __str__(self):
        return f"{self.value}"

    @classmethod
    def find_name(cls, index):
        return cls.indexes[index]

    @classmethod
    def find_index(cls, name):
        return cls.services[name]

    def __init__(self, value: str):
        if value.isdigit():
            self.index = value
            self.value = self.indexes[value]
        else:
            self.index = self.services[value]
            self.value = self.indexes[self.index]


@dataclass(slots=True)
class Radio:
    """
    Stores all relevant information for a given trunked radio UID
    """
    line_prefix = "UnitIds"
    name: str
    radio_id: int
    alert_tone: AlertTone
    alert_light: AlertLight

    def export(self):
        return f"UnitIds\t\t\t{self.name}\t{self.radio_id}\t{self.alert_tone}\t{self.alert_light}\n"

    def __repr__(self):
        return f"{self.name} UID: {self.radio_id}"

    @staticmethod
    def from_text(text: str):
        text = text.strip("\n")
        if text[:10] == "UnitIds\t\t\t":
            text = text[10:]
        else:
            raise TypeError("Text does not match Radio type")
        values = text.split('\t')
        return Radio(
            name=values[0],
            radio_id=int(values[1]),
            alert_tone=AlertTone((values[2], values[3])),
            alert_light=AlertLight((values[4], values[5]))
        )


@dataclass
class TrunkedChannel:
    line_prefix = "TGID"
    name: str
    avoid: UnidenBool
    tgid: int
    tdma_slot: str
    service_type: ServiceType
    delay: int
    volume_offset: int
    alert_tone: AlertTone
    alert_light: AlertLight
    number_tag: str
    p_channel: UnidenBool

    def export(self):
        return f"{self.line_prefix}\t\t\t{self.name}\t{self.avoid}\t{self.tgid}\t{self.tdma_slot}\t{self.service_type.index}\t{self.delay}\t{self.volume_offset}\t{self.alert_tone.export()}\t{self.alert_light.export()}\t{self.number_tag}\t{self.p_channel}\tAny\n"

    def __repr__(self):
        return f'{self.name} TGID: {self.tgid}'

    def __eq__(self, other):
        if isinstance(other, TrunkedChannel):
            if other.tgid == self.tgid:
                return True
        return False

    def __gt__(self, other):
        if self.tgid > other.tgid:
            return True
        return False

    def __lt__(self, other):
        if self.tgid > other.tgid:
            return True
        return False

    @classmethod
    def from_text(cls, text) -> 'TrunkedChannel':
        text = text.strip("\n")
        if text[:7] == "TGID\t\t\t":
            text = text[7:]
        else:
            raise TypeError("Text does not match TrunkedChannel type")
        values = text.split('\t')
        return TrunkedChannel(
            name=values[0],
            avoid=UnidenBool(values[1]),
            tgid=values[2],
            tdma_slot=values[3],
            service_type=ServiceType(values[4]),
            delay=values[5],
            volume_offset=values[6],
            alert_tone=AlertTone((values[7], values[8])),
            alert_light=AlertLight((values[9], values[10])),
            number_tag=values[11],
            p_channel=values[12]
        )


@dataclass(order=True, slots=True)
class TrunkedGroup:
    line_prefix = "T-Group"
    name: str
    avoid: UnidenBool
    range: UnidenRange
    quick_key: int
    channels: list[TrunkedChannel] = field(default_factory=list)

    def export(self):
        data = f"T-Group\t\t\t{self.name}\t{self.avoid}\t{self.range}\t{self.quick_key}\n"
        for channel in self.channels:
            data += channel.export()
        return data

    def __repr__(self):
        return f"TrunkedGroup {self.name} QK {self.quick_key} [{len(self.channels)} Channels]"

    @staticmethod
    def from_text(text):
        text = text.strip("\n")
        if text[:10] == "T-Group\t\t\t":
            text = text[10:]
        else:
            raise TypeError("Text does not match TrunkedGroup type")
        values = text.split('\t')
        return TrunkedGroup(
            name=values[0],
            avoid=UnidenBool(values[1]),
            range=UnidenRange(values[2], values[3], values[4], values[5]),
            quick_key=values[6]
        )

    @classmethod
    def from_file(cls, file: TextIO):
        group = cls.from_text(file.readline())
        while True:
            file_pos = file.tell()
            line = file.readline()
            match line.split("\t")[0]:
                case TrunkedChannel.line_prefix:
                    group.channels.append(TrunkedChannel.from_text(line))
                case _:
                    file.seek(file_pos)
                    return group


@dataclass
class ConventionalFrequency:
    line_prefix = "C-Freq"
    name: str
    avoid: UnidenBool
    freq: int
    modulation: str
    audio_option: str
    service_type: ServiceType
    attenuator: UnidenBool
    delay: int
    volume_offset: int
    alert_tone: AlertTone
    alert_light: AlertLight
    number_tag: str
    p_channel: UnidenBool

    def export(self):
        return f"{self.line_prefix}\t\t\t{self.name}\t{self.avoid}\t{self.freq}\t{self.modulation}\t{self.audio_option}\t{self.service_type.index}\t{self.attenuator}\t{self.delay}\t{self.volume_offset}\t{self.alert_tone.export()}\t{self.alert_light.export()}\t{self.number_tag}\t{self.p_channel}\n"

    def __repr__(self):
        return f'{self.name} Frequency: {self.freq / 1_000_000}'

    def __eq__(self, other):
        if isinstance(other, ConventionalFrequency):
            if other.freq == self.freq:
                return True
        return False

    def __gt__(self, other):
        if self.freq > other.freq:
            return True
        return False

    def __lt__(self, other):
        if self.freq > other.freq:
            return True
        return False

    @classmethod
    def from_text(cls, text) -> 'ConventionalFrequency':
        text = text.strip("\n")
        if text[:9] == "C-Freq\t\t\t":
            text = text[9:]
        else:
            raise TypeError("Text does not match TrunkedChannel type")
        values = text.split('\t')
        return ConventionalFrequency(
            name=values[0],
            avoid=UnidenBool(values[1]),
            freq=values[2],
            modulation=values[3],
            audio_option=values[4],
            service_type=ServiceType(values[5]),
            attenuator=values[6],
            delay=values[7],
            volume_offset=values[8],
            alert_tone=AlertTone((values[9], values[10])),
            alert_light=AlertLight((values[11], values[12])),
            number_tag=values[13],
            p_channel=values[14]
        )


@dataclass(order=True, slots=True)
class ConventionalGroup:
    line_prefix = "C-Group"
    name: str
    avoid: UnidenBool
    range: UnidenRange
    quick_key: int
    channels: list[ConventionalFrequency] = field(default_factory=list)
    filter: str = "Global"

    def export(self):
        data = f"C-Group\t\t\t{self.name}\t{self.avoid}\t{self.range}\t{self.quick_key}\t{self.filter}\n"
        for channel in self.channels:
            data += channel.export()
        return data

    def __repr__(self):
        return f"TrunkedGroup {self.name} QK {self.quick_key} [{len(self.channels)} Channels]"

    @classmethod
    def from_text(cls, text):
        text = text.strip("\n")
        if text[:10] == f"{cls.line_prefix}\t\t\t":
            text = text[10:]
        else:
            raise TypeError("Text does not match TrunkedGroup type")
        values = text.split('\t')
        return ConventionalGroup(
            name=values[0],
            avoid=UnidenBool(values[1]),
            range=UnidenRange(values[2], values[3], values[4], values[5]),
            quick_key=values[6],
            filter=values[7]
        )

    @classmethod
    def from_file(cls, file: TextIO):
        group = cls.from_text(file.readline())
        while True:
            file_pos = file.tell()
            line = file.readline()
            match line.split("\t")[0]:
                case ConventionalFrequency.line_prefix:
                    group.channels.append(ConventionalFrequency.from_text(line))
                case _:
                    file.seek(file_pos)
                    return group


class SiteFrequency(UnidenTextType):
    line_prefix = "T-Freq"


class BandPlan(UnidenTextType):
    line_prefix = "BandPlan_P25"
    tabs = 2


@dataclass
class Site(UnidenTextType):
    line_prefix = "Site"
    frequencies: list = field(default_factory=list)
    bandplan: BandPlan | None = None

    def export(self):
        data = f"{self.line_prefix}{self.tabs_text}{self.value}\n"
        if self.bandplan:
            data += self.bandplan.export()
        for freq in self.frequencies:
            data += freq.export()
        return data

    @classmethod
    def from_file(cls, file: TextIO):
        site = Site.from_text(file.readline())
        while True:
            file_pos = file.tell()
            line = file.readline()
            match line.split("\t")[0]:
                case SiteFrequency.line_prefix:
                    site.frequencies.append(SiteFrequency.from_text(line))
                case BandPlan.line_prefix:
                    site.bandplan = BandPlan.from_text(line)
                case _:
                    file.seek(file_pos)
                    return site


@dataclass
class DQKStatus:
    line_prefix = "DQKs_Status"
    tabs = 2
    statuses: list = field(default_factory=list)

    def export(self):
        return self.line_prefix + "\t" * self.tabs + "\t".join(self.statuses) + '\n'

    @classmethod
    def from_text(cls, text):
        text = text.strip("\n")
        offset = len(cls.line_prefix) + cls.tabs
        if text[:offset] == f"{cls.line_prefix}\t\t":
            text = text[offset:]
        else:
            raise TypeError(f"Text does not match {cls.__name__} type")
        return cls(text.split("\t"))


@dataclass
class System:
    system_types = ["Trunk", "Conventional"]
    line_prefix: str
    value: str
    dqk_status: DQKStatus | None = None
    groups: list[TrunkedGroup | ConventionalGroup] = field(default_factory=list)
    sites: list = field(default_factory=list)
    radios: list[Radio] = field(default_factory=list)

    def export(self):
        data = f"{self.line_prefix}\t\t\t{self.value}\n"
        if self.dqk_status is not None:
            data += self.dqk_status.export()
        for radio in self.radios:
            data += radio.export()
        for site in self.sites:
            data += site.export()
        for group in self.groups:
            data += group.export()
        return data

    @classmethod
    def from_text(cls, text) -> 'System':
        text = text.strip("\n")
        for system_type in cls.system_types:
            if text[:len(system_type) + 3] == f"{system_type}\t\t\t":
                text = text[len(system_type) + 3:]
                break
        else:
            raise TypeError("Text does not match System type")
        return System(line_prefix=system_type, value=text)

    @classmethod
    def from_file(cls, file: TextIO):
        line = file.readline()
        if line.startswith(TrunkedSystem.line_prefix):
            system = System.from_text(line)
        elif line.startswith(ConventionalSystem.line_prefix):
            system = System.from_text(line)
        else:
            raise TypeError("Text does not match System type")
        while True:
            file_pos = file.tell()
            line = file.readline()
            match line.split("\t")[0]:
                case Radio.line_prefix:
                    system.radios.append(Radio.from_text(line))
                case TrunkedGroup.line_prefix:
                    file.seek(file_pos)
                    system.groups.append(TrunkedGroup.from_file(file))
                case ConventionalGroup.line_prefix:
                    file.seek(file_pos)
                    system.groups.append(ConventionalGroup.from_file(file))
                case DQKStatus.line_prefix:
                    system.dqk_status = DQKStatus.from_text(line)
                case Site.line_prefix:
                    file.seek(file_pos)
                    system.sites.append(Site.from_file(file))
                case ConventionalSystem.line_prefix:
                    print("Found next system, continuing")
                    file.seek(file_pos)
                    return system
                case TrunkedSystem.line_prefix:
                    print("Found next system, continuing")
                    file.seek(file_pos)
                    return system
                case "":
                    return system
                case _:
                    print(f'Unknown line found in the text file:')
                    print(line)
                    file.seek(file_pos)
                    return system


class ConventionalSystem(System):
    line_prefix = "Conventional"


class TrunkedSystem(System):
    line_prefix = "Trunk"


@dataclass
class UnidenFile:
    target_model: str = "BCDx36HP"
    format_version: str = "1.00"
    systems: list = field(default_factory=list)

    @staticmethod
    def from_file(filename):
        with open(filename, 'r') as config_file:
            line = config_file.readline()
            if line[:12] == "TargetModel\t":
                target_model = line[12:]
                line = config_file.readline()
                if line[:14] == "FormatVersion\t":
                    format_version = line[14:]
                    uniden_file = UnidenFile(target_model=target_model, format_version=format_version)
                    while True:
                        file_pos = config_file.tell()
                        next_line = config_file.readline()
                        if next_line.startswith(TrunkedSystem.line_prefix):
                            config_file.seek(file_pos)
                            uniden_file.systems.append(System.from_file(config_file))
                        if next_line.startswith(ConventionalSystem.line_prefix):
                            config_file.seek(file_pos)
                            uniden_file.systems.append(System.from_file(config_file))
                        elif next_line == "":
                            return uniden_file
                        else:
                            raise ValueError(f"Unknown entry type found in config file:\r\n{next_line}")
        return uniden_file

    def export(self) -> str:
        output_data = f"TargetModel\t{self.target_model}"
        output_data += f"FormatVersion\t{self.format_version}"
        for system in self.systems:
            output_data += system.export()
        return output_data

    def to_file(self, filename):
        with open(filename, 'w') as config_file:
            config_file.write(self.export())
