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
from src.sheetio import query_character, update_character, get_weapon_from_character, deal_damage, get_wound_status, connect_character


@click.group()
@click.option('--character', default=getpass.getuser())
@click.pass_context
def route(ctx, character):
    ctx.obj = character
    pass


@route.command()
@click.pass_obj
def test(character):
    print(f"EDIT{character}")


@route.command()
@click.argument('character')
@click.argument('property')
def qc(call_char, character, property):
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
@click.option('--cmds', default='')
@click.pass_obj
def connect(character, target, auth, cmds):
    file = [file for file in os.listdir(
        './flavor_text') if target.lower() in file.lower()]
    if len(file) > 0:
        target = file[0]
    else:
        print(f'No target matching request "{target}"')
        return
    connect_character(character, target)
    with open(f'./flavor_text/{target}') as target:
        target = json.load(target)
        admin = 'access_code' in target.keys(
        ) and auth == target['access_code']
        Base(target, admin, character, cmds=cmds).get_type().display()


@route.group()
@click.pass_context
def roll(ctx):
    pass


@roll.command()
@click.option('--stat', default=None)
@click.option('--D', default=10, type=click.INT)
@click.option('--skill', default='')
@click.pass_obj
def skillcheck(character, stat, d, skill):
    msg = base_roll([stat], d, skill, character)
    print(msg)


@roll.command()
@click.pass_obj
def facedown(character):
    msg = base_roll(['cool', 'rep'], 10, None, character)
    print('This is the final facedown!')
    print(msg)


@roll.command()
@click.pass_obj
def initiative(character):
    msg = 'Rolling for initiative: ' + \
        base_roll(['REF'], 10, None, character) + '\n'
    msg += 'Special case: if a QUICK DRAW is declared, add 3 to intiative roll' \
        ' and take 3 extra damage in the current combat round.'
    print(msg)


def get_weapon_skill(weapon, character):
    skill = 0
    if weapon.weapon_type.lower() == 'hvy':
        skill = query_character(character, 'Heavy Weapons')[1]
    elif weapon.weapon_type.lower() == 'p':
        skill = query_character(character, 'Handgun')[1]
    elif weapon.weapon_type.lower() == 'smg':
        skill = query_character(character, 'Submachinegun')[1]
    elif weapon.weapon_type.lower() == 'rif' or weapon.weapon_type.lower() == 'sht':
        skill = query_character(character, 'Rifle')[1]
    return int(float(skill))

def get_hit_number(weapon, range):
    point_blank = 10
    close = 15
    medium = 20
    long = 25
    extreme = 30
    w_range = int(weapon.range.split('m')[0])
    if range < 0:
        raise ValueError("Combat range must be positive")
    elif range < round(w_range/4):
        return point_blank
    elif round(w_range/2) > range >= round(w_range/4):
        return close
    elif w_range > range >= round(w_range/2):
        return medium
    elif w_range*2 > range >= w_range:
        return long
    else:
        return extreme


def check_hit(weapon, range, character, modifier):
    roll = random.randrange(1, 11)
    ref = int(query_character(character, 'ref')[1])
    weapon_skill = get_weapon_skill(weapon, character)
    hit_number = get_hit_number(weapon, range)
    result = roll + ref + weapon_skill + modifier
    success = result >= hit_number
    print(f"{character} {'hit' if success else 'missed'} with their {weapon.flavor} [Rolled {roll} + REF {ref} + skill {weapon_skill} with {'' if modifier<0 else '+'}{modifier} = {result} vs {hit_number}]")
    return success

def check_melee_hit(character, opponent, skill, modifiers, attack):
    attack = 'smashe' if attack is None else attack
    attacker_ref = int(query_character(character,'ref')[1])
    defender_ref = int(query_character(opponent,'ref')[1])
    attacker_roll = random.randrange(1, 11)
    defender_roll = random.randrange(1, 11)
    attacker_result = attacker_ref + attacker_roll + modifiers
    defender_result = defender_ref + defender_roll
    success = attacker_result > defender_result
    print(f"{character} {attack+'d' if success else 'failed'} [Rolled {attacker_roll} + skill {skill} + REF {attacker_ref}  with {'' if modifiers<0 else '+'}{modifiers} = {attacker_result} vs {defender_result}]")
    return success

def melee_attack(character, opponent, modifiers, loc, weapon=None, attack=None):
    skill = 0
    damage = 0
    btm = 0
    if attack is not None:
        bt = int(query_character(character, 'body')[1])
        if bt <= 2:
            btm = -2
        elif bt <= 4:
            btm = -1
        elif bt <= 7:
            btm = 0
        elif bt <= 9:
            btm = 1
        elif bt == 10:
            btm = 2
        elif bt <= 12:
            btm = 4
        elif bt <= 14:
            btm = 6
        elif bt >= 15:
            btm = 8

        if attack == 'dodge':
            dodge = query_character(character, attack)[1]
            skill += 0 if dodge == '' else int(dodge)
        else:
            brawl = query_character(character, 'brawling')[1]
            skill += 0 if brawl == '' else int(brawl)
        if attack == 'strike':
            damage = round(random.randrange(1,7)/2) + btm
        elif attack == 'kick':
            damage = random.randrange(1,7) + btm
    elif weapon is not None:
        melee = query_character(character, 'melee')[1]
        skill += 0 if melee == '' else int(melee)
        damage = roll_damage(weapon)
    
    if not check_melee_hit(character, opponent, skill, modifiers, attack):
        return
    if attack is not None and attack not in ['strike', 'kick']:
        return
    msg = f"Hit {opponent}'s {loc}, dealing "
    sp = query_character(opponent, loc)[1]
    rolled = damage
    final_damage = calculate_damage(sp, btm, msg, damage, loc, opponent, rolled)
    deal_damage(opponent, final_damage)
    
