from dataclasses import dataclass
from pathlib import Path
from random import choice
import re

import dice
import yaml
from faker import Faker
fake = Faker()

@dataclass
class Character:
    name: str
    role: str
    sex: str
    tables: dict
    class_name: str = None
    cultural_region: str = None
    language: str = None
    personality: str = None
    clothing_style: str = None
    hairstyle: str = None
    affectation: str = None
    motivation: str = None
    relationships: str = None
    most_valued_person: str = None
    most_valued_possession: str = None
    family_background: str = None
    childhood_environment: str = None
    family_crisis: str = None
    life_goals: str = None

    friends: list = None
    enemies: list = None
    love: list = None

    message_role: str = ''

    def create(self, role: str) -> None:
        self.class_name = role.capitalize()

        if self.name == None:
            if self.sex == 'female':
                self.name = fake.name_female()
                self.appeal = 'she'
            else: # TODO: name dependency from cultiral origins
                self.name = fake.name_male()
                self.appeal = 'he' # TODO check for appeal he/she in message roles

        self.cultural_region, self.language = self.cultural_origins()

        attributes_names = ['personality',
                            'clothing_style',
                            'hairstyle',
                            'affectation',
                            'motivation',
                            'relationships',
                            'most_valued_person',
                            'most_valued_possession',
                            'family_background',
                            'childhood_environment',
                            'family_crisis',
                            'life_goals']

        self.from_table(attributes_names)

        self.friends = self.get_friends_enemies_or_love(Friend)
        self.enemies = self.get_friends_enemies_or_love(Enemy)
        self.love = self.get_friends_enemies_or_love(Love)
    # TODO: write docstrings for methods
    def from_table(self, attributes_names):
        for attribute_name in attributes_names:
            table_name = attribute_name.replace('_', ' ').title()
            self.__dict__[
                attribute_name] = self.tables[table_name][dice.roll('1d10t')]

    def get_table(self, keyword: str, dice_number: int) -> str:
        """Finds corresponing table based on class name and given keyword
        Args:
            keyword (str): keyword that is second part of the table name
            dice_number (int): number of sides of dice that is thrown on this table, usialy size of a table
        Returns:
            str: row from a table. number of which where rolled on the dice
        """
        if "/" in keyword:
            keywords = keyword
        else: # TODO: fix on a possibilty, not a very good decicion. Capitalize works wrong on word with "/"
            keywords = " ".join([word.capitalize() for word in keyword.split(' ')])

        return self.tables[self.class_name + ' ' + keywords][dice.roll(f'1d{int(dice_number)}t')]

    @staticmethod # TODO check for lower first letter in other places
    def lower_first(input: str) -> str:
        return input[0].lower() + input[1:]

    def cultural_origins(self):
        roll = dice.roll('1d10t')
        region = self.tables['Cultural Origins'][roll]['Cultural Region']
        if '/' in region:
            region = choice(region.split('/'))

        language = choice(self.tables['Cultural Origins'][roll]['Languages'])
        return (region, language)

    def get_friends_enemies_or_love(self, class_name):
        result = []

        number = max(0, dice.roll('1d10t') - 7)
        for _ in range(number):
            result.append(class_name(self.tables))
        return result

    def __str__(self):
        calling = 'He' if self.sex == 'male' else 'She'
        calling_other = "His" if self.sex == 'male' else 'Her'

        def lowfirst(s): return s[:1].lower() + s[1:] if s else ''
        family_crisis = lowfirst(self.family_crisis).replace(
            'your', lowfirst(calling_other))
        family_crisis = family_crisis.replace('you', lowfirst(calling_other))

        message_first = (f'Name: {self.name} ({self.sex})\n'
                    f'Role: {self.role.capitalize()}. {self.character_type}\n')
        message_person = (f'Person:\n'
                f'{calling} is from {self.cultural_region} region. Speaks {self.language}.\n'
                f'{calling} is {lowfirst(self.personality)}.\n'
                f'{calling} is wearing {self.clothing_style}.\n'
                f'{calling_other} hairstyle is {lowfirst(self.hairstyle)}. {calling_other} affectation is {lowfirst(self.affectation)}.\n'
                f'{calling} is value {lowfirst(self.motivation)} the most. {calling} feels about others "{self.relationships}".\n'
                f'{self.most_valued_person} is {lowfirst(calling_other)} most valued person.\n'
                f'{calling_other} {self.most_valued_possession[2:]} is most valued possession.\n'
                f'Family:\n{calling} is from {self.family_background[0]} family.\n'
                f'"{self.family_background[1]}"\n'
                f'{calling} where spend {lowfirst(calling_other)} childhood {lowfirst(self.childhood_environment)}\n'
                f'But {family_crisis}\n'
                f'Life goals: {self.life_goals}\n'
                f'Friends:\n{self.friends}\n'
                f'Enemies:\n{self.enemies}\n'
                f'Love affairs:\n{self.love}'
                )

        return message_first + self.message_role + message_person


