from src.router import query_character, get_weapon_from_character
from src.displayclasses import Weapon


def test_query_character():
    assert ('B22', '8', 'Charismatic Leadership') == query_character(
        'harley', 'charisma')
    assert (None, '0', 'cowardice') == query_character('harley', 'cowardice')
    assert ('B7', '5', 'int') == query_character('harley', 'int')

def test_get_weapon_from_character():
    weapon = {'flavor': 'Federated Arms Impact',
              'weapon_type': 'P',
              'accuracy': '+1',
              'con': 'J',
              'avail': 'E',
              'damage_ammo': '1d6(.22)',
              'num_shots': '10',
              'rof': '2',
              'rel': 'VR',
              'range': '50m',
              'cost': '60'}
    from_index = get_weapon_from_character('harley','Impact').__dict__
    for item in weapon.items():
        assert item in from_index.items()