import pytest

from src.sheetio import deal_damage, update_character
from src.router import get_hit_number
from src.displayclasses import Weapon

def test_attack():
    pass


def test_get_hit_number():
    target = {
        "type": "weapon",
        "flavor": "Federated Arms Impact"
    }
    weapon = Weapon(target, None, "spitefyre")
    assert(weapon.range == "50m")
    # Negative range
    with pytest.raises(ValueError):
        get_hit_number(weapon, -1)
    # Point blank: within one quarter of range
    assert(get_hit_number(weapon, 10) == 10)
    # Close: between quarter and half
    assert(get_hit_number(weapon, 20) == 15)
    # Medium: between half and the range
    assert(get_hit_number(weapon, 30) == 20)
    # Long: between range and twice the range
    assert(get_hit_number(weapon, 60) == 25)
    # Extreme: greater than or equal to twice the range
    assert(get_hit_number(weapon, 100) == 30)
    assert(get_hit_number(weapon, 150) == 30)