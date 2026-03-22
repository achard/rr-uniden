import io
import pytest
from uniden import UnidenBool, UnidenRange, AlertLight, AlertTone, ServiceType
from uniden.objects import (
    Radio, TrunkedChannel, TrunkedGroup, ConventionalFrequency,
    ConventionalGroup, SiteFrequency, BandPlan, Site, DQKStatus,
    System, UnidenFile, TrunkedSystem, ConventionalSystem,
)
from uniden.base_classes import UnidenTextType


# ── UnidenBool ──────────────────────────────────────────────

def test_uniden_bool():
    x = UnidenBool()
    assert x.value is False
    x = UnidenBool('Off')
    assert x.value is False
    x = UnidenBool('On')
    assert x.value is True
    x = UnidenBool(False)
    assert str(x) == "Off"
    assert x.value is False
    x = UnidenBool(True)
    assert str(x) == 'On'
    assert x.value is True


def test_uniden_bool_invalid_string():
    with pytest.raises(ValueError):
        UnidenBool("Maybe")


def test_uniden_bool_invalid_type():
    with pytest.raises(ValueError):
        UnidenBool(42)


# ── UnidenRange ─────────────────────────────────────────────

def test_uniden_range():
    x = UnidenRange()
    assert str(x) == "0.000000\t0.000000\t0.0\tCircle"


def test_uniden_range_custom():
    x = UnidenRange(lat="40.712800", long="-74.006000", distance="5.0", shape="Square")
    assert x.latitude == "40.712800"
    assert x.longitude == "-74.006000"
    assert x.distance == "5.0"
    assert x.shape == "Square"


# ── AlertTone ───────────────────────────────────────────────

def test_alert_tone():
    x = AlertTone()
    assert x.value == 0
    assert x.volume == 0
    assert str(x) == "Off\tAuto"


def test_alert_tone_with_values():
    x = AlertTone((3, 7))
    assert x.value == 3
    assert x.volume == 7
    assert str(x) == "3\t7"
    assert x.export() == "3\t7"


def test_alert_tone_textvalue_off():
    x = AlertTone((0, 5))
    assert x.textvalue == "Off"
    assert x.textvolume == "5"


# ── AlertLight ──────────────────────────────────────────────

def test_alert_light():
    x = AlertLight()
    assert x.state == "On"
    assert x.colour == "Off"
    assert str(x) == "Off\tOn"


def test_alert_light_with_values():
    x = AlertLight(("Red", "Fast Blink"))
    assert x.colour == "Red"
    assert x.state == "Fast Blink"
    assert str(x) == "Red\tFast Blink"
    assert x.export() == "Red\tFast Blink"


def test_alert_light_invalid_colour_defaults():
    x = AlertLight(("Purple", "On"))
    assert x.colour == "Off"


def test_alert_light_invalid_state_defaults():
    x = AlertLight(("Red", "Strobe"))
    assert x.state == "On"


def test_alert_light_repr():
    x = AlertLight(("Green", "Slow Blink"))
    assert repr(x) == "Slow Blink Green"


# ── ServiceType ─────────────────────────────────────────────

def test_service_types():
    x = ServiceType()
    assert str(x) == "Other"
    assert x.index == "21"
    assert x.value == "Other"
    x = ServiceType(15)
    assert str(x) == "Aircraft"
    x = ServiceType('Other')
    assert x.index == "21"


def test_service_type_by_name():
    x = ServiceType("Fire Dispatch")
    assert x.index == "3"
    assert x.value == "Fire Dispatch"


def test_service_type_by_string_index():
    x = ServiceType("2")
    assert x.value == "Law Dispatch"
    assert x.index == "2"


def test_service_type_find_name():
    assert ServiceType.find_name("15") == "Aircraft"
    assert ServiceType.find_name("1") == "Multi-Dispatch"


def test_service_type_find_index():
    assert ServiceType.find_index("Aircraft") == "15"
    assert ServiceType.find_index("EMS Dispatch") == "4"


def test_service_type_setter():
    x = ServiceType()
    x.value = "Fire Dispatch"
    assert x.index == "3"
    assert x.value == "Fire Dispatch"
    x.value = 15
    assert x.value == "Aircraft"
    x.value = "2"
    assert x.value == "Law Dispatch"


def test_service_type_custom():
    x = ServiceType("208")
    assert x.value == "Custom 1"
    x = ServiceType("Custom 5")
    assert x.index == "212"


