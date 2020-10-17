from src import SERVICE, SHEET_ID
import json


def find_skill(skill_table, skill, starting_cell):
    skill_row = None
    skill_col = None
    for y, row in enumerate(skill_table):
        for x, skill_name in enumerate(row):
            if skill in skill_name.lower():
                skill_row = y
                skill_col = x+1
                skill = skill_name
    if skill_row is None and skill_col is None:
        return (None, '0', skill)
    start_col = starting_cell[0]
    start_row = int(starting_cell[1:])
    cell = f'{chr(ord(start_col)+skill_col)}{start_row+skill_row}'
    val = skill_table[skill_row][skill_col] if len(
        skill_table[skill_row]) > skill_col else 0
    return (cell, val, skill)


def get_weapon(character, weapon_name):
    from src.displayclasses import Base
    _, weapons, _ = query_character(character, 'weapon')
    for weapon in weapons:
        if weapon[0].lower() in weapon_name.lower():
            return Base({
                        "type": "weapon",
                        "flavor": weapon[0],
                        "weapon_type": weapon[1],
                        "accuracy": weapon[2],
                        "concealability": weapon[3],
                        "availability": weapon[4],
                        "damage/ammunition": weapon[5],
                        "num_shots": weapon[6],
                        "rate_of_fire": weapon[7],
                        "reliability": weapon[8],
                        "range": weapon[9],
                        "cost": None
                        }, None).get_type()


def query_character(character, property):
    """Gets a stat value from a character sheet

    Args:
        character (string): name of the character
        property (string): name of the attribute or skill

    Returns:
        (query, value, skill): Returns the name of the cell holding the value,
        the value itself, and the full name of the relevant attribute or skill
    """
    with open('sheet_map.json') as sheet_map:
        cell_map = json.load(sheet_map)
        is_skill = property.lower() not in cell_map.keys()
        if is_skill:
            # assume its a skill
            query = cell_map['skills']
        else:
            query = cell_map[property.lower()]
        # pylint: disable=maybe-no-member
        sheet = SERVICE.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID,
                                    range=f'{character}!{query}').execute()
        if 'values' in result:
            return_val = result['values']
            if len(return_val) == 1 and len(return_val[0]) == 1 and ":" not in query:
                return_val = result['values'][0][0]
            return find_skill(result['values'], property, query.split(':')[0]) if is_skill else (query, return_val, property)
        else:
            return None


def update_character(character, property, value):
    with open('sheet_map.json') as sheet_map:
        cell_map = json.load(sheet_map)
        range_list = cell_map["range_list"]
        is_skill = property.lower() not in cell_map.keys()
        if is_skill:
            query, _, property = query_character(character, property)
        else:
            query = cell_map[property]
        if property in range_list:
            # First find next empty row
            existing = query_character(character, property)
            starting_cell = query.split(":")[0]
            if existing is None:
                query = starting_cell
            else:
                starting_col = starting_cell[:1]
                starting_row = starting_cell[1:]
                query = starting_col + \
                    str(int(starting_row) + len(existing[1]))
                i = 0
                while i < len(existing):
                    if existing[i] == []:
                        query = starting_col + str(int(starting_row) + i)
                        break
                    i += 1

        body = {'values': [value]}
        # pylint: disable=maybe-no-member
        sheet = SERVICE.spreadsheets()
        sheet.values().update(
            spreadsheetId=SHEET_ID,
            range=f'{character}!{query}',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()