from colorama import Fore, Back, Style
from tabulate import tabulate
import click
import getpass
from src.sheetio import query_character, update_character, disconnect_character


class Base:
    def display(self):
        if not self.options or self.cmds == '':
            if self.admin_flavor != '' and self.admin:
                print(self.admin_flavor)
            else:
                print(self.flavor)

    def get_summary(self):
        return self.flavor

    def get_properties(self):
        return self.__dict__

    def display_options(self, to_display=[]):
        if self.options:
            options = [Base(option, self.admin, self.character).get_type()
                       for option in self.options]
            if self.cmds == '':
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
                        print('```')
                        headers = [x[0] for x in tables[item_type]['table']]
                        headers = ['Stat'] + headers
                        display = []
                        for p in range(1,len(tables[item_type]['table'][0])):
                            display.append([tables[item_type]['headers'][p]] + [x[p] for x in tables[item_type]['table']])
                        print(tabulate(display,
                                       headers=headers, tablefmt="grid"))
                        print('```')
                elif isinstance(options[0], Info):
                    for i, option in enumerate(options):
                        print(f"{i+1}) {option.get_summary()}")
                print('Or q to quit')
                return
            choice = self.cmds.split(':')[0]
            self.cmds = self.cmds[1:]
            if choice == 'q':
                disconnect_character(self.character)
                print('Goodbye')
                return
            Base(self.options[int(choice)-1],
                 self.admin, self.character, cmds=self.cmds).get_type().display()

    def __init__(self, target, admin, character, cmds=''):
        self.type = target['type']
        self.target = target
        self.flavor = target['flavor']
        self.admin_flavor = target.get('admin_flavor', '')
        self.options = target.get('options', [])
        self.admin = admin
        self.character = character
        self.cmds = cmds

    def get_type(self):
        if self.type == 'store':
            return Store(self.target, self.admin, self.character, cmds=self.cmds)
        elif self.type == 'info':
            return Info(self.target, self.admin, self.character, cmds=self.cmds)
        elif self.type == 'item':
            return Item(self.target, self.admin, self.character)
        elif self.type == "weapon":
            return Weapon(self.target, self.admin, self.character)
        elif self.type == 'gear':
            return Gear(self.target, self.admin, self.character)
        elif self.type == 'armor':
            return Armor(self.target, self.admin, self.character)


class Store(Base):
    def display(self):
        super().display()
        super().display_options()

    def __init__(self, target, admin, character, cmds=''):
        super().__init__(target, admin, character, cmds=cmds)
        self.money = target['money']


class Info(Base):
    def display(self):
        super().display()
        super().display_options()

    def get_summary(self):
        return self.header

    def __init__(self, target, admin, character,  cmds=''):
        super().__init__(target, admin, character, cmds=cmds)
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
        balance = int(query_character(self.character, "money")[1])
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
        return {"flavor": "Name", "cost": "Cost (eb)"}

    def __init__(self, target, admin, character):
        super().__init__(target, admin, character)
        with open('items.csv') as items_file:
            for line in items_file.readlines()[1:]:
                item_description = line.rstrip().split('\t')
                if self.flavor.lower() in item_description[0].lower():
                    self.cost = item_description[1]
                    self.weight = item_description[2]
                    break


class Gear(Item):
    def __init__(self, target, admin, character):
        super().__init__(target, admin, character)

    def get_type_name(self):
        return "Gear"

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({"weight": "Weight (kg)"})
        return fields

    def checkout_update(self):
        update_character(self.character, "gear", [
            self.flavor, self.cost, self.weight])


class Armor(Item):
    def get_type_name(self):
        return "Armor"

    def __init__(self, target, admin, character):
        super().__init__(target, admin, character)
        with open('armor.csv') as armor_file:
            for line in armor_file.readlines()[1:]:
                armor_description = line.rstrip().split('\t')
                if target['flavor'].lower() in armor_description[0].lower():
                    self.flavor = armor_description[0]
                    self.covers = armor_description[1]
                    self.sp = armor_description[2]
                    self.ev = armor_description[3]
                    self.cost = armor_description[4]
                    break

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({
            "covers": "Coverage",
            "sp": "Stopping Power",
            "ev": "Encumberance"
        })
        return fields

    def checkout_update(self):
        update_character(self.character, "armor", [
            self.flavor, self.covers, self. sp, self.ev, self.cost])


class Weapon(Item):
    def get_type_name(self):
        return "Weapons"

    def __init__(self, target, admin, character):
        super().__init__(target, admin, character)
        found = False
        with open('weapons.csv') as weapons_file:
            for line in weapons_file.readlines()[1:]:
                weapon_description = line.rstrip().split('\t')
                if target['flavor'].lower() in weapon_description[0].lower():
                    self.flavor = weapon_description[0]
                    self.weapon_type = weapon_description[1]
                    self.accuracy = weapon_description[2]
                    self.con = weapon_description[3]
                    self.avail = weapon_description[4]
                    self.damage_ammo = weapon_description[5]
                    self.num_shots = weapon_description[6]
                    self.rof = weapon_description[7]
                    self.rel = weapon_description[8]
                    self.range = weapon_description[9]
                    self.cost = weapon_description[10]
                    found = True
                    break
            if not found:
                raise Exception(
                    f"Could not find {target['flavor']} in weapons index")

    def get_display_fields(self):
        fields = super().get_display_fields()
        fields.update({
            'weapon_type': 'Type',
            "accuracy": "Accuracy",
            "con": "Concealability",
            "avail": "Availability",
            "damage_ammo": "Damage/Ammo",
            "num_shots": "#Shots",
            "rof": "Rate of Fire",
            "rel": "Reliability",
            "range": "Range"
        })
        return fields

    def checkout_update(self):
        update_character(self.character, "weapon", [
            self.flavor, self.weapon_type, self.accuracy, self.con,
            self.avail, self.damage_ammo, self.num_shots, self.rof,
            self.rel, self.range, self.cost
        ])