def test_service_type_invalid_name():
    with pytest.raises(KeyError):
        ServiceType("Nonexistent")


def test_service_type_invalid_index():
    with pytest.raises(KeyError):
        ServiceType("999")


# ── Radio ───────────────────────────────────────────────────

RADIO_LINE = "UnitIds\t\t\tUnit 1\t12345\tOff\tAuto\tOff\tOn\n"


def test_radio_from_text():
    r = Radio.from_text(RADIO_LINE)
    assert r.name == "Unit 1"
    assert r.radio_id == 12345
    assert r.alert_tone.value == "Off"
    assert r.alert_light.colour == "Off"


def test_radio_export():
    r = Radio(name="Unit 1", radio_id=12345)
    exported = r.export()
    assert exported.startswith("UnitIds\t\t\t")
    assert "Unit 1" in exported
    assert "12345" in exported


def test_radio_repr():
    r = Radio(name="Dispatch", radio_id=99)
    assert repr(r) == "Dispatch UID: 99"


def test_radio_from_text_invalid():
    with pytest.raises(TypeError):
        Radio.from_text("Invalid\t\t\tdata\n")


def test_radio_roundtrip():
    r = Radio.from_text(RADIO_LINE)
    exported = r.export()
    r2 = Radio.from_text(exported)
    assert r2.name == r.name
    assert r2.radio_id == r.radio_id


# ── TrunkedChannel ──────────────────────────────────────────

TGID_LINE = "TGID\t\t\tFire Dispatch\tOff\t100\tALL\t3\t2\t0\tOff\tAuto\tOff\tOn\tOff\tOff\tAny\n"


def test_trunked_channel_from_text():
    ch = TrunkedChannel.from_text(TGID_LINE)
    assert ch.name == "Fire Dispatch"
    assert ch.tgid == "100"
    assert str(ch.avoid) == "Off"
    assert ch.tdma_slot == "ALL"


def test_trunked_channel_export():
    ch = TrunkedChannel(tgid=200, name="EMS")
    exported = ch.export()
    assert exported.startswith("TGID\t\t\t")
    assert "EMS" in exported
    assert "\t200\t" in exported


def test_trunked_channel_repr():
    ch = TrunkedChannel(tgid=300, name="Police")
    assert repr(ch) == "Police TGID: 300"


def test_trunked_channel_equality():
    ch1 = TrunkedChannel(tgid=100, name="A")
    ch2 = TrunkedChannel(tgid=100, name="B")
    ch3 = TrunkedChannel(tgid=200, name="A")
    assert ch1 == ch2
    assert ch1 != ch3


def test_trunked_channel_equality_different_type():
    ch = TrunkedChannel(tgid=100, name="A")
    assert ch != "not a channel"


def test_trunked_channel_from_text_invalid():
    with pytest.raises(TypeError):
        TrunkedChannel.from_text("Bad\t\t\tdata\n")


def test_trunked_channel_roundtrip():
    ch = TrunkedChannel.from_text(TGID_LINE)
    exported = ch.export()
    ch2 = TrunkedChannel.from_text(exported)
    assert ch2.name == ch.name
    assert ch2.tgid == ch.tgid


# ── TrunkedGroup ────────────────────────────────────────────

TGROUP_LINE = "T-Group\t\t\tFire\tOff\t0.000000\t0.000000\t0.0\tCircle\t1\n"


def test_trunked_group_from_text():
    g = TrunkedGroup.from_text(TGROUP_LINE)
    assert g.name == "Fire"
    assert str(g.avoid) == "Off"
    assert g.quick_key == "1"
    assert g.channels == []


def test_trunked_group_export_with_channels():
    ch = TrunkedChannel(tgid=100, name="Ch1")
    g = TrunkedGroup(name="Test", quick_key=1, channels=[ch])
    exported = g.export()
    assert exported.startswith("T-Group\t\t\t")
    assert "TGID\t\t\t" in exported


def test_trunked_group_repr():
    g = TrunkedGroup(name="Law", quick_key=2, channels=[
        TrunkedChannel(tgid=1, name="A"),
        TrunkedChannel(tgid=2, name="B"),
    ])
    assert repr(g) == "TrunkedGroup Law QK 2 [2 Channels]"


def test_trunked_group_from_text_invalid():
    with pytest.raises(TypeError):
        TrunkedGroup.from_text("Bad\t\t\tdata\n")


