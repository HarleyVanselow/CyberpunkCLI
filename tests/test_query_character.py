from src.router import query_character, get_weapon_from_character
from src.displayclasses import Weapon


def test_query_character():
    assert ('B22', '8', 'Charismatic Leadership') == query_character(
        'harley', 'charisma')
    assert (None, '0', 'cowardice') == query_character('harley', 'cowardice')
    assert ('B7', '5', 'int') == query_character('harley', 'int')

