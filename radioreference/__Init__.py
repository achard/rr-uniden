from dataclasses import dataclass
import csv


class TrunkedChannelDict(dict):

    @classmethod
    def import_csv(cls, file):
        self = cls()
        with open(file, newline='', encoding='utf-8-sig') as channel_file:
            channel_reader = csv.DictReader(channel_file, dialect='excel')
            for line in channel_reader:
                self[line['Decimal']] = TrunkedChannel(
                    tgid=line['Decimal'], alpha_tag=line['Alpha Tag'], mode=line['Mode'],
                    description=line['Description'], tag=line['Tag'], category=line['Category']
                )
        return self


@dataclass
class TrunkedChannel:
    tgid: int
    alpha_tag: str
    mode: str
    description: str
    tag: str
    category: str

    def __str__(self):
        return f"{self.tgid}: {self.alpha_tag}"

    @property
    def tgid_hex(self):
        return hex(self.tgid)
