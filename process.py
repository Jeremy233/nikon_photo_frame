from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
import exifread
import os

# for better display nikon mirrorless camera model
def better_nikon_model(camera_model):
    if camera_model[:5] == "NIKON": 
        modified_model = camera_model[6:].replace("_", "").replace(" ", "")
        return camera_model[:5] + " " + modified_model
    else: 
        return camera_model

# image data: camera model | focal length | exposure time | aperture | ISO | lens model
def get_info(tags):
    image_camera = str(tags['Image Model'])
    image_camera = better_nikon_model(image_camera)
    image_focal_length = str(tags['EXIF FocalLength']) + "mm"
    image_exposure_time = str(tags['EXIF ExposureTime']) + "s"
    value = tags['EXIF FNumber'].values
    numerator, denominator = value[0].num, value[0].den
    if (numerator % denominator == 0):
        image_aperture = "f" + str(numerator // denominator)
    else:
        image_aperture = "f" + str(numerator / denominator)
    image_iso = "ISO" + str(tags['EXIF ISOSpeedRatings'])
    image_lens = str(tags['EXIF LensModel'])
    info = f"{image_camera} | {image_focal_length} | {image_exposure_time} | {image_aperture} | {image_iso} | {image_lens}"
    return info

def add_padding(input_image_path, output_image_path, text, font_size, compress, padding=800, format='JPEG'):
    # read image and resize
    original_img = Image.open(input_image_path)
    original_width, original_height = original_img.size
    # check if xpan
    if original_width < 2 * original_height:
        scaled_width = int(8256 / original_height * original_width)
        scaled_height = 8256
        scaled_image = original_img.resize((scaled_width, scaled_height), Image.LANCZOS)
        
    else:
        scaled_width = 14677
        scaled_height = 5419
        scaled_image = original_img.resize((scaled_width, scaled_height), Image.LANCZOS)

    # add bg
    new_height = 8256 + 2 * padding
    new_width = int(float(new_height / 9 * 16))
    padded_img = Image.new("RGB", (new_width, new_height), "grey")
    paste_pos_x = (new_width - scaled_width) // 2
    paste_pos_y = (new_height - scaled_height) // 2
    padded_img.paste(scaled_image, (paste_pos_x, paste_pos_y))

    # add text
    draw = ImageDraw.Draw(padded_img)
    font = ImageFont.truetype("OpenSans-Italic.ttf", font_size)
    text_width = draw.textlength(text, font=font)
    text_height = font_size * 1
    text_x = (new_width - text_width) / 2
    text_y = paste_pos_y + scaled_height + 25
    draw.text((text_x, text_y), text, fill="white", font=font, align="center")
    if compress:
        compressed_image = padded_img.resize((7680, 4320), Image.LANCZOS)
        compressed_image.save(output_image_path, 'JPEG', quality=100)
    else: 
        padded_img.save(output_image_path, 'JPEG', quality=100)

def main(in_path, out_path, compress=False):
    for i in tqdm(os.listdir(in_path)):
        if i == ".DS_Store":
            continue
        with open(os.path.join(in_path, i), 'rb') as f:
            tags = exifread.process_file(f)
            text = get_info(tags)
            # print(text)
            add_padding(os.path.join(in_path, i), os.path.join(out_path, i), text, font_size=200, compress=compress, padding=800, format='JPEG')

if __name__ == "__main__":
    in_path = "/Users/jeremy/Desktop/photo_frame/nikon_photo_frame/input"
    out_path = "/Users/jeremy/Desktop/photo_frame/nikon_photo_frame/output"
    print("Need compress?")
    compress = input()
    if compress == "yes":
        main(in_path, out_path, compress=True)
    else:
        main(in_path, out_path)



