
import requests, json, os.path
from pprint import pprint
from datetime import datetime

with open('/Users/rup/Work/BTC/Rules.txt') as file:
    vk_token = file.readline().strip('\n')
    ya_token = file.readline()
# vk_id = '552934290'
vk_id = '193603962'

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


def save_json(content,file_name):
    file_name += '.json'
    try:
        os.makedirs(os.path.dirname(file_name))
    except FileExistsError:
        pass
    with open(file_name, 'w+') as file:
        json.dump(content, file, ensure_ascii=False, indent=2)

def ya_upload_from_vk(vk,ya,ya_dir='my_files',q_image=5,album='profile'):
    upload_list = vk.info_filter(album)
    json_log = []
    for img in upload_list[:q_image:]:
        yandex_files = [item['path'].strip("disk:/") for item in ya.get_files()['items']]
        if f"{ya_dir}/{img['file_name']}" in yandex_files:
            file_name = img['file_name'].strip('.jpg')+'_'+str(datetime.now().date())+'.jpg'
        else:
            file_name = img['file_name']
        file = requests.get(img['url'])
        ya.make_dir(ya_dir)
        ya.uploader(file, f'{ya_dir}/{file_name}')
        json_log += [{'file_name':file_name,
                      'size':img['size']
                      }]
    save_json(json_log,f'files/logs/{str(datetime.now().date())}/img_log')
    return json_log


vk_one=vk_API(vk_token,vk_id)
ya_one=yaDisk_API(ya_token)
# pprint(ya_upload_from_vk(vk_one,ya_one,'new_files'))




