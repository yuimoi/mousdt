import qrcode
from PIL import Image
import os
import config


def generate_QR_code(usdt_address):
    usdt_logo = os.path.join(config.BASE_DIR, 'utils', 'tool', 'usdt.png')

    logo = Image.open(usdt_logo).convert('RGBA')
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)

    QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)


    QRcode.add_data(usdt_address)
    QRcode.make()

    QRimg = QRcode.make_image(back_color="white").convert('RGBA')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
          (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos, logo)

    output_dir = os.path.abspath(os.path.join(config.BASE_DIR, '..', 'static', 'QR_code'))
    output_path = os.path.join(output_dir, usdt_address + '.png')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    QRimg.save(output_path)
