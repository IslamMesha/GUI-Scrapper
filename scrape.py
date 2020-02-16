import argparse
import base64
import json
import os

import requests
from bs4 import BeautifulSoup

from guiscrape import _alert


def _fetch_images(soup, base_url):
    images = []
    imgs = soup.findAll('img')
    for img in imgs:
        src = img.get('src')
        img_url = f'{base_url}/{src}'
        name = img_url.split('/')[-1]
        images.append(dict(name=name, url=img_url))
    return images


def _matches_extension(filename, extension_list):
    name, extension = os.path.splitext(filename.lower())
    return extension in extension_list


def _filter_images(images, type_):
    if type_ == 'all':
        return images
    ext_map = {
        'png': ['.png'],
        'jpg': ['.jpg', '.jpeg', ],
    }
    return [
        img for img in images if _matches_extension(img['name'], ext_map[type_])
    ]


def save_images(images):
    for img in images:
        url = img['url']
        name = img['name']
        img_data = requests.get(url=url).content
        with open(name, 'wb') as f:
            f.write(img_data)
    _alert('Done')


def save_json(images):
    data = {}
    for img in images:
        url = img['url']
        name = img['name']
        img_data = requests.get(url=url).content
        b64_img_data = base64.b64encode(img_data)
        str_img_data = b64_img_data.decode('utf-8')
        data[name] = str_img_data
    with open('images.json', 'w') as iJson:
        iJson.write(json.dumps(data))
    _alert('Done')


def _save(images, format_):
    if images:
        if format_ == 'img':
            save_images(images)
        else:
            save_json(images)
    else:
        print('No images to save.')


def scrape(url, format_, type_):
    try:
        page = requests.get(url=url)
    except requests.RequestException as re:
        print(re)
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        images = _fetch_images(soup, url)
        images = _filter_images(images, type_)
        _save(images, format_)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a webpage.')
    parser.add_argument('-t', '--type', choices=['all', 'png', 'jpg'], default='all',
                        help='The image type we want to scrape.')
    parser.add_argument('-f', '--format', choices=['img', 'json'], default='img',
                        help='The format images are _saved to.')
    parser.add_argument('url', help='The URL we want to scrape for images.')
    args = parser.parse_args()
    scrape(args.url, args.format, args.type)
