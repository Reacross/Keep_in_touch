from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import print_formatted_text
from collections import UserDict, UserList
from datetime import datetime, date
import pickle
import re

style = Style.from_dict({   # містить інформацію про те, які стилі повинні застосовуватися до різних елементів інтерфейсу
    # стилі для пунктів у меню завершення
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',  # стиль  фона
    'scrollbar.button': 'bg:#222222',
})

COMMANDS = [
    "hello",
    "add record",
    "edit record",
    "delete record",
    "find record",
    "show birthday list",
    "show all records",
    "add note",
    "edit note",
    "delete note",
    "find note",
    "sort notes by title",
    "sort notes by date from old to new",
    "sort notes by date from new to old",
    "show all notes",
    "good bye",
    "close",
    "exit",
    "help"
]


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        self.value = value


class Phone(Field):
    def __init__(self, value):
        while True:
            if value == '':
                self.value = ''
                break
            else:
                number = value.strip()
                number = number.replace(' ', '')
                number = number.replace('+', '')
                number = number.replace('-', '')
                number = number.replace('(', '')
                number = number.replace(')', '')
                try:
                    if number.isnumeric() and len(number) == 10:
                        self.value = number
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print("Invalid phone format. Please inmut 10-digits number")
                    value = input("Try again:>> ")


class Birthday(Field):
    def __init__(self, value=''):
        while True:
            if value == '':
                self.value = ''
                break
            else:
                try:
                    self.value = datetime.strptime(value, '%d-%m-%Y').date()
                    break
                except ValueError:
                    print('Invalid format of data. Please use DD-MM-YYYY format.')
                    value = input("Try again:>> ")


class Email(Field):
    def __init__(self, value):
        while True:
            if value == '':
                self.value = ''
                break
            else:
                check_pattern = re.compile(r'[\w.]+@(\w+\.)+\w{2,}')
                try:
                    if check_pattern.match(value):
                        self.value = value
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print(
                        'Invalid format of data. Please use example@example.org format.')
                    value = input("Try again:>> ")


class Adress(Field):
    def __init__(self, value: str):
        self.value = value


class Record:
    def __init__(self, name, birthday='', address='', address_book=None):
        self.name = self.check_unique_name(name, address_book)
        self.birthday = Birthday(birthday)
        self.address = address
        self.phones = []
        self.email = []

    def check_unique_name(self, name, address_book):
        if address_book:
            existing_record = address_book.find(name)
            if existing_record:
                raise ValueError("This name is already taken")
        return Name(name)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break
        else:
            raise ValueError("Phone not found")

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday.value:
            return None
        today = datetime.now()
        next_birthday = datetime(
            today.year, self.birthday.value.month, self.birthday.value.day)
        if today > next_birthday:
            next_birthday = datetime(
                today.year + 1, self.birthday.value.month, self.birthday.value.day)
        return (next_birthday - today).days

    def add_email(self, email):
        self.email.append(Email(email))

    def find_email(self, email):
        for e in self.email:
            if e.value == email:
                return e
        return None

    def remove_email(self, email):
        self.email = [e for e in self.email if e.value != email]

    def edit_email(self, old_email, new_email):
        for i, email in enumerate(self.email):
            if email.value == old_email:
                self.email[i] = Email(new_email)
                break
        else:
            raise ValueError("Email not found")

    def add_address(self, address):
        self.address = address

    def remove_address(self, address):
        self.address = [p for p in self.address if p.value != address]

    def edit_address(self, old_address, new_address):
        if self.address == old_address:
            self.address = new_address
        else:
            raise ValueError("Address not found")

    def __str__(self):
        phones_str = ', '.join(str(p.value) for p in self.phones)
        emails_str = ', '.join(str(e.value)
                               for e in self.email) if self.email else "None"
        return f"Name: {self.name.value}, Phones: {phones_str}, Birthday: {self.birthday}, Emails: {emails_str}, Address: {self.address}"


