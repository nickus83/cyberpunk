import re
from dataclasses import dataclass
from pathlib import Path
from random import choice
from typing import Tuple

import dice
import yaml
from faker import Faker

fake = Faker()

def generate_name(sex: str) -> str:
    """
    Generates a name based on the given sex.

    Parameters:
        sex (str): The sex of the person. Can be 'female' or 'male'.

    Returns:
        str: The generated name based on the given sex.
    """
    if sex == 'female':
        return fake.name_female()
    else:
        return fake.name_male()

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

    def __post_init__(self) -> None:
        """Main create functions. Generates character role attributes
            based on given role and corresponding tables.
            This method (and class) is abstract  dont't create this object/

        Args:
            role (str): name of a role
        """
        self.class_name = self.role.capitalize()

        if self.name is None:
            self.name = generate_name(self.sex)

        if self.sex == 'female':
            self.appeal = 'she'
            self.appeal_other = 'her'
        else: # TODO: name dependency from cultiral origins
            self.appeal = 'he' # TODO check for appeal he/she in message roles
            self.appeal_other = 'his'

        self.cultural_region, self.language = self.cultural_origins()

        self.set_attributes(self.attributes_names)

        self.friends = self.get_friends_enemies_or_love(Friend)
        self.enemies = self.get_friends_enemies_or_love(Enemy)
        self.love = self.get_friends_enemies_or_love(Love)

    def set_attributes(self, attributes_names: list) -> None:
        """
        Set attributes based on the given attribute names list.
        Args:
            attributes_names (list): A list of attribute names
        """

        #TODO: set atributes at random or manualy, for now only random
        self.random_attributes(attributes_names)


    def random_attributes(self, attributes_names: list) -> None:
        """Convert a list of names to attributes leading to correstonding tables
            and take a random value from the table
        Args:
            attributes_names (list): list of names that will be the attributes
        """
        for attribute_name in attributes_names:
            table_name = attribute_name.replace('_', ' ').title()
            self.__dict__[attribute_name] = self.tables[table_name][dice.roll('1d10t')]

    def chosen_atribute(self, attribute_names: str) -> None:
        ... #TODO: for manualy choosing atributes


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
        else: # TODO: fix on a possibilty, not a very good decishion. Capitalize works wrong on word with "/"
            keywords = " ".join([word.capitalize() for word in keyword.split(' ')])

        return self.tables[self.class_name + ' ' + keywords][dice.roll(f'1d{int(dice_number)}t')]

    @staticmethod # TODO: make separate function, not a class method
    def lower_first(input: str) -> str:
        """
        Convert the first character of a string to lowercase.

        Args:
            input (str): The string to convert.

        Returns:
            str: The converted string.
        """
        return input[0].lower() + input[1:]

    def cultural_origins(self) -> Tuple[str, str]:
        """
        Get a random cultural origin and language.
        Returns:
            Tuple[str, str]: A tuple containing the cultural region and language.
        """
        roll = dice.roll('1d10t')
        region = self.tables['Cultural Origins'][roll]['Cultural Region']

        # If the region contains multiple options, choose one randomly
        if '/' in region:
            region = choice(region.split('/'))

        language = choice(self.tables['Cultural Origins'][roll]['Languages'])
        return (region, language)

    def get_friends_enemies_or_love(self, class_name):
        """
        Generate a list of instances of the given class name.

        Args:
            class_name (class): The name of the class to instantiate.

        Returns:
            list: A list of instances of the given class name.
        """
        result = []

        # Generate a random number between 0 and 3.
        # If the result of the dice roll is less than or equal to 7, set the number to 0.
        # Otherwise, subtract 7 from the dice roll result.
        number = max(0, dice.roll('1d10t') - 7)

        # Instantiate the given class name `number` times and append the instances to the result list.
        for _ in range(number):
            result.append(class_name(self.tables))

        return result

    def __str__(self):
        # Generate the crisis description based on the family crisis and appeal_other
        crisis = self.lower_first(self.family_crisis).replace('your', self.appeal_other)
        crisis = crisis.replace('you', self.appeal_other)

        # Generate the first part of the message including name, sex, role, and character type
        message_first = (
            f'Name: {self.name} ({self.sex})\n'
            f'Role: {self.role.capitalize()}. {self.character_type}\n'
        )

        # Generate the description of the person including appeal, cultural region, language, personality, etc.
        message_person = (
            f'Person:\n'
            f'{self.appeal.capitalize()} is from {self.cultural_region} region. Speaks {self.language}.\n'
            f'{self.appeal.capitalize()} is {self.lower_first(self.personality)}.\n'
            f'{self.appeal.capitalize()} is wearing {self.clothing_style}.\n'
            f'{self.appeal_other.capitalize()} hairstyle is {self.lower_first(self.hairstyle)}. '
            f'{self.appeal_other} affectation is {self.lower_first(self.affectation)}.\n'
            f'{self.appeal.capitalize()} is value {self.lower_first(self.motivation)} the most. '
            f'{self.appeal} feels about others "{self.relationships}".\n'
            f'{self.most_valued_person} is {self.lower_first(self.appeal_other)} most valued person.\n'
            f'{self.appeal_other.capitalize()} {self.most_valued_possession[2:]} is most valued possession.\n'
            f'Family:\n'
            f'{self.appeal.capitalize()} is from {self.family_background[0]} family.\n'
            f'"{self.family_background[1]}"\n'
            f'{self.appeal.capitalize()} where spend {self.lower_first(self.appeal_other)} childhood '
            f'{self.lower_first(self.childhood_environment)}\n'
            f'But {crisis}\n'
            f'Life goals: {self.life_goals}\n'
            f'Friends:\n{self.friends}\n'
            f'Enemies:\n{self.enemies}\n'
            f'Love affairs:\n{self.love}'
        )

        # Combine all the parts of the message and return it
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
        self.name = generate_name(self.sex)

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
        self.name = generate_name(self.sex)
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

    def __post_init__(self) -> None:
        # Call the parent class method to create the role
        super().__post_init__()

        # Set the character type using the 'Type' table
        self.character_type = self.get_table('Type', 10)

        # Determine if the character has a partner or not
        if choice([0, 1]):
            self.partner = self.get_table('Partner', 6)

        # Create a message with the partner information
        partner_message = f"Partner: {self.partner}" if self.partner else ""

        # Set the office, clients, and gunning attributes using their respective tables
        self.office = self.get_table('Office', 6)
        self.clients = self.get_table('Side Clients', 6)
        self.gunning = self.get_table('Gunner', 6)

        # Create the final message with all the information
        self.message_role = (
            f"{partner_message}\n"
            f"Office: {self.office}\n"
            f"Clients: {self.clients.replace('you', self.appeal_other)}\n"
            f"Gunning: {self.gunning.replace('you', self.appeal_other)}\n"
    )


