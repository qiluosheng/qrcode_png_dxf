import qrcode
from dxfwrite import DXFEngine as dxf
import os
import qrcode.image.svg
import cv2 as cv


def make_dir():
    if not os.path.exists('svg'):
        os.mkdir('svg')
    if not os.path.exists('png'):
        os.mkdir('png')
    if not os.path.exists('dxf'):
        os.mkdir('dxf')


def make_qr(name):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=0,
    )

    qr.add_data(name)
    qr.make(fit=True)

    ## SVG 格式
    # svg_path = os.path.join(cur_dir, 'svg', f'{name}.svg')
    # factory = qrcode.image.svg.SvgPathImage
    # svg = qrcode.make('Some data here', image_factory=factory)
    # svg.save(svg_path)

    ## PNG 格式
    png_path = os.path.join(cur_dir, 'png', f'{name}.png')
    print(f'正在生成{png_path}')
    png = qr.make_image()
    png.save(png_path)


def out_dxf(png_path):
    # 用opencv 读取png颜色
    _img = cv.imread(png_path)
    gray = cv.cvtColor(_img, cv.COLOR_RGB2GRAY)
    box_hex = []
    for row in range(25):
        box_col_hex = []
        for col in range(25):
            px = gray[row * 20 + 12, col * 20 + 12]
            if px > 200:
                box_col_hex.append(0)
            else:
                box_col_hex.append(1)
        box_hex.append(box_col_hex)

    # print(box_hex)

    # 父目录的父目录
    dxf_dir = os.path.dirname(os.path.dirname(png_path))
    name = os.path.basename(png_path)[:-4]
    dxf_path = os.path.join(dxf_dir, 'dxf', f'{name}.dxf')

    print(f'正在生成{dxf_path}')
    drawing = dxf.drawing(dxf_path)

    ## box_size = 7.5/25 二维码总宽度/格子数
    box_size = 0.3
    for i, box_row in enumerate(box_hex):
        for j, box_col in enumerate(box_row):
            if box_col > 0:
                solid = dxf.solid([(box_size * i, box_size * (25 - j)), (box_size * (i + 1), box_size * (25 - j)),
                                   (box_size * (i + 1), box_size * (26 - j)), (box_size * i, box_size * (26 - j))],
                                  color=7)
                solid['layer'] = 'solids'
                solid['color'] = 7
                drawing.add(solid)
    drawing.save()


def fileListFunc(filePathList):
    # 获取 png list
    fileList = []
    for item in os.listdir(filePathList):
        if item.count('png'):
            fileList.append(os.path.join(filePathList, item))
    return fileList


if __name__ == '__main__':
    make_dir()
    cur_dir = os.path.dirname(os.path.realpath(__file__))

    white_start = int(input(f"白色起始编号"))
    white_stop = int(input(f"白色结束编号")) + 1
    blue_start = int(input(f"蓝色起始编号"))
    blue_stop = int(input(f"蓝色起始编号")) + 1

    # 生成图片
    for name in range(white_start, white_stop):
        name_len = len(str(name))
        top_name = 'H01184000000'
        name = top_name[:-name_len] + str(name)
        make_qr(name)
    for name in range(blue_start, blue_stop):
        name_len = len(str(name))
        top_name = 'HB1184000000'
        name = top_name[:-name_len] + str(name)
        make_qr(name)

    # 图片矢量化
    work_dir = os.path.join(cur_dir, 'png')
    fileList = fileListFunc(work_dir)
    for file in fileList:
        out_dxf(file)
