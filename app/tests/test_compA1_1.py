import pytest

from app.services.a_indicators import compA1_1
from app.models.instance import Instance

def test_compA1_1_with_operational_true():
    instance = Instance(type='rest', webpage=["https://github.com/inab/oeb-visualizations"], operational=True)
    result, logs = compA1_1(instance)
    print(logs)
    assert result == True

def test_compA1_1_with_webpage_no_operational():
    instance = Instance(type='rest', webpage=["https://github.com/inab/oeb-random"])
    result, logs = compA1_1(instance)
    assert result == False

def test_compA1_1_with_webpage_empty():
    instance = Instance(type='rest', webpage=[])
    result, logs = compA1_1(instance)
    assert result == False

def test_compA1_1_with_no_web_type():
    instance = Instance(type='cmd', webpage=["https://github.com/inab/oeb-visualizations"], operational=True)
    result, logs = compA1_1(instance)
    print(logs)
    assert result == False

if __name__ == "__main__":
    pytest.main()
