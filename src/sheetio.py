from src import SERVICE, SHEET_ID, TABLE
import json
import math
from tabulate import tabulate

def disconnect_character(character):
    c = {}
    with open('connections.json') as conn:
        c = json.load(conn)
        c.pop(character)
    with open('connections.json', 'w') as conn:
        json.dump(c, conn)


def connect_character(character, target,pw):
    c = {}
    with open('connections.json') as conn:
        c = json.load(conn)
        c[character] = target+':'+pw
    with open('connections.json', 'w') as conn:
        json.dump(c, conn)


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
        skill_table[skill_row]) > skill_col else '0'
    val = '0' if val == '' else val
    return (cell, val, skill)


def get_weapon_from_character(character, weapon_name):
    from src.displayclasses import Weapon
    _, weapons, _ = query_character(character, 'weapon')
    for weapon in weapons:
        if weapon_name.lower() in weapon[0].lower():
            return Weapon({'flavor': weapon[0], 'type': 'weapon'}, None, character)


def get_wound_status(character):
    wound_status = get_wound_values(character)
    for i, item in enumerate(wound_status.items()):
        if item[1] == 0:
            return i - 1 if i > 0 else 0
    return 8

def get_wound_values(character):
    _, wounds_list, _ = query_character(character, 'wounds')
    if len(wounds_list) == 2:
        categories = wounds_list[0] + wounds_list[1]
        wounds = []
    elif len(wounds_list) == 3:
        categories = wounds_list[0] + wounds_list[2]
        wounds = wounds_list[1]
    elif len(wounds_list) == 4:
        categories = wounds_list[0] + wounds_list[2]
        wounds = wounds_list[1] + wounds_list[3]
    else:
        raise ValueError("Incorrect wounds format in Google Sheets")

    wounds_int = [int(x) for x in wounds]

    while(len(wounds_int) < 10):
        wounds_int.append(0)
    return dict(zip(categories, wounds_int))


def deal_damage(character, new_damage):
    """
    :param str character: name of the character
    :param int new_damage: amount of additional damage to 
        be dealt to the character
    """
    new_damage = int(new_damage)

    cat_max = 4
    wound_values = get_wound_values(character)
    wounds_int = list(wound_values.values())
    categories = list(wound_values.keys())

    for i in range(len(wounds_int)):
        diff = cat_max - wounds_int[i]
        bump = min(diff, new_damage)
        wounds_int[i] += bump
        new_damage -= bump

    print(f'{character} health:')
    print('```')
    print(tabulate(zip(categories,['x'*x for x in wounds_int]),tablefmt="grid"))
    print('```')
    

    wounds = [str(x) for x in wounds_int]

    update_vals = [
        categories[:5],
        wounds[:5],
        categories[5:],
        wounds[5:]
    ]
    update_character(character, 'wounds', update_vals)


def query_sheet(**kwargs):
    global TABLE
    # pylint: disable=maybe-no-member
    split = kwargs['range'].split("!")
    character = split[0]
    query = split[1]

    def get_cells(name):
        col = ord(name[0]) - 65
        row = int(name[1:])-1
        return row, col
    if character not in TABLE.keys():
        sheet = SERVICE.spreadsheets()
        sheet_id = kwargs['spreadsheetId']
        TABLE[character] = sheet.values().get(
            spreadsheetId=sheet_id, range=character).execute()['values']
    query = query.split(':')
    if len(query) == 1:
        # Single cell
        row, col = get_cells(query[0])
        try:
            return {"values": [[TABLE[character][row][col]]]}
        except IndexError:
            return {}
    else:
        # Range
        start_cell = query[0]
        end_cell = query[1]
        start_row, start_col = get_cells(start_cell)
        end_row, end_col = get_cells(end_cell)
        return {"values": [[v for i, v in enumerate(row) if i >= start_col and i <= end_col] for i, row in enumerate(TABLE[character]) if i >= start_row and i <= end_row]}


def update_sheet(**kwargs):
    # pylint: disable=maybe-no-member
    sheet = SERVICE.spreadsheets()
    return sheet.values().update(**kwargs).execute()


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
        property = property.lower()
        cell_map = json.load(sheet_map)
        is_skill = property not in cell_map.keys()
        if is_skill:
            # assume its a skill
            query = cell_map['skills']
        else:
            query = cell_map[property]
        # These results are affected by wound status

        result = query_sheet(spreadsheetId=SHEET_ID,
                             range=f'{character}!{query}')

        if 'values' in result:
            return_val = result['values']
            if len(return_val) == 1 and len(return_val[0]) == 1 and ":" not in query:
                return_val = result['values'][0][0]
                if property in ['ref', 'int', 'cool']:
                    wound_status = get_wound_status(character)
                    return_val = apply_wound_effects(
                        property, wound_status, return_val)
            return find_skill(result['values'], property, query.split(':')[0]) if is_skill else (query, return_val, property)
        else:
            return (query, None, property)


def apply_wound_effects(stat, wound_status, starting_val):
    if stat == 'ref' and wound_status == 2:
        return int(starting_val) - 2
    elif wound_status == 3:
        return math.ceil(int(starting_val)/2)
    elif wound_status > 3:
        return math.ceil(int(starting_val)/3)
    else:
        return starting_val


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
            existing = query_character(character, property)[1]
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
        if isinstance(value[0], list):
            v = value
        else:
            v = [value]
        body = {'values': v}
        update_sheet(
            spreadsheetId=SHEET_ID,
            range=f'{character}!{query}',
            valueInputOption='USER_ENTERED',
            body=body
        )
