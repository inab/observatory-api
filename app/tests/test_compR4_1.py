from app.models.instance import Instance
from app.services.r_indicators import compR4_1

# Test cases for compR4_1 function
def test_compR4_1_with_version_control_true():
    # Case where version_control is True
    instance = Instance(version_control=True)
    result, logs = compR4_1(instance)
    assert result == True


def test_compR4_1_with_version_control_false():
    # Case where version_control is False
    instance = Instance(version_control=False)
    result, logs = compR4_1(instance)
    assert result == False

def test_compR4_1_with_version_control_none():
    # Case where version_control is None
    instance = Instance(version_control=None)
    result, logs = compR4_1(instance)
    assert result == False
