from src.router import query_character, get_weapon_from_character
from src.displayclasses import Weapon
from src.sheetio import apply_wound_effects
import os

skill_map=[['SPECIAL ABILITIES', '', 'INT', '', 'REF', '', 'TECH'], ['Authority', '', 'Accounting', '', 'Archery', '', 'Aero Tech (2)'], ['Charismatic Leadership', '8', 'Anthropology', '', 'Athletics', '', 'AV Tech (3)'], ['Combat Sense', '', 'Awareness/Notice', '', 'Brawling', '', 'Basic Tech (2)'], ['Credibility', '', 'Biology', '', 'Dance', '', 'Cryotank Operation'], ['Family', '', 'Botany', '', 'Dodge & Escape', '', 'Cyberdeck Design (2)'], ['Interface', '', 'Chemistry', '', 'Driving', '', 'Cyber Tech (2)'], ['Jury Rig', '', 'Composition', '', 'Fencing', '', 'Demolitions (2)'], ['Medical Tech', '', 'Diagnose Illness', '', 'Handgun', '', 'Disguise'], ['Resources', '', 'Education & Gen Know', '', 'Heavy Weapons', '', 'Electronics'], ['Streetdeal', '', 'Expert', '', 'Martial Art 1', '', 'Elect. Security (2)'], ['ATTR', '', 'Gamble', '', 'Martial Art 2', '', 'First Aid'], ['Personal Grooming', '', 'Geology', '', 'Martial Art 3', '', 'Forgery'], ['Wardrobe & Style', '', 'Hide/Evade', '', 'Melee', '', 'Gyro Tech (3)']]
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
def mock_query_sheet(**query):
    assert query['spreadsheetId'] == os.getenv('SHEET_ID')
    if query['range'] == 'harley!B22':
        return {"values":[['8']]}
    elif query['range'] == 'harley!B7':
        return {"values":[['5']]}
    elif query['range'] == 'harley!A20:H51':
        return {"values": skill_map}
    elif query['range'] == 'harley!J55:T75':
        return {"values": [list(weapon.values())]}
    else:
        return {}

def mock_get_wounds(character):
    if character != 'wounded':
        return 0


def test_query_character(mocker):
    mocker.patch("src.sheetio.query_sheet", new=mock_query_sheet)
    mocker.patch("src.sheetio.get_wound_status", new=mock_get_wounds)

    assert ('B22', '8', 'Charismatic Leadership') == query_character(
        'harley', 'charisma')
    assert (None, '0', 'cowardice') == query_character('harley', 'cowardice')
    assert ('B7', '5', 'int') == query_character('harley', 'int')


def test_get_weapon_from_character(mocker):
    mocker.patch("src.sheetio.query_sheet", new=mock_query_sheet)
    mocker.patch("src.sheetio.get_wound_status", new=mock_get_wounds)

    from_index = get_weapon_from_character('harley', 'Impact').__dict__
    for item in weapon.items():
        assert item in from_index.items()

def test_apply_wound_effects():
    assert 5 == apply_wound_effects('stat',1,5)
    assert 3 == apply_wound_effects('ref',2,5)
    assert 5 == apply_wound_effects('int',2,5)
    assert 4 == apply_wound_effects('int',3,7)
    assert 3 == apply_wound_effects('int',4,7)