def test_trunked_group_from_file():
    lines = TGROUP_LINE + TGID_LINE + TGID_LINE + "\n"
    f = io.StringIO(lines)
    g = TrunkedGroup.from_file(f)
    assert g.name == "Fire"
    assert len(g.channels) == 2


def test_trunked_group_from_file_stops_at_unknown():
    lines = TGROUP_LINE + TGID_LINE + "Trunk\t\t\tNext System\n"
    f = io.StringIO(lines)
    g = TrunkedGroup.from_file(f)
    assert len(g.channels) == 1
    remaining = f.readline()
    assert remaining.startswith("Trunk")


# ── ConventionalFrequency ──────────────────────────────────

CFREQ_LINE = "C-Freq\t\t\tWeather\tOff\t162550000\tNFM\t\t21\tOff\t2\t0\tOff\tAuto\tOff\tOn\tOff\tOff\n"


def test_conventional_freq_from_text():
    ch = ConventionalFrequency.from_text(CFREQ_LINE)
    assert ch.name == "Weather"
    assert ch.freq == "162550000"
    assert ch.modulation == "NFM"


def test_conventional_freq_export():
    ch = ConventionalFrequency(name="Test", freq=155000000, modulation="FM")
    exported = ch.export()
    assert exported.startswith("C-Freq\t\t\t")
    assert "Test" in exported


def test_conventional_freq_repr():
    ch = ConventionalFrequency(name="NOAA", freq=162_550_000, modulation="NFM")
    assert "162.55" in repr(ch)


def test_conventional_freq_equality():
    ch1 = ConventionalFrequency(name="A", freq=155000000, modulation="FM")
    ch2 = ConventionalFrequency(name="B", freq=155000000, modulation="NFM")
    ch3 = ConventionalFrequency(name="A", freq=160000000, modulation="FM")
    assert ch1 == ch2
    assert ch1 != ch3


def test_conventional_freq_equality_different_type():
    ch = ConventionalFrequency(name="A", freq=155000000, modulation="FM")
    assert ch != "not a freq"


def test_conventional_freq_from_text_invalid():
    with pytest.raises(TypeError):
        ConventionalFrequency.from_text("Bad\t\t\tdata\n")


def test_conventional_freq_roundtrip():
    ch = ConventionalFrequency.from_text(CFREQ_LINE)
    exported = ch.export()
    ch2 = ConventionalFrequency.from_text(exported)
    assert ch2.name == ch.name
    assert ch2.freq == ch.freq


# ── ConventionalGroup ──────────────────────────────────────

CGROUP_LINE = "C-Group\t\t\tWeather\tOff\t0.000000\t0.000000\t0.0\tCircle\tOff\tGlobal\n"


def test_conventional_group_from_text():
    g = ConventionalGroup.from_text(CGROUP_LINE)
    assert g.name == "Weather"
    assert str(g.avoid) == "Off"
    assert g.quick_key == "Off"
    assert g.filter == "Global"


def test_conventional_group_export_with_channels():
    ch = ConventionalFrequency(name="Ch1", freq=155000000, modulation="FM")
    g = ConventionalGroup(name="Test", channels=[ch])
    exported = g.export()
    assert exported.startswith("C-Group\t\t\t")
    assert "C-Freq\t\t\t" in exported


def test_conventional_group_from_text_invalid():
    with pytest.raises(TypeError):
        ConventionalGroup.from_text("Bad\t\t\tdata\n")


def test_conventional_group_from_file():
    lines = CGROUP_LINE + CFREQ_LINE + CFREQ_LINE + "\n"
    f = io.StringIO(lines)
    g = ConventionalGroup.from_file(f)
    assert g.name == "Weather"
    assert len(g.channels) == 2


def test_conventional_group_from_file_stops_at_unknown():
    lines = CGROUP_LINE + CFREQ_LINE + "Conventional\t\t\tNext\n"
    f = io.StringIO(lines)
    g = ConventionalGroup.from_file(f)
    assert len(g.channels) == 1
    remaining = f.readline()
    assert remaining.startswith("Conventional")


# ── BandPlan ────────────────────────────────────────────────

def test_bandplan_defaults():
    bp = BandPlan()
    assert len(bp.band_plans) == 16
    assert bp.band_plans[0] == (0, 0)


def test_bandplan_from_text():
    values = "\t".join(f"{i}\t{i + 1}" for i in range(0, 32, 2))
    line = f"BandPlan_P25\t\t{values}\n"
    bp = BandPlan.from_text(line)
    assert len(bp.band_plans) == 16
    assert bp.band_plans[0] == ("0", "1")