@dataclass
class Media(Character):
    character_type: str = None
    source: str = None
    ethics: str = None
    stories: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 6)
        self.source = self.get_table('Source', 6)
        self.ethics = self.get_table('Ethics', 6)
        self.stories = self.get_table('Stories', 6)

        self.message_role = (f"Works in {self.lower_first(self.source)}. Write about {self.stories.lower()}.\n"
                             f"{self.ethics.replace('You', self.appeal.capitalize())}\n"
                             )


@dataclass
class Exec(Character):
    character_type: str = None
    division: str = None
    good_or_bad: str = None
    based: str = None
    gunning: str = None
    boss: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
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
                            f"Gunning: { self.gunning.replace('you', self.appeal_other)}\n"
                            f"{self.boss.replace('Your', self.appeal_other.capitalize()).replace('your', self.appeal_other).replace('you', self.appeal_other)}\n")


@dataclass
class Rockerboy(Character):
    character_type: str = None
    in_group: bool = None
    perform: str = None
    were_in_group: bool = None
    leave: str = None
    gunning: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 10)
        self.in_group = choice([True, False]) #TODO: make it True, False everywhere

        if self.in_group == False:
            self.were_in_group = choice([True, False])
            if self.were_in_group == True:
                self.leave = self.get_table('Leave', 6)

        self.perform = self.get_table('Perform', 6)
        self.gunning = self.get_table('Gunning', 6)

        if self.leave:
            temp_leave = self.leave.replace('''you''', self.appeal).replace('''You''', self.appeal).lower()
        self.message_role = (f"{'Perform alone' if self.in_group else 'Perform in group'}."
                            f"{f' Where in a group but, {temp_leave}' if self.were_in_group else ''}\n"
                            f"Perform in {self.perform.lower()}\n"
                            f"Gunning {self.gunning.replace('you', self.appeal_other)}\n"
                            )