class Friend(object):
    def __init__(self, tables) -> None:
        self.relationship = tables['Friend'][dice.roll('1d10t')]
        self.name = fake.name()

    def __repr__(self) -> str:
        return (f'{self.name}. {self.relationship}')


class Enemy(object):
    def __init__(self, tables) -> None:
        self.enemy_type = tables['Enemy type'][dice.roll('1d10t')]

        self.sex = choice(['male', 'female'])
        if self.sex == 'female':
            self.name = fake.name_female()
        else:
            self.name = fake.name_male()

        self.wrong = tables['Enemy wrong'][dice.roll('1d10t')]
        self.throw = self._get_enemy_throw(tables)
        self.meet = tables['Enemy meet'][dice.roll('1d10t')]

    @staticmethod
    def lowfirst(s): return s[:1].lower() + s[1:] if s else ''

    def _get_enemy_throw(self, tables):
        result = tables['Enemy throw'][dice.roll('1d10t')]
        template = r'\{.*?\}'

        replace = re.findall(template, result)
        if len(replace) > 0:
            number = dice.roll(replace[0][1:-1])
            result = re.sub(template, str(number), result)

        return result

    def __repr__(self) -> str:
        return (f'{self.name} ({self.sex}) ({self.enemy_type}) {self.wrong} '
                f'Can throw {self.lowfirst(self.throw)} If meet: {self.meet}')

class Love(object): # TODO: pass character sex as argument and make love sex choice opposite to characer sex
    def __init__(self, tables) -> None: # TODO think about straight of homo of character
        self.sex = choice(['male', 'female'])
        if self.sex == 'female':
            self.name = fake.name_female() # TODO make this a function, code repeats
        else:
            self.name = fake.name_male()

        self.happend = tables['Love happened'][dice.roll('1d10t')]

    def __repr__(self) -> str:
        return f'{self.name} ({self.sex}). {self.happend}'


@dataclass
class Fixer(Character):
    character_type: str = None
    partner: str = None
    office: str = None
    clients: str = None
    gunning: str = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 10)

        if choice([0, 1]): # have partner or not
            self.partner = self.get_table('Partner', 6)
        partner_message = f"Partner: {self.partner}"

        self.office = self.get_table('Office', 6)
        self.clients = self.get_table('Side Clients', 6)
        self.gunning = self.get_table('Gunner', 6)

        self.message_role = (f"{partner_message}\nOffice: {self.office}\n"
                            f"Clents: {self.clients}\n"
                            f"Gunning for you: {self.gunning}\n")


@dataclass
class Media(Character):
    character_type: str = None
    source: int = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 10)
        self.source = self.get_table('Source', 6)

        self.message_role = f"{self.source}\n"


@dataclass
class Exec(Character):
    character_type: str = None
    division: str = None
    good_or_bad: str = None
    based: str = None
    gunning: str = None
    boss: str = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 10)
        division_roll = dice.roll('1d6t')
        if division_roll == 5:
            temp = self.tables[self.class_name + ' Division'][division_roll]
            self.division = temp.split('/')[dice.roll('1d3t')-1]
        else:
            self.division = self.tables[self.class_name + ' Division'][division_roll]

        self.good_or_bad = self.get_table('Good/Bad', 6)
        self.based = self.get_table('Based', 6)
        self.gunning = self.get_table('Gunning', 6)
        self.boss = self.get_table('Boss', 6)

        self.message_role = (f"Works for '{self.character_type}'"
        f" corporation wich is '{self.good_or_bad[:-1].lower()}'"
        f" located in {self.based.lower()}"
        f" in {self.division} division.\n"
        f"Gunning: { self.gunning}\n"
        f"{self.boss}\n")


@dataclass
class Rockerboy(Character):
    character_type: str = None
    in_group: bool = None
    perform: str = None
    were_in_group: bool = None
    leave: str = None
    gunning: str = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 10)
        self.in_group = choice([True, False])

        if self.in_group == False:
            self.were_in_group = choice([True, False])
            if self.were_in_group == True:
                self.leave = self.get_table('Leave', 6)

        self.perform = self.get_table('Perform', 6)
        self.gunning = self.get_table('Gunning', 10)

        self.message_role = (f"{'Perform alone' if self.in_group else 'Perform in group'}."
            f"{f' Where in a group but, {self.leave.lower()}' if self.were_in_group else ''}\n"
            f"Perform in {self.perform.lower()}\n"
            f"Gunning {self.gunning}\n"
            )