class AddressBook(UserDict):
    def __init__(self, filename='book.bin'):
        super().__init__()
        self.filename = filename
        self.load_from_file()

    def add_record(self, value):
        self.data[str(value.name)] = value
        self.save_to_file()

    def find(self, name):
        name = name.title()
        return self.data.get(name)

    def search(self, value=None):  # пошук за за кількома цифрами номера телефону або літерами імені
        if value:
            data_match = str()
            value = value.lower()
            for _, record in self.data.items():
                phon = str([str(i) for i in record.phones])
                if value in str(record.name).lower() or value in phon:
                    data_match += f'{record}\n'
            print(data_match)

    def delete(self, name):
        name = name.title()
        try:
            del self.data[name]
            self.save_to_file()
        except KeyError:
            return None

    def birthdays_in_the_next_days(self, num_day=7):
        for _, record in self.data.items():
            if record.birthday.value:
                days_to = record.days_to_birthday()
                if days_to <= num_day:
                    print(
                        f'{record.name} birthday in {days_to} days, {record.birthday}')

    def save_to_file(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self):
        try:
            with open(self.filename, 'rb') as file:
                data = dict(sorted((pickle.load(file)).items()))
                if data:
                    self.data = data
        except FileNotFoundError:
            pass


class Note(UserDict):
    def __init__(self, title, tags=None, text=None):
        super().__init__()
        self.data["title"] = title
        self.data["tags"] = tags if tags is not None else []
        self.data["text"] = text
        self.data["date"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # добавление тэга. Тэги также можно добавлять по одному к уже существующим
    def add_tag(self, tag):
        if not isinstance(self.data["tags"], list):
            self.data["tags"] = []
        self.data["tags"].append(tag)

    # добавление текста. Позволяет дописывать текст к уже существующему
    def add_text(self, text):
        if self.data["text"] is None:
            self.data["text"] = text
        else:
            self.data["text"] += text

    def __str__(self):
        return f"{self.data['title']}\ntags: {', '.join(t for t in self.data['tags']) if self.data['tags'] else ''}\n\
{self.data['text'] if self.data['text'] else ''}\n{self.data['date']}"


class Notes(UserList):
    def __init__(self, filename='notes.bin'):
        super().__init__()
        self.filename = filename
        self.load_notes_from_file()

    # добавление записи в записную книгу
    def add_note(self, note):
        for existing_note in self:   
            if existing_note.data["title"] == note.data["title"]:
                return f"Note with title {note.data['title']} already exists. Please choose another title."
        self.append(note)
        return f'Note with title {note.data["title"]} has been added successfully.'  
      
    # редактирование заголовка одной записи
    def edit_title(self, old_title, new_title):       
        for note in self:
            if note.data["title"].lower() == new_title.lower():
                return f'Note with title "{new_title}" already exists. Please choose another title.'

        for note in self:
            if note.data["title"] == old_title:
                note.data["title"] = new_title
                return f'Title "{old_title}" has been changed to "{new_title}".'

        return f'Note with title "{old_title}" not found.'

    # удаление записи по заголовку. Без учета различий между строчными и заглавными буквами
    def delete_note_by_title(self, title):
        for note in self:
            if note.data["title"].lower() == title.lower():
                self.remove(note)
                return f'Note with title "{title}" has been deleted.'
        return f'Note with title "{title}" not found.'
    
        # удаление записи по дате. Не знаю, нужен ли этот метод вообще. Можно пока не делать для него команду в функции main
    def delete_note_by_date(self, date):
        for note in self:
            if note.data["date"] == date:
                self.remove(note)
                return f'Note with date "{date}" has been deleted.'
        return f'Note with date "{date}" not found.'

    # поиск записи по заголовку, а именно по частичному совпадению заголовка с поисковым запросом. Без учета различий между строчными и заглавными буквами
    def search_by_title(self, search_query):
    
        for note in self:
            if search_query.lower() in note.get("title", "").lower():
                return note

        return None

    # поиск записи по тэгу, а именно по точному (а не частичному) совпадению тэга с поисковым запросом. Без учета различий между строчными и заглавными буквами
    def search_by_tag(self, search_tags):
        result_list = []
        for note in self:
            for tag in note.data.get("tags", []):
                if tag.lower() in search_tags:
                    result_list.append(note)

        if not result_list:
            return "No notes with a tag that matches the search query"
        return "\n--------------\n\n".join(str(note) for note in result_list)

    # сортировка и вывод записей по дате - от старых к новым. Если записная книжка пустая, то юзеру сообщается "Your notebook is empty"
    def sort_by_date(self):
        if self:
            sorted_by_date = sorted(self, key=lambda note: datetime.strptime(note.data["date"], "%d.%m.%Y %H:%M:%S"))
            return "\n--------------\n\n".join(str(note) for note in sorted_by_date)
        else:
            return "Your notebook is empty"


    # сортировка и вывод записей по дате в обратном порядке - от новых с старым. Если записная книжка пустая, то юзеру сообщается "Your notebook is empty"
    def sort_by_date_reverse(self):
        if self:
            sorted_by_date_reverse = sorted(self, key=lambda note: datetime.strptime(note.data["date"], "%d.%m.%Y %H:%M:%S"), reverse=True)
            return "\n--------------\n\n".join(str(note) for note in sorted_by_date_reverse)
        else:
            return "Your notebook is empty"


    # сортировка и вывод записей по заголовку в алфавитном порядке. Если записная книжка пустая, то юзеру сообщается "Your notebook is empty"
    def sort_by_title(self):
        if self:
            sorted_by_title = sorted(self, key=lambda note: note.data["title"])
            return "\n--------------\n\n".join(str(note) for note in sorted_by_title)
        else:
            return "Your notebook is empty"


    # сохранение в файл
    def save_to_file(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self, file)
            

    # загрузка из файла. В случае, если файл не найден или он пустой, то юзеру будет выведено "Your notebook is empty", т.к. это задано в методе __str__ -------------- Нат добавила в 16:55 18.02.2024
    def load_notes_from_file(self):
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
                if data:
                    self.data = data
        except EOFError:
            pass
        except FileNotFoundError:
            pass


    # вывод всех записей, содержащихся в записной книжке. Если она пустая, то юзеру сообщается "Your notebook is empty"
    def __str__(self):
        return "\n--------------\n\n".join(str(note) for note in self) if self else "Your notebook is empty"


def hello_command():   # Привітання
    print("How can I help you?")


def add_contact(name=None):
    if name is None:
        name = input("Enter the name: ")
    if book.find(name):
        print("Contact with this name already exists.")
        return
    contact = Record(name)
    contact.add_phone(input("Enter the phone: "))
    contact.add_birthday(
        input("Enter the birthday in format dd-mm-yyyy:  "))
    contact.add_email(input("Enter the email: "))
    contact.add_address(input("Enter the address: "))
    book.add_record(contact)
    print(f"Contact {contact.name} is saved")


def edit_record():
    name = input("Enter the name of the record you want to edit: ")
    record = book.find(name)
    if record:
        print("Record found:")
        print(record)

        while True:
            print("Select the field you want to edit:")
            print("1. Name")
            print("2. Phones")
            print("3. Birthday")
            print("4. Emails")
            print("5. Address")
            print("0. Done editing")

            choice = input("Enter your choice: ")

            if choice == "1":
                new_name = input("Enter the new name: ")
                record.name = Name(new_name)
            elif choice == "2":
                old_phone = input(
                    "Enter the phone number you want to edit (leave blank to add a new one): ")
                if not old_phone:
                    new_phone = input("Enter the new phone number: ")
                    record.add_phone(new_phone)
                else:
                    new_phone = input("Enter the new phone number: ")
                    try:
                        record.edit_phone(old_phone, new_phone)
                    except ValueError as e:
                        print(e)
            elif choice == "3":
                new_birthday = input(
                    "Enter the new birthday in format dd-mm-yyyy: ")
                record.birthday = Birthday(new_birthday)
            elif choice == "4":
                old_email = input(
                    "Enter the email you want to edit (leave blank to add a new one): ")
                if not old_email:
                    new_email = input("Enter the new email: ")
                    record.add_email(new_email)
                else:
                    new_email = input("Enter the new email: ")
                    try:
                        record.edit_email(old_email, new_email)
                    except ValueError as e:
                        print(e)
            elif choice == "5":
                new_address = input("Enter the new address: ")
                record.edit_address(record.address, new_address)
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")

        print("Record edited successfully:")
        print(record)
        book.save_to_file()  # Сохраняем изменения
    else:
        print("Record not found.")


def delete_record():
    name = input("Enter the name of the record to delete: ")
    if book.find(name):
        book.delete(name)
        print(f"Record '{name}' deleted successfully!")
    else:
        print(f"Record '{name}' not found.")


def find_record():
    value = input("Enter search query: ")
    book.search(value)


def bithday_list():    # Пошук іменинників
    days = int(input("Enter number of days: "))
    book.birthdays_in_the_next_days(days)


def show_all_records():
    for _, record in book.data.items():
        print(record)
        print('-'*100)


def add_note(title=None):   # Додавання нотатки
    note_title = title if title else input("Enter note title: ")
    note_tags = input("Enter note tags (separated by comma): ").split(", ")
    note_text = input("Enter note text: ")

    note = Note(title=note_title)
    for tag in note_tags:
        note.add_tag(tag)
    note.add_text(note_text)

    my_notes.add_note(note)
    print(f"Note '{note_title}' is saved")


# Редагування нотатки
def edit_note():
    title = input("Enter the title of the note you want to edit: ")
    found_note = my_notes.search_by_title(title)

    if found_note is None:
        print("Note not found.")
        return

    print("Note found:")
    print(found_note)

    while True:
        print("Select the field you want to edit:")
        print("1. Title")
        print("2. Tags")
        print("3. Text")
        print("0. Done editing")

        choice = input("Enter your choice: ")

        if choice == "1":
            new_title = input("Enter the new title: ")
            found_note.data["title"] = new_title
        elif choice == "2":
            new_tags = input(
                "Enter the new tags separated by commas: ").split(",")
            found_note.data["tags"] = [tag.strip() for tag in new_tags]
        elif choice == "3":
            new_text = input("Enter the new text: ")
            found_note.data["text"] = new_text
        elif choice == "0":
            print("Done editing.")
            break
        else:
            print("Invalid choice. Please try again.")

    my_notes.save_to_file()  # Сохраняем изменения


def delete_note(name=None):   # Видалення нотатки
    title_to_delete = input("Enter the title of the note to delete: ")
    print(my_notes.delete_note_by_title(title_to_delete))


def find_note(name=None):   # Пошук нотатки за ключовими словами
    unique_tags = set(tag for note in my_notes for tag in note.data.get("tags", []))
    completer = WordCompleter(list(unique_tags), ignore_case=True)
    tag_to_find = prompt("Enter the tag to search for: ", completer=completer)
    print(my_notes.search_by_tag(tag_to_find))


def sort_notes_title(name=None):   # Сортування нотаток за заголовком
    print(my_notes.sort_by_title())


def sort_notes_date(name=None):   # Сортування нотаток за датою (від старих до нових)
    print(my_notes.sort_by_date())


# Сортування нотаток за датою (від нових до старих)
def sort_notes_date_reverse(name=None):
    print(my_notes.sort_by_date_reverse())


def show_all_notes(name=None):   # Показати всі нотатки
    print(my_notes)

def helper():
    print('''hello - starting work with helper bot
        add record - adding a new record to Address Book
        edit record - editing existing record in Address Book
        delete record - deleting existing record by name
        find record - searching existing record in Address Book
        show birthday list - show list of contacts who have birthdays for some range of days (7 by default)
        show all records - represents all records from Address Book
        add note - adding a new note to Notes
        edit note - editing existing note in Notes
        delete note - deleting existing note by title
        find note - searching note by tags
        sort notes by title - sorting notes by title in alphabet orders
        sort notes by date from old to new - sorting notes by date of creations (oldest first)
        sort notes by date from new to old - sorting notes by date of creations (newest first)
        show all notes - represents all notes from Notes
        good bye - shutting down helper bot
        close - shutting down helper bot
        exit - shutting down helper bot
        help - represents list of approachable commands
        ''')


COMMANDS_fanc = {
    "hello": hello_command,
    "add record": add_contact,
    "edit record": edit_record,
    "delete record": delete_record,
    "find record": find_record,
    "show birthday list": bithday_list,
    "show all records": show_all_records,
    "add note": add_note,
    "edit note": edit_note,
    "delete note": delete_note,
    "find note": find_note,
    "sort notes by title": sort_notes_title,
    "sort notes by date from old to new": sort_notes_date,
    "sort notes by date from new to old": sort_notes_date_reverse,
    "show all notes": show_all_notes,
    "help": helper
}


def main():

    # об'єкт для автодоповнення введення команд у консолі, ignore_case - ігнорує регістр
    completer = WordCompleter(COMMANDS, ignore_case=True)
    while True:
        try:
            user_input = prompt(
                "Enter command: ", completer=completer, style=style)  # input('>>> ')

            if user_input in ["good bye", "close", "exit"]:
                my_notes.save_to_file()
                book.save_to_file()
                print("Good bye!")
                break
            elif user_input.lower() in COMMANDS:
                command = COMMANDS_fanc[user_input]
                command()
            else:
                print("Invalid command. Try again.")
        except Exception as e:
            print(f"Error: {e}")

book = AddressBook()
my_notes = Notes()
if __name__ == "__main__":

    main()

