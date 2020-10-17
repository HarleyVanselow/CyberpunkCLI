from __future__ import print_function

import json
from googleapiclient.discovery import build
import click
import httplib2
import os
import getpass
import random
from colorama import Fore, Back, Style
from tabulate import tabulate
from src import SERVICE,SHEET_ID

@click.group()
def route():
    pass


@route.command()
@click.argument('character')
@click.argument('property')
def qc(character, property):
    results = query_character(character, property)[1]
    for result in results:
        print(f'{character} has {result} {property}')


@route.command()
@click.argument('character')
@click.argument('property')
@click.argument('value')
def uc(character, property, value):
    update_character(character, property, [value])


@route.command()
@click.argument('target')
@click.option('--auth', default=None)
def connect(target, auth):
    with open(f'./flavor_text/{target}.json') as target:
        target = json.load(target)
        admin = 'access_code' in target.keys(
        ) and auth == target['access_code']
        Base(target, admin).get_type().display()


@route.command()
@click.option('--stat', default=None)
@click.option('--D', default=10, type=click.INT)
@click.option('--skill', default='')
@click.option('--action', default=None)
def roll(stat, d, skill, action):
    if action is None:
        msg = base_roll(stat, d, skill)
    elif action == 'facedown':
        print('This is a facedown!')
    elif action == 'initiative':
        msg = 'Rolling for initiative: ' + base_roll('REF', d, None) +'\n'
        msg +=  'Special case: if a QUICK DRAW is declared, add 3 to intiative roll' \
            ' and take 3 extra damage in the current combat round.'
    elif action == 'attack':
        pass
    elif action == 'save':
        msg = "Rolling for save: "
    print(msg)
    os.system(f'wall "{msg}"')


def base_roll(stat, d, skill):
    result = random.randrange(1, d+1)
    character = getpass.getuser()
    stat_modifier = query_character(character, stat)[1]
    skill_notification = ']'
    skill_modifier = 0
    if skill:
        query, skill_modifier, skill = query_character(character, skill)
        skill_modifier = 0 if skill_modifier == '' else skill_modifier
        skill_notification = f' + {skill_modifier} ({skill})]'
    total = int(result) + int(stat_modifier) + int(skill_modifier)
    message = f"{character} rolled a {Fore.GREEN}{total}!{Style.RESET_ALL} [{result} (roll) + {stat_modifier} ({stat}){skill_notification}"
    return message


class Base:
    def _color_replace(self, input):
        color_map = {
            "g": Fore.GREEN,
            "r": Fore.RED,
            "b": Fore.BLUE,
            "/": Style.RESET_ALL
        }
        for k, v in color_map.items():
            input = input.replace(f'<{k}>', v)
        return input

    def display(self):
        if self.admin_flavor != '' and self.admin:
            print(self._color_replace(self.admin_flavor))
        else:
            print(self._color_replace(self.flavor))

    def get_summary(self):
        return self.flavor

    def get_properties(self):
        return self.target

    def display_options(self, to_display=[]):
        if self.options:
            user_done = False
            while not user_done:
                options = [Base(option, self.admin).get_type()
                           for option in self.options]
                if isinstance(options[0], Item):
                    tables = {}
                    headers = ['Item #']
                    for i, option in enumerate(options):
                        typed_table = tables.setdefault(
                            option.get_type_name(), {})
                        if 'headers' not in typed_table.keys():
                            typed_table['headers'] = headers + \
                                [h for h in option.get_display_fields().values()]
                        typed_table.setdefault('table', []).append(
                            [i+1]+[option.get_properties()[p] for p in option.get_display_fields().keys()])
                    for item_type in tables.keys():
                        print(item_type)
                        print(tabulate(tables[item_type]['table'],
                                       headers=tables[item_type]['headers']))
                elif isinstance(options[0], Info):
                    for i, option in enumerate(options):
                        print(f"{i+1}) {option.get_summary()}")
                print('Or q to quit')
                choice = click.prompt('')
                if choice == 'q':
                    return
                Base(self.options[int(choice)-1],
                     self.admin).get_type().display()
                user_done = click.confirm('Exit?')

    def __init__(self, target, admin):
        self.type = target['type']
        self.target = target
        self.flavor = target['flavor']
        self.admin_flavor = target.get('admin_flavor', '')
        self.options = target.get('options', [])
        self.admin = admin
        self.character = getpass.getuser()

    def get_type(self):
        if self.type == 'store':
            return Store(self.target, self.admin)
        elif self.type == 'info':
            return Info(self.target, self.admin)
        elif self.type == 'item':
            return Item(self.target, self.admin)
        elif self.type == "weapon":
            return Weapon(self.target, self.admin)
        elif self.type == 'gear':
            return Gear(self.target, self.admin)