@dataclass
class Solo(Character):
    character_type: str = None
    moral_compass: str = None
    operational_territory: str = None
    gunning: str = None # TODO check for gunning for other classes. gunning is who hunts the character

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 6)
        if '/' in self.character_type:
            temp = []
            for word in self.character_type.split(' '):
                if '/' in word:
                    word = choice(word.split('/'))

                temp.append(word)

            self.character_type = " ".join(temp)

        self.moral_compass = self.get_table('Moral Compass', 6)
        self.operational_territory = self.get_table('Operational Territory', 6)
        self.gunning = self.get_table('Gunning', 6)

        self.message_role = (f"{self.moral_compass.replace('You', self.appeal.capitalize()).replace('you', self.appeal)}\n"
                            f"Works in {self.lower_first(self.operational_territory)}.\n"
                            f"{self.gunning} is after {'him' if self.sex == 'male' else 'her'}.\n"
            )


@dataclass
class Netrunner(Character):
    character_type: str = None
    alone: bool = None
    partner: str = None
    workspace: str = None
    clients: str = None
    get_programs: str = None
    gunning: str = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 6)
        self.alone = choice([True, False])
        if not self.alone:
            self.partner = self.get_table('Partner', 6)
        self.workspace = self.get_table('Workspace', 6)
        self.clients = self.get_table('Clients', 6)
        self.get_programs = self. get_table('Get Programs', 6)
        self. gunning = self.get_table('Gunning', 6)

        self.message_role = (f"Works {'alone.' if self.alone else 'with partner, a ' + self.lower_first(self.partner)}\n"
                            f"Workspace: {self.workspace}\n"
                            f"Clients: {self.clients}.\n"
                            f"How get programs - {self.lower_first(self.get_programs).replace('You', self.appeal).replace('you', self.appeal)}\n"
                            f"May harm {'him' if self.sex == 'male' else 'her'} {self.lower_first(self.gunning)}\n"
                            )


@dataclass
class Tech(Character):
    character_type: str = None
    alone: bool = None
    partner: str = None
    workspace: str = None
    clients: str = None
    supplies: str = None
    gunning: str = None

    def create(self, role: str) -> None:
        super().create(role)
        self.character_type = self.get_table('Type', 10)

        self.alone = choice([True, False])
        if not self.alone:
            self.partner = self.get_table('Partner', 6)
        self.workspace = self.get_table('Workspace', 6)
        self.clients = self.get_table('Clients', 6)
        self.supplies = self.get_table('Supplies', 6)
        self.gunning = self.get_table('Gunning', 6)

        self.message_role = (f"Works {'alone' if self.alone else 'with partner ' + self.lower_first(self.partner)}.\n"
                            f"Workspace: {self.workspace}\n"
                            f"Clients: {self.clients}\n"
                            f"{self.appeal.capitalize()} {self.lower_first(self.supplies).replace('You', '').replace('you', self.appeal)}\n"
                            f"Gunning: {self.gunning.replace('you', self.appeal)}\n"
                            )

# TODO: Medtech class
# TODO: Lawmen class
# TODO: Nomad class

def main(name, role, sex, tables_path):
    # TODO: fix random seed
    # TODO: fix faker seed
    with open(Path.cwd() / tables_path) as fo:
        tables = yaml.safe_load(fo)

    message = f"No such role '{role}'. Choose from {[i for i in tables['roles']]}"
    assert role.capitalize() in tables['roles'], message
    # TODO: write tests for varios classes
    if not sex:
        sex = choice(['male', 'female'])

    role_class = globals()[role.capitalize()]
    char = role_class(name, role, sex, tables)
    char.create(role)

    print(char)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parse = ArgumentParser(
        description="Create random character for Cyberpunk Red")
    parse.add_argument('-n', '--name', required=False, type=str,
                       help='name of a character')
    parse.add_argument('-r', '--role', required=True, type=str,
                       help='role of a character')
    parse.add_argument('-s', '--sex', default=None, type=str,
                       help='sex of a character, random choice if not set')
    parse.add_argument('-t', '--tables-path', default='data/tables.yaml',
                       type=Path, help='relative path to tables yaml file, data/tables.yaml as default')
    args = parse.parse_args()

    main(**vars(args))
