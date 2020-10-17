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
from src import SERVICE, SHEET_ID
from src.displayclasses import Base
from src.sheetio import query_character, update_character


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
        msg = 'Rolling for initiative: ' + base_roll('REF', d, None) + '\n'
        msg += 'Special case: if a QUICK DRAW is declared, add 3 to intiative roll' \
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
