import os
import time
from os import listdir
from os.path import isfile, join
import requests
import json
import pandas as pd
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt

from crawl_bourse24 import convert_arabic_to_persian, is_exist_tag

url = "https://www.eboo.ir/api/ocr/getway"
global_token = ""# eboo token
dir_path = "C:/Users/ASUS/PycharmProjects/Maral_Project/images"  # input()


def save_file(filename):
    os.makedirs(join(dir_path, "savefile"), exist_ok=True)

    if isfile(join(dir_path, "savefile", f"{filename}.json")):
        print("SKIP saving file")
        with open(join(dir_path, "savefile", f"{filename}.json"), 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    else:
        upload = {'filehandle': (f"{dir_path}/{filename}", open(join(dir_path, filename), 'rb'), 'multipart/form-data')}
        payload = {
            "token": global_token,
            "command": "addfile",
        }

        response = requests.post(url, data=payload, files=upload)
        data = response.text
        json_data = json.loads(data)

        with open(join(dir_path, "savefile", f"{filename}.json"), 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4)

    print(json.dumps(json_data, indent=4))


def convert(filename, method=4, output=""):
    os.makedirs(join(dir_path, "convert"), exist_ok=True)
    if isfile(join(dir_path, "convert", f'{filename}_{method}{output}.json')):
        print("SKIP converting file")
        with open(join(dir_path, "convert", f'{filename}_{method}{output}.json'), 'r', encoding='utf-8') as file:
            json_data = json.load(file)

    else:
        with open(join(dir_path, "savefile", f"{filename}.json"), 'r', encoding='utf-8') as file:
            file_token = json.load(file)['FileToken']

        payload = {
            "token": global_token,
            "command": "convert",
            "filetoken": file_token,
            "method": method,
            "output": output
        }

        response = requests.post(url, data=payload)
        data = response.text
        json_data = json.loads(data)

        with open(join(dir_path, "convert", f'{filename}_{method}{output}.json'), 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=4)

    # show_json
    print(json.dumps(json_data, indent=4))


def download_file(filename, method, output=""):
    with open(join(dir_path, "convert", f'{filename}_{method}{output}.json'), 'r', encoding='utf-8') as file:
        file_url = json.load(file)['FileToDownload']
        file_url_suffix = file_url.split(".")[-1]
    os.makedirs(join(dir_path, "words"), exist_ok=True)
    if output == "":
        downloaded_file_path = f'{filename}_{method}_Doc.{file_url_suffix}'
    elif output == "txt":
        downloaded_file_path = f'{filename}_{method}_txt.{file_url_suffix}'
    elif output == "txtraw":
        downloaded_file_path = f'{filename}_{method}_txtraw.{file_url_suffix}'
    elif output == "txtrawjson":
        downloaded_file_path = f'{filename}_{method}_txtrawjson.{file_url_suffix}'
    else:
        raise ValueError
    if isfile(join(dir_path, "words", downloaded_file_path)):
        print("SKIP downloading file")
    else:
        response = requests.get(file_url)

        if response.status_code == 200:
            with open(join(dir_path, "words", downloaded_file_path), 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully and saved")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    if output == "txt":
        with open(join(dir_path, "words", downloaded_file_path), 'r', encoding='utf-8') as file:
            content = file.read()
        return content


# onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
# if '.DS_Store' in onlyfiles:
#     onlyfiles.remove('.DS_Store')
#
# for f in reversed(onlyfiles):
#     # check the file has the .pdf extension
#     if f.endswith('.jpg'):
#         # Step 1: Reads the pdf file
#         print('Parsing file: {}'.format(f))
#         pdf_file = '{}/{}'.format(dir_path, f)
#
#         save_file(f)
#         convert(f, method=4, output='txt')
#         download_file(f, method=4, output='txt')
#         break


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save(f"images/{url.split('/')[-1]}")
            return image
        else:
            return None
    except:
        return None


def is_mostly_white(image, threshold=0.7):
    image_array = np.array(image)
    white_pixels = np.all(image_array >= 240, axis=-1)  # Considering pixels with RGB values >= 240 as white
    white_pixel_count = np.sum(white_pixels)
    total_pixels = image_array.shape[0] * image_array.shape[1]
    white_percentage = white_pixel_count / total_pixels
    return white_percentage >= threshold


def display_image_with_label(image, label):
    plt.imshow(image)
    plt.axis('off')  # Hide axes
    plt.title(label)
    plt.show()


with open('data\stock_names.json', 'r', encoding='utf-8') as json_file:
    stock_names = json.load(json_file)

for group in reversed(list(stock_names.keys())):
    for key in reversed(stock_names[group]):
        key = convert_arabic_to_persian(key)
        if is_exist_tag(key):
            if isfile(f"images/data/image_text{key}.json"):
                is_white = pd.read_json(f"images/data/image_text{key}.json")
            else:
                is_white = pd.DataFrame(columns=['img', 'is_white', 'text'])

            if isfile(f"ndata/all_news_{key}.json"):
                with open(f"ndata/all_news_{key}.json", 'r', encoding='utf-8') as json_file:
                    all_news = json.load(json_file)
            else:
                print('reached end')
                exit(0)
            print(key, len(all_news))
            for news in all_news:
                link = news['img']
                if link is not None and int(news['persian_date'][:4]) == 1403:
                    if link not in is_white['img'].values:
                        img = None
                        for i in range(5):
                            img = download_image(link)
                            if img is not None:
                                break
                            time.sleep(0.3)
                        if img is not None:
                            label = is_mostly_white(img)
                            urladdr = link.split("/")[-1]
                            if label:
                                save_file(f"{urladdr}")
                                for i in range(5):
                                    try:
                                        convert(f"{urladdr}", 4, 'txt')
                                        break
                                    except:
                                        time.sleep(0.3)
                                        if i == 4:
                                            raise ValueError
                                text = download_file(f"{urladdr}", 4, 'txt')
                                print(text)
                            else:
                                text = ""
                            os.remove(f"images/{urladdr}")
                            is_white = is_white.append({"img": link, "is_white": label, "text": text},
                                                       ignore_index=True)
                            is_white.to_json(f"images/data/image_text{key}.json", orient="records", force_ascii=False)
                        else:
                            is_white = is_white.append({"img": link, "is_white": None, "text": None}, ignore_index=True)
                            is_white.to_json(f"images/data/image_text{key}.json", orient="records", force_ascii=False)
