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
def connect(target):
    with open(f'./flavor_text/{target}.json') as target:
        target = json.load(target)
        display(target)


def display(target):
    if target['type'] == 'item':
        print(f'Buy {target["flavor"]}?')
    else:
        print(target['flavor'])
    if 'options' in target.keys():
        user_done = False
        while not user_done:
            for i, option in enumerate(target['options']):
                print(f'{i+1}) {get_summary(option)}')
            choice = click.prompt('')
            display(target['options'][int(choice)-1])
            user_done = click.confirm('Exit?')


def get_summary(target):
    if target['type'] == 'item':
        return display_item(target)
    elif target['type'] == 'info':
        return target['header']


def display_item(target):
    if target['cost'] is None:
        return target['flavor']
    else:
        return f"{target['flavor']}: ${target['cost']}"


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