def test_bandplan_from_text_invalid():
    with pytest.raises(TypeError):
        BandPlan.from_text("BadPrefix\t\tdata\n")


def test_bandplan_export_roundtrip():
    values = "\t".join(f"{i}\t{i + 1}" for i in range(0, 32, 2))
    line = f"BandPlan_P25\t\t{values}\n"
    bp = BandPlan.from_text(line)
    exported = bp.export()
    bp2 = BandPlan.from_text(exported)
    assert bp2.band_plans == bp.band_plans


# ── DQKStatus ───────────────────────────────────────────────

DQK_LINE = "DQKs_Status\t\tOn\tOff\tOn\tOff\n"


def test_dqk_from_text():
    d = DQKStatus.from_text(DQK_LINE)
    assert d.statuses == ["On", "Off", "On", "Off"]


def test_dqk_export():
    d = DQKStatus(statuses=["On", "Off", "On"])
    assert d.export() == "DQKs_Status\t\tOn\tOff\tOn\n"


def test_dqk_roundtrip():
    d = DQKStatus.from_text(DQK_LINE)
    exported = d.export()
    d2 = DQKStatus.from_text(exported)
    assert d2.statuses == d.statuses


def test_dqk_from_text_invalid():
    with pytest.raises(TypeError):
        DQKStatus.from_text("Bad\t\tdata\n")


# ── Site ────────────────────────────────────────────────────

SITE_LINE = "Site\t\t\tMy Site Info\n"


def test_site_from_text():
    s = Site.from_text(SITE_LINE)
    assert s.value == "My Site Info"


def test_site_export_no_children():
    s = Site(value="Empty Site")
    exported = s.export()
    assert exported == "Site\t\t\tEmpty Site\n"


def test_site_from_text_invalid():
    with pytest.raises(TypeError):
        Site.from_text("Bad\t\t\tdata\n")


# ── SiteFrequency ───────────────────────────────────────────

SITEFREQ_LINE = "T-Freq\t\t\tOff\t851012500\tOff\tOff\n"


def test_site_frequency_from_text():
    sf = SiteFrequency.from_text(SITEFREQ_LINE)
    assert sf.frequency == "851012500"
    assert str(sf.unknown_value) == "Off"
    assert sf.dmr_lcn == "Off"
    assert sf.colour == "Off"


def test_site_frequency_str():
    sf = SiteFrequency(frequency=851012500)
    assert "851.0125" in str(sf)
    assert "Mhz" in str(sf)


def test_site_frequency_from_text_invalid():
    with pytest.raises(TypeError):
        SiteFrequency.from_text("Bad\t\t\tdata\n")


# ── Site from_file ──────────────────────────────────────────

def test_site_from_file_with_frequencies():
    lines = SITE_LINE + SITEFREQ_LINE + SITEFREQ_LINE + "\n"
    f = io.StringIO(lines)
    s = Site.from_file(f)
    assert s.value == "My Site Info"
    assert len(s.frequencies) == 2


def test_site_from_file_with_bandplan():
    bp_values = "\t".join(f"{i}\t{i}" for i in range(16))
    bp_line = f"BandPlan_P25\t\t{bp_values}\n"
    lines = SITE_LINE + bp_line + SITEFREQ_LINE + "\n"
    f = io.StringIO(lines)
    s = Site.from_file(f)
    assert s.bandplan is not None
    assert len(s.frequencies) == 1


def test_site_from_file_stops_at_unknown():
    lines = SITE_LINE + SITEFREQ_LINE + "T-Group\t\t\tNext Group\n"
    f = io.StringIO(lines)
    s = Site.from_file(f)
    assert len(s.frequencies) == 1
    remaining = f.readline()
    assert remaining.startswith("T-Group")


# ── System ──────────────────────────────────────────────────

TRUNK_SYS_LINE = "Trunk\t\t\tP25 System\n"
CONV_SYS_LINE = "Conventional\t\t\tLocal Freqs\n"


def test_system_from_text_trunked():
    s = System.from_text(TRUNK_SYS_LINE)
    assert s.line_prefix == "Trunk"
    assert s.value == "P25 System"


def test_system_from_text_conventional():
    s = System.from_text(CONV_SYS_LINE)
    assert s.line_prefix == "Conventional"
    assert s.value == "Local Freqs"


def test_system_from_text_invalid():
    with pytest.raises(TypeError):
        System.from_text("Unknown\t\t\tdata\n")


