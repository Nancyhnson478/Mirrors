from PIL import Image, ImageFont, ImageDraw
from telethon import events
from .. import jdbot, chat_id, _LogDir, _JdbotDir,logger
from prettytable import PrettyTable
import subprocess

IN = _LogDir + '/bean_income.csv'
OUT = _LogDir + '/bean_outlay.csv'
TOTAL = _LogDir + '/bean_total.csv'
_botimg = _LogDir + '/bean.jpg'
_font = _JdbotDir + '/font/jet.ttf'


@jdbot.on(events.NewMessage(chats=chat_id, pattern=r'^/bean'))
async def mybean(event):
    try:
        await jdbot.send_message(chat_id, '正在查询，请稍后')
        subprocess.check_output(
            'jcsv', shell=True, stderr=subprocess.STDOUT)
        if len(event.raw_text.split(' ')) > 1:
            text = event.raw_text.replace('/bean ', '')
        else:
            text = None
        if text and text == 'in':
            creat_bean_counts(IN)
            await jdbot.send_message(chat_id, '您的近日收入情况', file=_botimg)
        elif text and text == 'out':
            creat_bean_counts(OUT)
            await jdbot.send_message(chat_id, '您的近日支出情况', file=_botimg)
        elif text and int(text):
            creat_bean_count(text)
            await jdbot.send_message(chat_id, f'您的账号{text}收支情况', file=_botimg)
        else:
            creat_bean_counts(TOTAL)
            await jdbot.send_message(chat_id, '您的总京豆情况', file=_botimg)
    except Exception as e:
        await jdbot.send_message(chat_id, 'something wrong,I\'m sorry\n'+str(e))
        logger.error('something wrong,I\'m sorry'+str(e))

def creat_bean_count(count):
    files = {"BEANIN": IN, "BEANOUT": OUT, "TOTAL": TOTAL}
    tb = PrettyTable()
    columns = []
    with open(files["BEANIN"], 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = lines[-7:]
    for line in lines:
        columns.append(line.split(',')[0])
    tb.add_column('DATE', columns)
    for key, file in files.items():
        columns = []
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        lines = lines[-7:]
        for line in lines:
            columns.append(line.split(',')[int(count)])
        tb.add_column(key, columns)
    length = 172 + 100 * 3
    im = Image.new("RGB", (length, 280), (244, 244, 244))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(_font, 18)
    dr.text((10, 5), str(tb), font=font, fill="#000000")
    im.save(_botimg)


def creat_bean_counts(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        data = f.readlines()
    tb = PrettyTable()
    num = len(data[-1].split(',')) - 1
    title = ['DATE']
    for i in range(0, num):
        title.append('COUNT'+str(i+1))
    tb.field_names = title
    data = data[-7:]
    for line in data:
        row = line.split(',')
        if len(row) > len(title):
            row = row[:len(title)]
        elif len(row) < len(title):
            i = len(title) - len(row)
            for _ in range(0,i):
                row.append(0)
        tb.add_row(row)
    length = 172 + 100 * num
    im = Image.new("RGB", (length, 360), (244, 244, 244))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(_font, 18)
    dr.text((10, 5), str(tb), font=font, fill="#000000")
    im.save(_botimg)
