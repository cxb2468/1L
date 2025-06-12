# coding=utf-8
import os
import argparse
import requests, shutil
import PIL.Image as pimg
from lxml import etree


def mk_tmp():
    '''
    创建临时文件夹
    :return:
    '''
    try:
        os.mkdir('temp')
    except:
        shutil.rmtree('temp', True)
        os.mkdir('temp')


def main_process(file_id, pic_index=0):
    mk_tmp()
    while True:
        db_web = f'https://hbba.sacinfo.org.cn/hbba_onlineRead_page/{file_id}/{pic_index}.png'
        r = requests.get(db_web, headers=headers)
        print(f'page:{pic_index},status:{r.status_code}')
        if r.status_code == 404:
            print('complete!')
            break
        else:
            with open('./temp/' + f'{pic_index}.png', 'wb') as f:
                f.write(r.content)
            pic_index += 1


def get_filename(file_id):
    name_web = f'https://hbba.sacinfo.org.cn/stdDetail/{file_id}'
    r = requests.get(name_web, headers=headers)
    html_element = etree.HTML(r.text)
    xpath_filename = '//h4/text()'
    filename = html_element.xpath(xpath_filename)[0].strip('\r\n\t')
    print(filename)
    return filename


if __name__ == '__main__':
    file_id = 'e99f8d17284a5e920923b11911b2f0b1df9ca7e1b6d177b9a7e71ba5390bf573'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46'
    }
    parser = argparse.ArgumentParser(description="Download DB file with file_id on the website")
    parser.add_argument('-f', '--file_id', type=str, help='file_id', required=True)
    parser.add_argument('-p', '--pic_index', type=int, help='pic_index', default=0)
    args = parser.parse_args()
    filename = get_filename(args.file_id)
    main_process(args.file_id, args.pic_index)
    sources = []
    file_list = os.listdir('./temp')
    sources = [pimg.open(f'./temp/{i}.png') for i in range(len(file_list))]
    sources[0].save(f'./{filename}.pdf', 'pdf', save_all=True, append_images=sources[1:])7