def test_system_export():
    s = System(line_prefix="Trunk", value="Test System")
    exported = s.export()
    assert exported == "Trunk\t\t\tTest System\n"


def test_system_from_file_trunked_with_groups():
    lines = TRUNK_SYS_LINE + TGROUP_LINE + TGID_LINE + "\n"
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert s.line_prefix == "Trunk"
    assert len(s.groups) == 1
    assert len(s.groups[0].channels) == 1


def test_system_from_file_conventional_with_groups():
    lines = CONV_SYS_LINE + CGROUP_LINE + CFREQ_LINE + "\n"
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert s.line_prefix == "Conventional"
    assert len(s.groups) == 1
    assert len(s.groups[0].channels) == 1


def test_system_from_file_with_radios():
    lines = TRUNK_SYS_LINE + RADIO_LINE + "\n"
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert len(s.radios) == 1
    assert s.radios[0].name == "Unit 1"


def test_system_from_file_with_dqk():
    lines = TRUNK_SYS_LINE + DQK_LINE + "\n"
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert s.dqk_status is not None
    assert len(s.dqk_status.statuses) == 4


def test_system_from_file_with_sites():
    lines = TRUNK_SYS_LINE + SITE_LINE + SITEFREQ_LINE + "\n"
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert len(s.sites) == 1
    assert len(s.sites[0].frequencies) == 1


def test_system_from_file_stops_at_next_system():
    lines = TRUNK_SYS_LINE + TGROUP_LINE + TGID_LINE + CONV_SYS_LINE
    f = io.StringIO(lines)
    s = System.from_file(f)
    assert len(s.groups) == 1
    remaining = f.readline()
    assert remaining.startswith("Conventional")


def test_system_from_file_invalid():
    f = io.StringIO("Unknown\t\t\tdata\n")
    with pytest.raises(TypeError):
        System.from_file(f)


# ── UnidenFile ──────────────────────────────────────────────

def test_uniden_file_defaults():
    uf = UnidenFile()
    assert uf.target_model == "BCDx36HP"
    assert uf.format_version == "1.00"
    assert uf.systems == []


def test_uniden_file_export_empty():
    uf = UnidenFile()
    exported = uf.export()
    assert "TargetModel\tBCDx36HP" in exported
    assert "FormatVersion\t1.00" in exported


def test_uniden_file_export_with_system():
    s = System(line_prefix="Trunk", value="Test")
    uf = UnidenFile(systems=[s])
    exported = uf.export()
    assert "Trunk\t\t\tTest" in exported


def test_uniden_file_from_file(tmp_path):
    content = (
        "TargetModel\tBCDx36HP\n"
        "FormatVersion\t1.00\n"
        + TRUNK_SYS_LINE
        + TGROUP_LINE
        + TGID_LINE
    )
    p = tmp_path / "test.hpd"
    p.write_text(content)
    uf = UnidenFile.from_file(str(p))
    assert uf.target_model == "BCDx36HP\n"
    assert len(uf.systems) == 1
    assert len(uf.systems[0].groups) == 1


def test_uniden_file_from_file_multiple_systems(tmp_path):
    content = (
        "TargetModel\tBCDx36HP\n"
        "FormatVersion\t1.00\n"
        + TRUNK_SYS_LINE
        + TGROUP_LINE
        + TGID_LINE
        + CONV_SYS_LINE
        + CGROUP_LINE
        + CFREQ_LINE
    )
    p = tmp_path / "test.hpd"
    p.write_text(content)
    uf = UnidenFile.from_file(str(p))
    assert len(uf.systems) == 2


def test_uniden_file_from_file_invalid_entry(tmp_path):
    content = "TargetModel\tBCDx36HP\nFormatVersion\t1.00\nGarbage\tline\n"
    p = tmp_path / "test.hpd"
    p.write_text(content)
    with pytest.raises(ValueError, match="Unknown entry type"):
        UnidenFile.from_file(str(p))


# ── UnidenTextType ──────────────────────────────────────────

def test_uniden_text_type_site_from_text():
    s = Site.from_text("Site\t\t\tMy Site Data\n")
    assert s.value == "My Site Data"


def test_uniden_text_type_export():
    s = Site(value="Exported Site")
    assert s.export().startswith("Site\t\t\t")
    assert "Exported Site" in s.export()


def test_uniden_text_type_tabs_text():
    s = Site(value="x")
    assert s.tabs_text == "\t\t\t"