@dataclass
class Solo(Character):
    character_type: str = None
    moral_compass: str = None
    operational_territory: str = None
    gunning: str = None # TODO check for gunning for other classes. gunning is who hunts the character

    def __post_init__(self) -> None:
        super().__post_init__()
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

        self.message_role = (f"{self.moral_compass.replace('You', self.appeal_other.capitalize()).replace('you', self.appeal_other)}\n"
                            f"Works in {self.lower_first(self.operational_territory.replace('you', self.appeal_other))}.\n"
                            f"{self.gunning.replace('you', self.appeal_other)} is after {self.appeal_other}.\n"
            )


@dataclass
class Netrunner(Character):
    character_type: str = None
    alone: bool = None
    partner: str = None
    workspace: str = None
    clients: str = None
    supplies: str = None
    gunning: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 6)
        self.alone = choice([True, False])
        if not self.alone:
            self.partner = self.get_table('Partner', 6)
        self.workspace = self.get_table('Workspace', 6)
        self.clients = self.get_table('Clients', 6)
        self.supplies = self. get_table('Supplies', 6)
        self. gunning = self.get_table('Gunning', 6)

        self.message_role = (f"Works {'alone.' if self.alone else 'with partner, a ' + self.lower_first(self.partner)}\n"
                            f"Workspace: {self.workspace}\n"
                            f"Clients: {self.clients.replace('your', self.appeal_other).replace('you', self.appeal_other).replace('You', self.appeal_other.capitalize())}\n"
                            f"How get programs - {self.lower_first(self.supplies.replace('you', self.appeal_other)).replace('You', self.appeal_other.capitalize())}\n"
                            f"May harm {self.appeal_other} {self.lower_first(self.gunning.replace('you', self.appeal_other)).replace('You', self.appeal_other.capitalize())}\n"
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

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 10)

        self.alone = choice([True, False])
        if not self.alone:
            self.partner = self.get_table('Partner', 6)
        self.workspace = self.get_table('Workspace', 6)
        self.clients = self.get_table('Clients', 6)
        self.supplies = self.get_table('Supplies', 6)
        self.gunning = self.get_table('Gunning', 6)

        self.message_role = (f"Works {'alone' if self.alone else 'with partner ' + self.lower_first(self.partner)}.\n"
                            f"Workspace: {self.workspace.replace('you', self.appeal)}\n"
                            f"Clients: {self.clients.replace('you', self.appeal_other).replace('You', self.appeal_other.capitalize())}\n"
                            f"{self.appeal.capitalize()} {self.lower_first(self.supplies).replace('You', '').replace('you', self.appeal)}\n"
                            f"Gunning: {self.gunning.replace('you', self.appeal_other).replace('You', self.appeal_other.capitalize())}\n"
                            )


@dataclass
class Medtech(Character):
    character_type: str = None #TODO: move all deafult fields to parent class
    alone: bool = None
    partner: str =  None
    workspace: str = None
    clients: str = None
    supplies: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 10)
        self.alone = choice([True, False])
        if not self.alone:
            self.partner = self.get_table('Partner', 6)
        self.workspace = self.get_table('Workspace', 6)
        self.clients = self.get_table('Clients', 6)
        self.supplies = self.get_table('Supplies', 6)

        self.message_role = (f"Works {'alone' if self.alone else 'with partner ' + self.lower_first(self.partner)}.\n"
                        f"Workspace: {self.workspace}\n"
                        f"Clients: {self.clients}\n"
                        f"Supplies: {self.supplies}\n"
                        )


