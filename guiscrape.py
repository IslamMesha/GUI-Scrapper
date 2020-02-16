import base64
import json
from tkinter import ttk, filedialog, messagebox, StringVar, Listbox, N, S, E, W, VERTICAL, Tk

import requests
from bs4 import BeautifulSoup

config = {}


def _sb(msg):
    _status_msg.set(msg)


def _alert(msg):
    messagebox.showinfo(message=msg)


def fetch_images(soup, base_url):
    images = []
    for img in soup.findAll('img'):
        src = img.get('src')
        img_url = f'{base_url}/{src}'
        name = img_url.split('/')[-1]
        images.append(dict(name=name, url=img_url))
    return images


def fetch_url():
    images = []
    url = _url.get()
    config['images'] = []
    _images.set(())  # initialised as an empty tuple
    try:
        page = requests.get(url)
    except requests.RequestException as err:
        _sb(str(err))
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        images = fetch_images(soup, url)
        if images:
            _images.set(tuple(img['name'] for img in images))
            _sb('Images found: {}'.format(len(images)))
        else:
            _sb('No images found')
    config['images'] = images


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


def _save_images(dirname):
    images = config.get('images')
    if dirname and images:
        save_images(images)


def _save_json(filename):
    images = config.get('images')
    if filename and images:
        save_json(images)


def save():
    if not config.get('images'):
        _alert('No images to save')
        return
    if _save_method.get() == 'img':
        dirname = filedialog.askdirectory(mustexist=True)
        _save_images(dirname)
    else:
        filename = filedialog.asksaveasfile(initialfile='images.json', filetypes=[('JSON', '.json')])
        _save_json(filename)


if __name__ == '__main__':
    _root = Tk()
    _root.title('Scrape app')
    _main_frame = ttk.Frame(_root, padding='5 5 5 5')
    _main_frame.grid(row=0, column=0, sticky=(E, W, N, S))

    # URL Frame
    _url_frame = ttk.LabelFrame(_main_frame, text='URL', padding='5 5 5 5')
    _url_frame.grid(row=0, column=0, sticky=(E, W))
    _url_frame.columnconfigure(0, weight=1)
    _url_frame.rowconfigure(0, weight=1)
    _url = StringVar()
    _url.set('http://localhost:8000')
    _url_entry = ttk.Entry(_url_frame, width=40, textvariable=_url)
    _url_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)
    _fetch_btn = ttk.Button(_url_frame, text='Fetch info', command=fetch_url)
    _fetch_btn.grid(row=0, column=1, sticky=W, padx=5)

    # Images Frame
    # The first section (Listbox section)
    _img_frame = ttk.LabelFrame(_main_frame, text='Content', padding='9 0 0 0')
    _img_frame.grid(row=1, column=0, sticky=(N, S, E, W))
    _images = StringVar()
    _imgs_listbox = Listbox(_img_frame, listvariable=_images, height=6, width=25)
    _imgs_listbox.grid(row=0, column=0, sticky=(E, W), pady=5)
    _scrollbar = ttk.Scrollbar(_img_frame, orient=VERTICAL, command=_imgs_listbox.yview)
    _scrollbar.grid(row=0, column=1, sticky=(S, N), pady=6)
    _imgs_listbox.configure(yscrollcommand=_scrollbar.set)

    # The second section (Radio buttons section)
    _radio_frame = ttk.Frame(_img_frame)
    _radio_frame.grid(row=0, column=2, sticky=(N, S, W, E))
    _choice_lbl = ttk.Label(_radio_frame, text='Choose how to save images')
    _choice_lbl.grid(row=0, column=0, padx=5, pady=5)

    _save_method = StringVar()
    _save_method.set('img')
    _img_only_radio = ttk.Radiobutton(_radio_frame, text='As images', variable=_save_method, value='img')
    _img_only_radio.grid(row=1, column=0, padx=5, pady=2, sticky=W)
    _img_only_radio.configure(state='normal')
    _json_radio = ttk.Radiobutton(_radio_frame, text='As JSON', variable=_save_method, value='json')
    _json_radio.grid(row=2, column=0, padx=5, pady=2, sticky=W)

    # The third section (Scrape button)
    _scrape_button = ttk.Button(_main_frame, text='Scrape!', command=save)
    _scrape_button.grid(row=2, column=0, sticky=E, pady=5)

    # The forth section (Status button)
    _status_frame = ttk.Frame(_root, relief='sunken', padding='2 2 2 2')
    _status_frame.grid(row=1, column=0, sticky=(E, W, S))
    _status_msg = StringVar()
    _status_msg.set('Type a URL to start scraping...')
    _status = ttk.Label(_status_frame, textvariable=_status_msg, anchor=W)
    _status.grid(row=0, column=0, sticky=(E, W))
    _root.mainloop()
