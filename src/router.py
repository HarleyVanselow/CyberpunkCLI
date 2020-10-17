from __future__ import print_function

import json
from googleapiclient.discovery import build
import click
import httplib2
import os
import getpass
import random
from src import SERVICE, SHEET_ID
from src.displayclasses import Base
from src.sheetio import query_character, update_character, get_weapon
from colorama import Fore, Back, Style

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


@route.group()
def roll():
    pass

@roll.command()
@click.option('--stat', default=None)
@click.option('--D', default=10, type=click.INT)
@click.option('--skill', default='')
def skillcheck(stat, d, skill):
    msg = base_roll(stat, d, skill)
    print(msg)
    os.system(f'wall "{msg}"')

@roll.command()
def facedown():
    print('This is the final facedown!')

@roll.command()
def initiative():
    msg = 'Rolling for initiative: ' + base_roll('REF', 10, None) + '\n'
    msg += 'Special case: if a QUICK DRAW is declared, add 3 to intiative roll' \
        ' and take 3 extra damage in the current combat round.'
    print(msg)
    os.system(f'wall "{msg}"')


@roll.command()
@click.argument('is_called') 
@click.argument('weapon')
@click.argument('opponent')
def attack(is_called, weapon_name, opponent):
    """
    :param is_called: If an attack is called, it aims at a specific 
        part of the opponent's body but the attacker takes -4 penalty 
        in attack damage. Allowed values: True or False.
    :param weapon: Pick a weapon from your inventory to use in the 
        current combat round. Allowed values: Names of weapons you own.
    :param opponent: Name of the person you are fighting against.
    """
    #TODO: Make the docstring keep its formatting when 
    # printed with --help
    # Get weapon stats
    character = getpass.getuser()
    weapon = get_weapon(character, weapon_name) #TODO: Implement get_weapon()

    for i in range(weapon.rof):
        # Roll for hit location
        loc = random.randrange(1, 11)

        # Get opponent's SP based on location

        # Get opponent's body type

        # Compute final damage on opponent

        # Update opponent's wounds


@roll.command()
def save():
    pass


def base_roll(stat, d, skill):
    result = random.randrange(1, d+1)
    character = getpass.getuser()
    stat_modifier = query_character(character, stat)[1]
    skill_notification = ']'
    skill_modifier = 0
    if skill:
        _, skill_modifier, skill = query_character(character, skill)
        skill_modifier = 0 if skill_modifier == '' else skill_modifier
        skill_notification = f' + {skill_modifier} ({skill})]'
    total = int(result) + int(stat_modifier) + int(skill_modifier)
    message = f"{character} rolled a {Fore.GREEN}{total}!{Style.RESET_ALL} [{result} (roll) + {stat_modifier} ({stat}){skill_notification}"
    return message