@dataclass
class Lawman(Character):
    character_type: str = None # other attributes is unique
    jurisdiction: str = None
    corrupt: str = None
    gunning: str = None
    target: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.character_type = self.get_table('Type', 6)
        self.jurisdiction = self.get_table('Jurisdiction', 6)
        self.corrupt = self.get_table('Corrupt', 6)
        self.gunning = self.get_table('Gunning', 6)
        self.target = self.get_table('Target', 6)

        self.message_role = (f"Works in {self.jurisdiction}.\n"
                             f"{self.corrupt}\n"
                             f"{self.gunning} is after {'him' if self.sex=='male' else 'her'}.\n"
                             f"{self.target} is {'his' if self.sex=='male' else 'her'} main target.\n"
                             )


@dataclass
class Nomad(Character):
    character_type: str = ''
    pack_size: str = None
    pack_type: str = None
    pack_do: str = None
    pack_role: str = None
    pack_philosophy: str = None
    pack_gunning: str = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.pack_size = self.get_table('Pack Size', 6)

        self.pack_type = choice(['land', 'air', 'sea'])
        if self.pack_type == 'land':
            self.pack_do = self.get_table('Land', 10)
        elif self.pack_type == 'air':
            self.pack_do = self.get_table('Air', 6)
        elif self.pack_type == 'sea':
            self.pack_do = self.get_table('Sea', 6)

        self.pack_role = self.get_table('Role', 6)
        self.pack_philosophy = self.get_table('Pack Philosophy', 6)
        self.pack_gunning = self.get_table('Pack Gunning', 6)

        self.message_role = (f"Pack size: {self.pack_size}.\n"
                             f"Pack operates on {self.pack_type}.\n"
                             f"Pack doing a {self.lower_first(self.pack_do)}.\n"
                             f"{self.pack_philosophy}\n"
                             f"{self.pack_gunning} is after pack.\n"
                             f"{'his'.capitalize() if self.sex=='male' else 'her'.capitalize()} role is {self.pack_role}.\n"
                             )


def main(name, role, sex, tables_path='data/tables.yaml'):
    """
    Generate the main character of the game based on the given name, role, sex, and tables path.

    Args:
        name (str): The name of the character.
        role (str): The role of the character. If not provided, a random role will be chosen from the available roles.
        sex (str): The sex of the character. If not provided, a random sex will be chosen.
        tables_path (str): The path to the tables file.

    Returns:
        None
    """
    # TODO: fix random seed
    # TODO: fix faker seed
    with open(Path(__file__).parent.resolve() / tables_path) as fo:
        tables = yaml.safe_load(fo)

    if not role:
        role = choice(tables['roles']).lower()
    else:
        role = role.lower()

    message = f"No such role '{role}'. Choose from {[i for i in tables['roles']]}"
    assert role.capitalize() in tables['roles'], message
    # TODO: write tests for varios classes
    if not sex:
        sex = choice(['male', 'female'])

    role_class = globals()[role.capitalize()]
    char = role_class(name, role, sex, tables)

    return char

    #TODO: try translator library for Russian https://pypi.org/project/translators/
    #TODO: move all characters classes to separate file
    #TODO: try something to check right sentences

if __name__ == '__main__':
    from argparse import ArgumentParser
    parse = ArgumentParser(
        description="Create random character for Cyberpunk Red")
    parse.add_argument('-n', '--name', required=False, type=str,
                       help='name of a character')
    parse.add_argument('-r', '--role', required=False, type=str,
                       default=None,
                       help='role of a character, random choice if not set')
    parse.add_argument('-s', '--sex', default=None, type=str,
                       help='sex of a character, random choice if not set')
    parse.add_argument('-t', '--tables-path', default='data/tables.yaml',
                       type=Path, help='relative path to tables yaml file, data/tables.yaml as default')
    args = parse.parse_args()


    print(main(**vars(args)))
