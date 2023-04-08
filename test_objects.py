from uniden import UnidenBool, UnidenRange, AlertLight, AlertTone, ServiceType


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


def test_uniden_range():
    x = UnidenRange()
    assert str(x) == "0.000000\t0.000000\t0.0\tCircle"


def test_alert_tone():
    x = AlertTone()
    assert x.value == 0
    assert x.volume == 0
    assert str(x) == "Off\tAuto"


def test_alert_light():
    x = AlertLight()
    assert x.state == "On"
    assert x.colour == "Off"
    assert str(x) == "Off\tOn"


def test_service_types():
    x = ServiceType()
    assert str(x) == "Other"
    assert x.index == "21"
    assert x.value == "Other"
    x = ServiceType(15)
    assert str(x) == "Aircraft"
    x = ServiceType('Other')
    assert x.index == "21"

