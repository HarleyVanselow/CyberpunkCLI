from __future__ import print_function

import json
from googleapiclient.discovery import build
import click
import httplib2
import os
import getpass

from tabulate import tabulate
from apiclient import discovery
from google.oauth2 import service_account
# To connect to the google sheet with all the characters
API_KEY = ''
SHEET_ID = ''
SERVICE = None


@click.group()
def route():
    pass


@route.command()
@click.argument('character')
@click.argument('property')
def qc(character, property):
    results = query_character(character, property)
    for result in results:
        print(f'{character} has {result[0]} {property}')

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
        admin = 'access_code' in target.keys() and auth == target['access_code']
        Base(target, admin).get_type().display()


class Base:
    def display(self):
        if self.admin_flavor != '' and self.admin:
            print(self.admin_flavor)
        else:
            print(self.flavor)

    def get_summary(self):
        return self.flavor
    
    def get_properties(self):
        return self.target

    def display_options(self, to_display=[]):
        if self.options:
            user_done = False
            while not user_done:
                options = [Base(option, self.admin).get_type() for option in self.options]
                option_types = set([type(opt) for opt in options])
                for option_type in option_types:
                    table = []
                    typed_options = [o for o in options if type(o) == option_type]
                    for i, option in enumerate(typed_options):
                        table.append([i+1]+[option.get_properties()[p] for p in option.get_display_fields().keys()])
                    print(typed_options[0].get_type_name())
                    headers = ['Item #']
                    headers+=[h for h in typed_options[0].get_display_fields().values()]
                    print(tabulate(table, headers=headers))
                print('Or q to quit')
                choice = click.prompt('')
                if choice == 'q':
                    return
                Base(self.options[int(choice)-1], self.admin).get_type().display()
                user_done = click.confirm('Exit?')

    def __init__(self, target, admin):
        self.type = target['type']
        self.target = target
        self.flavor = target['flavor']
        self.admin_flavor = target.get('admin_flavor', '')
        self.options = target.get('options', [])
        self.admin = admin

    def get_type(self):
        if self.type == 'store':
            return Store(self.target, self.admin)
        elif self.type == 'info':
            return Info(self.target, self.admin)
        elif self.type == 'item':
            return Item(self.target, self.admin)
        elif self.type == "weapon":
            return Weapon(self.target, self.admin)


class Store(Base):
    def display(self):
        super().display()
        super().display_options()

    def __init__(self, target, admin):
        super().__init__(target,admin)
        self.money = target['money']


class Info(Base):
    def display(self):
        super().display()
        super().display_options()

    def get_summary(self):
        return self.header

    def __init__(self, target, admin):
        super().__init__(target,admin)
        self.header = target.get('header', target['flavor'])


class Item(Base):
    """
    Item a player can buy at a store
    """
    def get_type_name(self):
        return "Items"

    def display(self):
        # import pdb; pdb.set_trace()
        self.checkout()
        print(f"{self.cost} eb has been deducted. Enjoy your {self.flavor}")

    def checkout(self):
        character = getpass.getuser()
        balance = int(query_character(character, "money")[0][0]) - int(self.cost)
        update_character(character, "money", [balance])
        update_character(character, "gear", [self.flavor, self.cost, self.weight])

    def get_display_fields(self):
        return {"flavor":"Name", "cost":"Price (eb)","weight":"Weight (kg)"}

    def __init__(self,target, admin):
        super().__init__(target, admin)
        self.cost = target['cost']
        self.weight = target['weight']
        pass


class Gear(Item):
    def __init__(self, )

    def get_type_name(self):
        return "Gear"

    

class Weapon(Item):
    def get_type_name(self):
        return "Weapons"

    def __init__(self, target, admin):
        super().__init__(target, admin)

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({'damage':'Damage'})
        return fields


def query_character(character, property):
    with open('sheet_map.json') as sheet_map:
        cell_map = json.load(sheet_map)
        query = cell_map[property]
        sheet = SERVICE.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID,
                                    range=f'{character}!{query}').execute()
        return result['values']


def update_character(character, property, value):
    with open('sheet_map.json') as sheet_map:
        cell_map = json.load(sheet_map)
        range_list = cell_map["range_list"]

        query = cell_map[property]
        if property in range_list:
            # First find next empty row 
            existing = query_character(character, property)
            starting_cell = query.split(":")[0]
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
        sheet = SERVICE.spreadsheets()
        sheet.values().update(
            spreadsheetId=SHEET_ID, 
            range=f'{character}!{query}',
            valueInputOption='USER_ENTERED', 
            body=body
        ).execute()


if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    with open('credentials.json') as creds:
        creds = json.load(creds)
        SHEET_ID = creds['sheet_id']
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'client_secret.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        SERVICE = discovery.build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        print(e)
    route()