class Store(Base):
    def display(self):
        super().display()
        super().display_options()

    def __init__(self, target, admin):
        super().__init__(target, admin)
        self.money = target['money']


class Info(Base):
    def display(self):
        super().display()
        super().display_options()

    def get_summary(self):
        return self.header

    def __init__(self, target, admin):
        super().__init__(target, admin)
        self.header = target.get('header', target['flavor'])


class Item(Base):
    """
    Item a player can buy at a store
    """

    def get_type_name(self):
        return "Items"

    def display(self):
        self.checkout()

    def checkout(self):
        balance = int(query_character(self.character, "money")
                      [0][0])[1]
        cost = int(self.cost)
        if balance < cost:
            print("Insufficient funds: Come back when you get some money, buddy!")
        else:
            balance -= cost
            update_character(self.character, "money", [balance])
            print(f"{self.cost} eb has been deducted. Enjoy your {self.flavor}")
            self.checkout_update()

    def checkout_update(self):
        raise NotImplementedError

    def get_display_fields(self):
        return {"flavor": "Name", "cost": "Price (eb/unit)"}

    def __init__(self, target, admin):
        super().__init__(target, admin)
        self.cost = target['cost']
        pass


class Gear(Item):
    def __init__(self, target, admin):
        super().__init__(target, admin)
        self.weight = target['weight']

    def get_type_name(self):
        return "Gear"

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({"weight": "Weight (kg)"})
        return fields

    def checkout_update(self):
        update_character(self.character, "gear", [
            self.flavor, self.cost, self.weight])


class Weapon(Item):
    def get_type_name(self):
        return "Weapons"

    def __init__(self, target, admin):
        super().__init__(target, admin)
        self.weapon_type = target['weapon_type']
        self.accuracy = target['accuracy']
        self.con = target['concealability']
        self.avail = target['availability']
        self.damage_ammo = target['damage/ammunition']
        self.num_shots = target['num_shots']
        self.rof = target['rate_of_fire']
        self.rel = target['reliability']
        self.range = target['range']

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({
            'weapon_type': 'Type',
            "accuracy": "Accuracy",
            "concealability": "Concealability",
            "availability": "Availability",
            "damage/ammunition": "Damage/Ammo",
            "num_shots": "#Shots",
            "rate_of_fire": "Rate of Fire",
            "reliability": "Reliability",
            "range": "Range"
        })
        return fields

    def checkout_update(self):
        update_character(self.character, "weapon", [
            self.flavor, self.weapon_type, self.accuracy, self.con,
            self.avail, self.damage_ammo, self.num_shots, self.rof,
            self.rel, self.range
        ])


def find_skill(skill_table, skill, starting_cell):
    skill_row = 0
    skill_col = 0
    for y, row in enumerate(skill_table):
        for x, skill_name in enumerate(row):
            if skill in skill_name.lower():
                skill_row = y
                skill_col = x+1
                skill = skill_name
    start_col = starting_cell[0]
    start_row = int(starting_cell[1:])
    cell = f'{chr(ord(start_col)+skill_col)}{start_row+skill_row}'
    val = skill_table[skill_row][skill_col] if len(
        skill_table[skill_row]) > skill_col else 0
    return (cell, val, skill)


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
            if len(return_val) == 1 and len(return_val[0]) == 1:
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
            query, skill_value, property = query_character(character, property)
        else:
            query = cell_map[property]
        if property in range_list:
            # First find next empty row
            (query, existing, property) = query_character(character, property)
            starting_cell = query.split(":")[0]
            if existing is None:
                query = starting_cell
            else:
                starting_col = starting_cell[:1]
                starting_row = starting_cell[1:]
                query = starting_col + str(int(starting_row) + len(existing))
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



