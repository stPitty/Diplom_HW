from pprint import pprint
import requests, json, os.path
from datetime import datetime
from tqdm import tqdm

with open('/Users/rup/Work/BTC/Rules.txt') as file:
    vk_token = file.readline().strip('\n')
    ya_token = file.readline()
# vk_id = '552934290' #ДЗ
# vk_id = '193603962' #Лера
vk_id = '22889807' #Ншан

class vk_API:

    def __init__(self,token,id):
        self.url = 'https://api.vk.com/method/'
        self.params = {
            'access_token':token,
            'v':'5.131',
            'owner_id':id
        }

    def get_info(self, album='profile'):
        current_params = {
            'album_id':album,
            'extended': 1,
            'photo_sizes': 1
                          }
        current_url = 'photos.get'
        response = requests.get(self.url+current_url,{**self.params,**current_params}).json()['response']['items']
        return response

    def info_filter(self, album='profile'):
        ph_list = self.get_info(album)
        img_list = [{
                    'file_name': f"{ph_info['likes']['count']}.jpg",
                      'size': f'{ph_info["sizes"][-1]["height"]}x{ph_info["sizes"][-1]["width"]}',
                      'scale': (ph_info["sizes"][-1]["height"], ph_info["sizes"][-1]["width"]),
                      'url': ph_info["sizes"][-1]["url"]
                      }
                    for ph_info in ph_list]
        img_list.sort(key=lambda item: sum(item['scale']), reverse=True)
        return img_list

    def get_albums(self):
        current_url = 'photos.getAlbums'
        response = requests.get(self.url + current_url, self.params).json()['response']['items']
        return response

class yaDisk_API:

    def __init__(self,token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }
        self.url = "https://cloud-api.yandex.net/v1/disk/resources/"

    def get_files(self):
        url = self.url+"files"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def _get_upload_link(self,file_name):
        url = self.url+"upload"
        params = {"path":file_name,
                  "overwrite":'true'}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def uploader(self,file,file_name):
        href = self._get_upload_link(file_name).get('href')
        response = requests.put(href,data=file)
        return response

    def make_dir(self,path):
        params = {'path':path}
        response = requests.put(self.url, headers=self.headers, params=params,)
        return response

    def upload_from_list(self, list, dir='my_files',img_qt=5):
        json_log = []
        for img in tqdm(list[:img_qt:],
                        desc='Идет загрузка файлов на ЯДиск',
                        colour='green'):
            yandex_files = [item['path'].strip("disk:/") for item in self.get_files()['items']]
            if f"{dir}/{img['file_name']}" in yandex_files:
                file_name = img['file_name'].strip('.jpg') + '_' + str(datetime.now().date()) + '.jpg'
            else:
                file_name = img['file_name']
            file = requests.get(img['url'])
            self.make_dir(dir)
            self.uploader(file, f'{dir}/{file_name}')
            json_log += [{'file_name': file_name,
                          'size': img['size']
                          }]
        save_json(json_log, f'files/logs/{str(datetime.now().date())}/img_log')
        return json_log


def save_json(content,file_name):
    file_name += '.json'
    try:
        os.makedirs(os.path.dirname(file_name))
    except FileExistsError:
        pass
    with open(file_name, 'w+') as file:
        json.dump(content, file, ensure_ascii=False, indent=2)

vk_one=vk_API(vk_token,vk_id)
ya_one=yaDisk_API(ya_token)

# pprint(vk_one.get_albums())
my_img_list = vk_one.info_filter()
# ya_one.upload_from_list(my_img_list)




