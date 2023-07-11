from typing import Dict, Union, List

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id
from core import ApiInterface
from config import community_token, access_token, db_url_object
import ast
from db import ViewedTableInterface


class BotStates:
    AGE = 0
    CITY = 1


class BotInterface:
    def __init__(self, comunity_token, access_token, db_url_object):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = ApiInterface(access_token=access_token)
        self.db = ViewedTableInterface(db_url_object=db_url_object)
        self.users: Dict[int: Dict] = {}
        self.states: Dict[int: BotStates] = {}
        self.worksheet: Dict[int: Dict[str: Union[int, List[Dict[str: Union[int, str]]]]]] = {}

    def message_send(self, user_id, message, keyboard=None, attachment=None):
        post = {'user_id': user_id,
                'message': message,
                'attachment': attachment,
                'random_id': get_random_id()
                }
        if keyboard and type(keyboard) == VkKeyboard:
            post['keyboard'] = keyboard.get_keyboard()
        elif type(keyboard) == str:
            post['keyboard'] = keyboard
        self.interface.method('messages.send', post)

    def event_handler(self):

        def get_menu_keyboard():
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Начать поиск', payload={'cmd': 'search'})
            keyboard.add_button('Мой профиль', payload={'cmd': 'profile'})
            return keyboard

        def get_search_keyboard():
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Далее', payload={'cmd': 'search'})
            keyboard.add_button('Назад', payload={'cmd': 'menu'})
            return keyboard

        def validate_age(age: str) -> bool:
            try:
                age = int(age)
                if 0 < age < 100:
                    return True
                else:
                    return False
            except:
                return False

        def user_has_age(user: Dict) -> bool:
            if user['age']:
                return True
            else:
                return False

        def user_get_age(user_id, command):
            if validate_age(command):
                age = int(command)
                self.message_send(user_id, f'Вы указали возраст: {age}.')
                self.users[user_id]['age'] = age
                user = self.users[user_id]
                if not validate_user_data(user):
                    self.states[user_id] = get_state(user)
                else:
                    self.states[user_id] = None
                    keyboard = get_menu_keyboard()
                    self.message_send(user_id, 'Всё готово к работе!', keyboard=keyboard)
            else:
                self.message_send(user_id, 'Вы указали недопустимое значение возраста.\nВведите ваш возраст:')

        def user_has_city(user: Dict):
            if user['city']:
                return True
            else:
                return False

        def user_get_city(user_id, command):
            try:
                id = int(command)
                city = self.api.get_cites_by_id(id)
                if city['title'] != '':
                    self.users[user_id]['city'] = id
                    self.message_send(user_id, f'Для поиска установлен город: {city["title"]}')
                    user = self.users[user_id]
                    if not validate_user_data(user):
                        self.states[user_id] = get_state(user)
                    else:
                        self.states[user_id] = None
                        keyboard = get_menu_keyboard()
                        self.message_send(user_id, 'Всё готово к работе!', keyboard=keyboard)
                else:
                    self.message_send(user_id,
                                      'Вы указали неверный id. Проверьте правильность написания id и отправьте его в новом сообщении.')
            except:
                if len(command) < 16:
                    cites = self.api.get_cites(command)
                    if len(cites) > 0:
                        messange = ''
                        for city in cites:
                            messange += f'id: {city["id"]}\nНазвание: {city["title"]}\n{str("Регион: ", city["region"]) if "region" in city else ""}\n\n'
                        self.message_send(user_id,
                                          'Найдите свой город в списке и отправьте его id в следующем сообщении, либо выполните поиск повторно, написав название города.')
                        self.message_send(user_id, messange)
                    else:
                        self.message_send(user_id,
                                          'Такого города не было найдено, попробуйте выполнить поиск повторно.')
                else:
                    self.message_send(user_id,
                                      'Название города должно содержать не более 15 символов! Произведите поиск повторно.')

        def validate_user_data(user: Dict):
            if user_has_age(user) and user_has_city(user):
                return True
            return False

        def get_state(user):
            keyboard = VkKeyboard().get_empty_keyboard()
            if not user_has_age(user):
                self.message_send(user_id, 'Введите ваш возраст:', keyboard=keyboard)
                return BotStates.AGE
            elif not user_has_city(user):
                self.message_send(user_id, 'Введите id вашего города или его название для поиска id:',
                                  keyboard=keyboard)
                return BotStates.CITY
            else:
                return None

        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                user_id = event.user_id
                payload = ast.literal_eval(event.payload) if hasattr(event, 'payload') else {}
                payload_cmd = payload['cmd'] if 'cmd' in payload else None
                start_commands = ('привет', 'меню', 'menu', 'старт', 'start')
                if user_id not in self.users and command not in start_commands:  # проверка на 'регистрацию' пользователя в боте
                    self.message_send(user_id, 'Для начала работы с ботом напишите: меню')
                    continue
                if (self.states[user_id] if user_id in self.states else None) == BotStates.AGE:  # обработка стадии ввода возраста
                    user_get_age(user_id, command)
                    continue
                elif (self.states[user_id] if user_id in self.states else None) == BotStates.CITY:  # обработка стадии ввода города
                    user_get_city(user_id, command)
                    continue
                if command in start_commands or payload_cmd == 'menu':  # обработка меню
                    keyboard = get_menu_keyboard()
                    self.message_send(user_id, 'Приветствую тебя в боте VKinder!', keyboard=keyboard)
                    if user_id in self.users:
                        user = self.users[user_id]
                    else:
                        user = self.api.get_profile_info(user_id)
                        self.users[user_id] = user
                        viewed_profiles = self.db.get_all_viewed_from_profile_id(user_id)
                        self.worksheet[user_id] = {'offset': 0, 'data': [], 'viewed_profiles': viewed_profiles}
                        self.states[user_id] = None
                    if not validate_user_data(user):
                        self.states[user_id] = get_state(user)
                elif command == 'начать поиск' or payload_cmd == 'search':  # обработка команды поиска
                    keyboard = get_search_keyboard()
                    while len(self.worksheet[user_id]['data']) == 0:
                        viewed = self.worksheet[user_id]['viewed_profiles']
                        data = self.api.search_users(user, offset=self.worksheet[user_id]['offset'])
                        data_cheked = []
                        for f_user in data:
                            if not f_user['id'] in viewed:
                                data_cheked.append(f_user)
                        self.worksheet[user_id]['data'] = data_cheked
                        self.worksheet[user_id]['offset'] += 50
                    finded_user = self.worksheet[user_id]['data'].pop()
                    photos_user = self.api.get_photos(finded_user['id'])
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                        if num == 2:
                            break
                    self.message_send(user_id, f'@id{finded_user["id"]} ({finded_user["name"]})', keyboard=keyboard,
                                      attachment=attachment)
                    self.db.add_record(user_id, finded_user['id'])
                    self.worksheet[user_id]['viewed_profiles'].append(finded_user['id'])
                elif command == 'мой профиль' or payload_cmd == 'profile':
                    user = self.users[user_id]
                    self.message_send(user_id, f'''Ваш профиль:
                    Имя: {user["name"]}
                    Возраст: {user["age"]}
                    Город: {self.api.get_cites_by_id(user["city"])["title"]}
                    Пол: {"Муж" if user['sex'] == 2 else "Жен"}
                    ''', keyboard=get_menu_keyboard())
                else:
                    self.message_send(user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot = BotInterface(comunity_token=community_token, access_token=access_token, db_url_object=db_url_object)
    bot.event_handler()
