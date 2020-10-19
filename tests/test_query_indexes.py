from src.displayclasses import Weapon


def test_get_weapon_from_index():
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
    from_index = Weapon({'flavor':'Impact','type':'weapon'}, None).__dict__
    for item in weapon.items():
        assert item in from_index.items()