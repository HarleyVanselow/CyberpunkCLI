from __future__ import print_function

import json
from googleapiclient.discovery import build
import click

api_key = ''
sheet_id = ''


@click.group()
def route():
    pass


@route.command()
@click.argument('target')
@click.argument('property')
def gc(target, property):
    service = build(
        'sheets', 'v4', developerKey=api_key)
    print(f'{target} has {query_character(target, property, service)} {property}')


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

    def display_options(self):
        if self.options:
            user_done = False
            while not user_done:
                for i, option in enumerate(self.options):
                    option = Base(option, self.admin).get_type()
                    print(f'{i+1}) {option.get_summary()}')
                print('Or q to quit')
                choice = click.prompt('')
                if choice == 'q':
                    return
                Base(self.options[int(choice)-1], self.admin).get_type().display()
                user_done = click.confirm('Exit?')

    def __init__(self,target, admin):
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
    def display(self):
        print(f"{self.cost} eb has been deducted. Enjoy your {self.flavor}")
    def get_summary(self):
        return f'{self.flavor}: {self.cost} eb'
    def __init__(self,target, admin):
        super().__init__(target, admin)
        self.cost = target['cost']
        pass


def query_character(character, property, service):
    with open('sheet_map.json') as sheet_map:
        cell_map = json.load(sheet_map)
        query = cell_map[property]
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=f'{character}!{query}').execute()
        return result['values'][0][0]


if __name__ == '__main__':
    with open('./credentials.json') as creds:
        creds = json.load(creds)
        api_key = creds['api_key']
        sheet_id = creds['sheet_id']
    route()
