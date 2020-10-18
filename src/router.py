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
from src.sheetio import query_character, update_character, get_weapon_from_character, deal_damage, get_wound_status
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
    file = [file for file in os.listdir(
        './flavor_text') if target.lower() in file.lower()]
    if len(file) > 0:
        target = file[0]
    else:
        print(f'No target matching request "{target}"')
        return
    with open(f'./flavor_text/{target}') as target:
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
    msg = base_roll([stat], d, skill)
    print(msg)
    os.system(f'wall "{msg}"')


@roll.command()
def facedown():
    msg = base_roll(['cool', 'rep'], 10, None)
    print('This is the final facedown!')
    print(msg)
    os.system(f'wall "{msg}"')


@roll.command()
def initiative():
    msg = 'Rolling for initiative: ' + base_roll(['REF'], 10, None) + '\n'
    msg += 'Special case: if a QUICK DRAW is declared, add 3 to intiative roll' \
        ' and take 3 extra damage in the current combat round.'
    print(msg)
    os.system(f'wall "{msg}"')


@roll.command()
@click.option('--target', type=click.Choice(['head', 'torso', 'right arm', 'left arm', 'right leg', 'left leg']), default=None)
@click.argument('weapon_name')
@click.argument('opponent')
def attack(weapon_name, opponent, target):
    """
    :param weapon: Pick a weapon from your inventory to use in the 
        current combat round. Allowed values: Names of weapons you own.
    :param opponent: Name of the person you are fighting against.
    """
    # TODO: Make the docstring keep its formatting when
    # printed with --help
    # Get weapon stats
    character = getpass.getuser()
    weapon = get_weapon_from_character(character, weapon_name)

    body_map = {
        "head": [1],
        "toro": [2, 3, 4],
        "right arm": [5],
        "left arm": [6],
        "right leg": [7, 8],
        "left leg": [9, 10]
    }

    if target is None:
        # Roll for hit location
        loc = random.randrange(1, 11)
        loc = [k for k, v in body_map.items() if loc in v][0]
        damage = 0
        msg = f"The attack is not called - hit {loc}. "
    else:
        loc = target
        damage = -4
    # Get opponent's SP based on location
    query, sp, name = query_character(opponent, loc)

    # Get opponent's body type
    query, btm, name = query_character(opponent, 'btm')

    # Roll for damage
    # Assuming weapon.damage_ammo is always in the form of "XDY+Z (mm)"
    damage_stat = weapon.damage_ammo.lower().split(' ')[0]
    if '+' in damage_stat:
        # XdY+Z
        roll, bonus = damage_stat.split('+')
        bonus = int(bonus)
        damage += bonus
    else:
        roll = damage_stat
    times, d = [int(x) for x in roll.split('d')]
    for i in range(times):
        damage += random.randrange(1, d+1)

    # Compute final damage on opponent
    if sp:
        damage -= int(sp)
    if btm:
        damage -= int(btm)

    # Update opponent's wounds
    msg += "Total damage is %d" % damage
    print(msg)


@roll.command()
@click.argument('character')
@click.argument('new_damage')
def damage(character, new_damage):
    """
    :param str character
    :param int new_damage: additional damage to be dealt to the character
    """
    deal_damage(character, new_damage)


@roll.group()
def save():
    pass

@save.command()
def stun():
    """
    Roll a stun save
    """
    character = getpass.getuser()
    bt = int(query_character(character, 'body')[1])
    wound_status = get_wound_status(character)
    roll = random.randrange(1, 11)
    success = roll < (bt - wound_status)
    status = 'succeeded' if success else 'failed'
    print(f'Stun save {status}: rolled {roll} vs body type ({bt}) - wound status ({wound_status})')

@save.command()
def death():
    """
    Roll a death save
    """
    character = getpass.getuser()
    bt = int(query_character(character, 'body')[1])
    wound_status = 0
    success = random.randrange(1, 11) < (bt - wound_status)
    print('Death save')


def base_roll(stats, d, skill):
    result = random.randrange(1, d+1)
    character = getpass.getuser()
    stat_results = {}
    for stat in stats:
        stat_results[stat] = query_character(character, stat)[1]
    skill_notification = ']'
    stat_notification = ' + '.join([f"{v} ({k})" for k,
                                    v in stat_results.items()])
    skill_modifier = 0
    if skill:
        _, skill_modifier, skill = query_character(character, skill)
        skill_modifier = 0 if skill_modifier == '' else skill_modifier
        skill_notification = f' + {skill_modifier} ({skill})]'
    total = int(result) + sum([int(v)
                               for v in stat_results.values()]) + int(skill_modifier)
    message = f"{character} rolled a {Fore.GREEN}{total}!{Style.RESET_ALL} [{result} (roll) + {stat_notification}{skill_notification}"
    return message
