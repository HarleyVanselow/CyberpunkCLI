from src.router import query_character, get_weapon, Base


def test_query_character():
    assert ('B22', '8', 'Charismatic Leadership') == query_character(
        'harley', 'charisma')
    assert (None, '0', 'cowardice') == query_character('harley', 'cowardice')
    assert ('B7', '5', 'int') == query_character('harley', 'int')


def test_get_weapon():
    weapon_dict = {
        "type": "weapon",
        "flavor": "C-6",
        "weapon_type": "HVY",
        "accuracy": '0',
        "concealability": "P",
        "availability": "P",
        "damage/ammunition": "8D10",
        "num_shots": '1',
        "rate_of_fire": '1',
        "reliability": "VR",
        "range": "-1",
        "cost": None
    }
    weapon = Base(weapon_dict, None).get_type()
    assert weapon.__dict__ == get_weapon('harley', 'C-6').__dict__