def roll_damage(weapon):
    # Roll for damage
    # Assuming weapon.damage_ammo is always in the form of "XDY+Z (mm)"
    damage = 0
    damage_stat = weapon.damage_ammo.lower().split('(')[0]
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
    return damage

@roll.command()
@click.argument('weapon_name')
@click.argument('opponent')
@click.argument('distance', default=0)
@click.option('--modifiers', default='')
@click.option('--target', type=click.Choice(['head', 'torso', 'right arm', 'left arm', 'right leg', 'left leg']), default=None)
@click.pass_obj
def attack(character, weapon_name, opponent, distance, modifiers, target):
    """
    :param weapon: Pick a weapon from your inventory to use in the 
        current combat round. Allowed values: Names of weapons you own.
    :param opponent: Name of the person you are fighting against.
    """
    # TODO: Make the docstring keep its formatting when
    # printed with --help
    # Get weapon stats
    body_map = {
        "head": [1],
        "torso": [2, 3, 4],
        "right arm": [5],
        "left arm": [6],
        "right leg": [7, 8],
        "left leg": [9, 10]
    }
    modifier = 0 if modifiers == '' else sum(
        [int(m) for m in modifiers.split(',')])

    if target is None:
        # Roll for hit location
        loc = random.randrange(1, 11)
        loc = [k for k, v in body_map.items() if loc in v][0]
    else:
        loc = target
        modifier -= 4

    melee_attacks = ['strike','kick','block','parry','dodge','disarm','throw','hold','escape','choke','trip','grapple']
    if weapon_name.lower() in melee_attacks:
        return melee_attack(character, opponent, modifier, loc, attack=weapon_name.lower())
    weapon = get_weapon_from_character(character, weapon_name)
    if weapon.weapon_type == 'MEL':
        return melee_attack(character, opponent, modifier, loc, weapon=weapon)

    if not check_hit(weapon, int(distance), character, modifier):
        return

    msg = f"Hit {opponent}'s {loc}, dealing "
    # Get opponent's SP based on location
    sp = query_character(opponent, loc)[1]

    # Get opponent's body type
    btm = query_character(opponent, 'btm')[1]

    rolled = roll_damage(weapon)
    damage = rolled

    # Compute final damage on opponent
    damage = calculate_damage(sp, btm, msg, damage, loc, opponent, rolled)    
    deal_damage(opponent, damage)

def calculate_damage(sp, btm, msg, damage, loc, opponent, rolled):
    sp_msg = ''
    head_msg = ''
    btm_msg = ''
    if sp:
        damage -= int(sp)
        sp_msg = f' - SP {sp}'
    # Body type modifier can't reduce damage below 1
    if loc == 'head' and damage > 0:
        damage = damage * 2
        head_msg = ' x 2 (headshot)'
    if btm and damage > 1:
        damage -= int(btm)
        btm_msg = f' - BTM {btm}'
        if damage <= 0:
            damage = 1
    # Update opponent's wounds
    if damage < 0:
        damage = 0
    msg += f"{damage} damage [Rolled {rolled}{sp_msg}{head_msg}{btm_msg}]"
    print(msg)
    if damage >= 8:
        if loc == 'head':
            print(f"{opponent}'s head explodes in a pulpy mess")
        else:
            print(f"{opponent}'s {loc} is mangled beyond recognition")
            death_save(opponent, 3)
    return damage

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
@click.pass_context
def save(ctx):
    pass


@save.command()
@click.pass_obj
def stun(character):
    """
    Roll a stun save
    """
    bt = int(query_character(character, 'body')[1])
    wound_status = get_wound_status(character)
    roll = random.randrange(1, 11)
    success = roll < (bt - wound_status)
    status = 'succeeded' if success else 'failed'
    print(
        f'Stun save {status}: rolled {roll} vs {bt - wound_status} [body type ({bt}) - wound status ({wound_status})]')


@save.command()
@click.pass_obj
def death(character):
    death_save(character)


def death_save(character, ws=None):
    """
    Roll a death save
    """
    bt = int(query_character(character, 'body')[1])
    wound_status = get_wound_status(character) if ws is None else ws
    roll = random.randrange(1, 11)
    success = roll < (bt - wound_status - 3)
    status = 'succeeded' if success else 'failed'
    print(
        f'Death save {status}: rolled {roll} vs {bt - wound_status - 3} [body type ({bt}) - wound status ({wound_status - 3})]')


def base_roll(stats, d, skill, character):
    result = random.randrange(1, d+1)
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
    message = f"{character} rolled a {total}! [{result} (roll) + {stat_notification}{skill_notification}"
    return message
