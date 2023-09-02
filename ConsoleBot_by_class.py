from collections import UserDict
from collections.abc import Iterator
from datetime import datetime
from prettytable import PrettyTable
from dataclasses import dataclass
import pickle

class AddressBook(UserDict):
    '''The only Address book'''
    instance = None
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(AddressBook, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        super().__init__()
        self.data = {}
        self.idx = 0
        self.end_idx = 0
        self.filename = 'AddressBook.bin'

    def add_record(self, record):
        '''Add some contact'''
        key = record.name.value
        self.data[key] = record

    def __next__(self):
        sheet = PrettyTable()
        keys = tuple(enumerate(self.data.keys()))
        sheet.field_names = ['Name', 'Phone', 'Days to birthday']
        if self.end_idx == len(self):
            self.idx = 0
            self.end_idx = 0
            raise StopIteration
        self.end_idx = self.idx + 2 if (self.idx + 2) <= len(self) else len(self)
        for _, key in keys[self.idx : self.end_idx]:
            sheet.add_row([
                key,
                self.data[key].phone.value,
                self[key].days_to_birthday()
            ])
            self.idx += 1
        return sheet

    def __iter__(self) -> Iterator:
        return self

    def handler(self, command: str, args) -> str:
        '''Handle commands'''

        errors = {
            1: 'Enter valid command!',
            2: 'Username not found',
            3: 'Enter valid username and(or) phone (phone must contain only digits)',
            4: 'Number not found',
            5: 'Please enter date using format "YYYY-MM-DD"',
            6: 'File not found!',
            7: PhoneExistError.__doc__
        }
        
        def greet():
            return 'Hello!\nHow can I help you?'


        def add(name_value: str, phone_value=None, birth_value=None) -> str:
            '''Add user number and/or birthday into database'''
            try:
                if birth_value:
                    birth_value = datetime.strptime(birth_value, '%Y-%m-%d')
            except ValueError as err:
                raise DateError from err

            if name_value in ab.keys():
                if phone_value:
                    if not ab[name_value].phone:
                        phone = Phone()
                        phone.value = phone_value
                        ab[name_value].phone = phone
                    else:
                        raise PhoneExistError
                if birth_value:
                    birthday = Birthday()
                    birthday.value = birth_value
                    ab[name_value].birthday = birthday
                return 'Done'

            name = Name()
            name.value = name_value

            phone = Phone()
            phone.value = phone_value

            birthday = Birthday()
            birthday.value = birth_value
            
            rec = Record(name, phone, birthday)
            ab.add_record(rec)
            return 'Done'


        def change(name, old_number, new_number) -> str:
            '''Change user number'''

            if name not in self.keys():
                raise UsernameError

            for phone in self[name].phones:
                if phone.value == old_number:
                    phone.value = new_number
                    return 'Done'

            raise ValueError

        def show(name: str) -> str:
            '''Show User phone.\n
            If key: 'all' - show all contacts'''

            if name == 'all':
                if self.keys():
                    for sheet in self:
                        return sheet

            else:
                user = PrettyTable()
                user.field_names = ['Name', 'Phone', 'Days to birthday']
                user.add_row([
                    self[name].name.value,
                    self[name].phone.value,
                    self[name].days_to_birthday()
                    ])
                return user
            return 'End list'    
        
        try:
            if command == 'hello':
                return greet()
            elif command == 'add':
                return add(args[0], args[1], args[2])
            elif command == 'change':
                return change(args[0], args[1], args[2])
            elif command == 'phone':
                return show(args[0])
            elif command == 'show':
                return show(args[0])
            elif command == 'load':
                return self.load(args[0])
            elif command == 'save':
                return self.save(args[0])
            raise CommandError
        
        except UsernameError:
            return errors[2]
        except ValueError:
            return errors[4]
        except IndexError:
            return errors[3]
        except CommandError:
            return errors[1]
        except KeyError:
            return errors[2]
        except DateError:
            return errors[5]
        except FileNotFoundError:
            return errors[6]
        except PhoneExistError:
            return errors[7]

    def save(self, filename=None):
        '''Save address book into file'''
        if filename:
            self.filename = filename
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)
        return 'Done'

    def load(self, filename=None):
        '''Load address book from file'''
        if filename:
            self.filename = filename
        with open(self.filename, 'rb') as file:
            self.data = pickle.load(file)
        return 'Done'

    def parser(self, raw_input: str) -> str|tuple[str]:
        '''Returns (command, name, number, birthday)'''
        raw_input = str(raw_input)
        if raw_input == 'good bye' or\
        raw_input == 'close' or\
        raw_input == 'exit' or\
        raw_input == 'quit':
            print('Good bye!')
            return 'break'

        user_input = raw_input.split(' ')
        if len(user_input) < 2:
            return 'error'
        command = user_input[0]
        name = user_input[1]
        number = None
        birthday = None

        if len(user_input) > 2:
            for inp in user_input[2:]:
                if inp.isnumeric():
                    number = inp
                    continue
                birthday = inp

        return (command, name, number, birthday)

class Record:
    def __init__(self, name, phone=None, birthday=None) -> None:
        self.name = name
        self.birthday = birthday
        self.phone = phone

    def days_to_birthday(self):
        if self.birthday.value:
            now = datetime.now()
            birthday = self.birthday.value
            next_birthday = birthday.replace(year=now.year)
            if next_birthday < now:
                next_birthday = next_birthday.replace(year=next_birthday.year + 1)
            return next_birthday.toordinal() - now.toordinal()
        return '-----'


class Field:
    def __init__(self) -> None:
        self.value = {}

    def __setitem__(self, item, _):
        self.value['value'] = item

    def __getitem__(self, _):
        return self.value['value']


@dataclass
class Name(Field):
    '''Name'''


@dataclass
class Birthday(Field):
    '''Birthday'''


@dataclass
class Phone(Field):
    '''Phone'''


class UsernameError(LookupError):
    '''Username not found!'''
class CommandError(LookupError):
    '''Undefined command'''
class DateError(LookupError):
    '''Unsupported date format'''    
class PhoneExistError(LookupError):
    '''Phone already exist, use 'change' command instead'''


def main() -> None:
    """Main cycle"""
    index = -1
    while True:
        # command = parser(input().lower())

        command = input()

        if command == '':
            index += 1
            test = [
                'add nick 15952124',
                'add nick 1992-1-5',
                'show all',
                'show nick',
                'add nancy 159648 1552-4-5',
                'add nana 5934 2002-4-17',
                'add nency 1594648 1552-4-27',
                'add nata 59314 2002-1-7',
                'add naa 593153434 2021-1-8',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                'show all',
                    ]
            print(test[index])
            command = test[index]
        command = ab.parser(command.lower())
        if command == 'break':
            ab.save()
            break

        result = ab.handler(command[0], command[1:])

        if isinstance(result, AddressBook):
            for sheet in result:
                print(sheet)
                break
        else:
            print(result)


if __name__ == "__main__":
    ab = AddressBook()
    try:
        ab.load()
    except FileNotFoundError:
        print('New address book!')
    main()
