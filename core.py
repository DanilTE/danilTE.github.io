from datetime import date
import vk_api
from config import access_token


class ApiInterface:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):
        def calculate_age(bdate: str):
            try:
                day, month, year = map(int, bdate.split('.'))
            except ValueError:
                return None
            today = date.today()
            return today.year - year - ((today.month, today.day) < (month, day))

        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex'
                                 }
                                )
        print(info['bdate'])
        user_info = {'name': f'{info["first_name"]} {info["last_name"]}',
                     'id': info['id'],
                     'age': calculate_age(info['bdate']) if 'bdate' in info else None,
                     'sex': info['sex'],
                     'city': info['city']['id'] if 'city' in info else None
                     }
        return user_info

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )
        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        return res

    def search_users(self, params, offset=0):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        age = params['age']
        age_from = age - 5
        age_to = age + 5
        users = self.api.method('users.search',
                                {'count': 50,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                 }
                                )
        try:
            users = users['items']
        except KeyError:
            return []
        res = []
        for user in users:
            if not user['is_closed']:
                res.append({'id': user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                            }
                           )
        return res

    def get_cites(self, q,country_id=1):
        cites = self.api.method('database.getCities',
                                {
                                    'country_id': country_id,
                                    'q': q,
                                    'need_all': 1
                                })
        print(cites)
        return cites['items'] if 'items' in cites and cites['count'] > 0 else []

    def get_cites_by_id(self, id):
        city, = self.api.method('database.getCitiesById',
                               {
                                   'city_ids': id
                               })
        return city


if __name__ == '__main__':
    api = ApiInterface(access_token)
    print(api.get_profile_info(544004447))
