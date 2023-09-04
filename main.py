from PIL import Image, ImageFont, ImageDraw
import PySimpleGUI as sg
import math
import os

SHADE_CONVERSION = {'Light': (255, 255, 255),
                    'Dark': (0, 0, 0)}
image = Image.new('RGBA', (100, 100))


def gui():
    watermark_complete = False
    sg.theme('DarkTeal11')

    layout = [[sg.FileBrowse(enable_events=True, key='image', button_text='Select Image')],
              [sg.Text(size=(50, 1), background_color='gray', text_color='black', key='reflect_image',
                       enable_events=True)],
              [sg.Text('Type Watermark Text: '), sg.InputText(size=(36, 1), key='watermark_text')],
              [sg.HSep()],
              [sg.Text('Select Watermark Opacity (%)'), sg.Slider(range=(0, 100), orientation='h', default_value=50,
                                                                  resolution=5, key='opacity')],
              [sg.Text('Choose Text Shade'), sg.Combo(values=['Light', 'Dark'], key='shade')],
              [sg.HSep()],
              [sg.Button('Cancel', button_color=('white', 'gray')), sg.Push(),
               sg.Button('Run', size=(8, 1), key='run'),
               sg.Button('Show Image', size=(8, 1), key='show'),
               sg.Button('Save Image', size=(8, 1), key='save')]]

    window = sg.Window(title='Watermarking Tool', layout=layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            values = ['', 0]
            break
        if event == 'image':
            file_path = values['image']
            file_name = os.path.basename(file_path)
            window['reflect_image'].update(value=file_name)
        if event == 'run':
            if values['image'] == '':
                sg.popup('Please choose a file')
                continue
            file_path = values['image']
            file_name = os.path.basename(file_path)
            if file_name.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
                sg.popup('Invalid filetype: Please choose a .png or .jpeg instead')
                continue
            if values['watermark_text'] == '':
                sg.popup('Please type what you would like the watermark to say')
                continue
            if values['shade'] == '':
                sg.popup('Please choose whether the watermark has light or dark text')
                continue
            watermark_complete = add_watermark(file=values['image'],
                                               text=values['watermark_text'],
                                               opacity=values['opacity'],
                                               shade=values['shade'])
            if not watermark_complete:
                sg.popup('Watermark string too long, try removing some characters')
                continue
            sg.popup('Watermark Added!')

        if event == 'show':
            if not watermark_complete:
                sg.popup('The watermarked image has not been created yet. Please click "Run"')
                continue
            image.show()
        if event == 'save':
            if not watermark_complete:
                sg.popup('The watermarked image has not been created yet. Please click "Run"')
                continue
            file_path = values['image']
            file_name = os.path.basename(file_path)
            parent_path = os.path.dirname(file_path)
            new_file_name = ''
            while new_file_name == '':
                new_file_name = sg.popup_get_text('Watermarked File Name', title="Save Watermarked Image")
                if any(map(new_file_name.__contains__, ['.', '/', '\\'])):
                    sg.popup('Invalid character(s) used')
                    new_file_name = ''
                    continue
                new_file_name += f".{file_name.split('.')[-1]}"
                if new_file_name in os.listdir():
                    sg.popup('File already exists')
                    new_file_name = ''
                    continue
            image.save(fp=f'{parent_path}/{new_file_name}')
            sg.popup(f'Image saved to:\n\n{parent_path}/{new_file_name}')


def add_watermark(file: str, text: str, opacity: int, shade: str) -> bool:
    global image
    font = ImageFont.truetype('ELEPHNT.TTF', 100, encoding='unic')
    image = Image.open(file)
    angle = math.degrees(math.atan(image.size[1] / image.size[0]))
    diagonal = math.sqrt(image.size[1] ** 2 + image.size[0] ** 2)
    text_temp = Image.new(mode='RGBA', size=image.size, color=(0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_temp)
    x, y, text_width, text_height = text_draw.textbbox(xy=(0, 0), text=text, font=font)
    if text_width > diagonal * 0.8:
        return False
    text_draw.text(xy=((text_temp.size[0] - text_width) / 2, (text_temp.size[1] - text_height) / 2),
                   text=text, font=font, fill=SHADE_CONVERSION[shade])
    text_temp = text_temp.rotate(angle=angle, expand=True, center=(image.size[0] / 2, image.size[1] / 2))
    text_transparent = text_temp.copy()
    text_transparent.putalpha(int(opacity * 255 / 100))
    text_temp.paste(text_transparent, mask=text_temp)
    horizontal_shift = int((image.size[0] - text_temp.size[0]) / 2)
    vertical_shift = int((image.size[1] - text_temp.size[1]) / 2)
    image.paste(text_temp, box=(horizontal_shift, vertical_shift), mask=text_temp)
    return True


if __name__ == '__main__':
    gui()
