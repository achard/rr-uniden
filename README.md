# rr-uniden

A Python library for parsing, manipulating, and exporting Uniden scanner configuration files (`.hpd` format). Also includes utilities for importing trunked channel data from [RadioReference](https://www.radioreference.com/) CSV exports.

Targets Uniden BCD436HP/BCD536HP scanners (Sentinel software `.hpd` files).

## Requirements

- Python 3.10+
- No external runtime dependencies (stdlib only)

## Installation

Clone the repo and use it directly — there's no package distribution yet.

```bash
git clone https://github.com/achard/rr-uniden.git
cd rr-uniden
```

## Usage

### Parse an existing .hpd file

```python
from uniden import UnidenFile

config = UnidenFile.from_file("my_scanner.hpd")

for system in config.systems:
    print(f"{system.line_prefix}: {system.value}")
    for group in system.groups:
        print(f"  Group: {group.name} ({len(group.channels)} channels)")
        for channel in group.channels:
            print(f"    {channel}")
```

### Build a configuration programmatically

```python
from uniden import UnidenFile
from uniden.objects import TrunkedChannel, TrunkedGroup, System, ServiceType

ch = TrunkedChannel(tgid=100, name="Fire Dispatch", service_type=ServiceType("Fire Dispatch"))
group = TrunkedGroup(name="Fire", quick_key=1, channels=[ch])
system = System(line_prefix="Trunk", value="County P25", groups=[group])

config = UnidenFile(systems=[system])
config.to_file("output.hpd")
```

### Import RadioReference CSV data

RadioReference allows exporting trunked system talkgroups as CSV. This library can parse those exports:

```python
from radioreference import TrunkedChannelDict

channels = TrunkedChannelDict.import_csv("radioreference_export.csv")

for tgid, channel in channels.items():
    print(f"{channel.alpha_tag} ({channel.category}) - TGID {channel.tgid}")
```

### Look up service types

```python
from uniden.objects import ServiceType

st = ServiceType("Fire Dispatch")
print(st.index)  # "3"

st = ServiceType(15)
print(st.value)  # "Aircraft"
```

## .hpd File Structure

The `.hpd` format is a tab-delimited text file used by Uniden's Sentinel software. The hierarchy looks like:

```
TargetModel     BCDx36HP
FormatVersion   1.00
Trunk           <system name>
  DQKs_Status   <status list>
  UnitIds       <radio UID>
  Site          <site info>
    BandPlan_P25  <band plan pairs>
    T-Freq        <site frequency>
  T-Group       <group/department>
    TGID          <talkgroup channel>
Conventional    <system name>
  C-Group       <group>
    C-Freq        <frequency>
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install pytest flake8

# Run tests
pytest

# Run a single test
pytest test_objects.py::test_name

# Lint
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## License

See repository for license details.
