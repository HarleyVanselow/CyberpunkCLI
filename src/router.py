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
from src.sheetio import query_character, update_character, get_weapon_from_character, deal_damage
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
    file = [file for file in os.listdir('./flavor_text') if target.lower() in file.lower()]
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
    msg = base_roll(['cool','rep'], 10, None)
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
@click.argument('is_called') 
@click.argument('weapon_name')
@click.argument('opponent')
def attack(is_called, weapon_name, opponent):
    """
    :param is_called: If an attack is called, it aims at a specific 
        part of the opponent's body but the attacker takes -4 penalty 
        in attack damage. Allowed values: 1-10 for called attacks, 11 for uncalled
        1: Head
        2-4: Torso
        5: Right arm
        6: Left arm
        7-8: Right leg
        9-10: Left leg
    :param weapon: Pick a weapon from your inventory to use in the 
        current combat round. Allowed values: Names of weapons you own.
    :param opponent: Name of the person you are fighting against.
    """
    #TODO: Make the docstring keep its formatting when 
    # printed with --help
    # Get weapon stats
    character = getpass.getuser()
    weapon = get_weapon_from_character(character, weapon_name) 

    # Roll for hit location
    is_called = int(is_called)
    if is_called == 11:
        loc = random.randrange(1, 11)
        damage = 0
        msg = "The attack is not called - rolled %d for attack location" % loc
    else:
        loc = is_called
        damage = -4        

    # Get opponent's SP based on location
    query, sp, name = query_character(opponent, 'loc_'+str(loc))

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
    deal_damage(character, damage)


@roll.command()
def save():
    pass


def base_roll(stats, d, skill):
    result = random.randrange(1, d+1)
    character = getpass.getuser()
    stat_results = {}
    for stat in stats:
        stat_results[stat] = query_character(character, stat)[1]
    skill_notification = ']'
    stat_notification = ' + '.join([f"{v} ({k})" for k,v in stat_results.items()])
    skill_modifier = 0
    if skill:
        _, skill_modifier, skill = query_character(character, skill)
        skill_modifier = 0 if skill_modifier == '' else skill_modifier
        skill_notification = f' + {skill_modifier} ({skill})]'
    total = int(result) + sum([int(v) for v in stat_results.values()]) + int(skill_modifier)
    message = f"{character} rolled a {Fore.GREEN}{total}!{Style.RESET_ALL} [{result} (roll) + {stat_notification}{skill_notification}"
    return message
