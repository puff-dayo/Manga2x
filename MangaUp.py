import io
import zipfile

from PIL import Image
from realesrgan_ncnn_py import Realesrgan
from tqdm import tqdm
from waifu2x_ncnn_py import Waifu2x


def extract_epub(_epub_path):
    with zipfile.ZipFile(_epub_path, 'r') as zip_ref:
        file_contents = {name: zip_ref.read(name) for name in zip_ref.namelist()}
    return file_contents


def find_images_in_directory(file_contents):
    images_info = []
    for file_name, content in file_contents.items():
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            images_info.append((file_name, content))
    return images_info


def upscale_images(images_info, waifu2x):
    scaled_images_info = []
    for image_name, content in tqdm(images_info, desc="Up-scaling images"):
        with Image.open(io.BytesIO(content)) as image:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            scaled_image = waifu2x.process_pil(image)
            output_bytes = io.BytesIO()
            scaled_image.save(output_bytes, format='JPEG', quality=85)
            scaled_images_info.append((image_name, output_bytes.getvalue()))
    return scaled_images_info


def replace_images_in_directory(file_contents, scaled_images_info):
    for image_name, scaled_content in tqdm(scaled_images_info, desc="Replacing images"):
        file_contents[image_name] = scaled_content


def repack_epub(file_contents, _output_epub_path):
    with zipfile.ZipFile(_output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_name, content in tqdm(file_contents.items(), desc="Repacking EPUB"):
            zipf.writestr(file_name, content)


def manga_up(_epub_path, _output_epub_path, _method):
    # print(method)
    file_contents = extract_epub(_epub_path)
    images_info = find_images_in_directory(file_contents)
    if _method == "Moderate":
        processor = Waifu2x(gpuid=0, scale=2, noise=2, model="models-upconv_7_anime_style_art_rgb", tilesize=768)
    elif _method == "Sharp":
        processor = Realesrgan(gpuid=0, model=0, tilesize=384)
    else:
        return -1
    scaled_images_info = upscale_images(images_info, processor)
    replace_images_in_directory(file_contents, scaled_images_info)
    repack_epub(file_contents, _output_epub_path)

    print(f"Up-scaled EPUB saved to: {_output_epub_path}")

    return 0


if __name__ == "__main__":
    epub_path = ''
    method = 'Moderate'  # or 'Sharp'
    output_epub_path = epub_path + f"_{method}2x"
    manga_up(epub_path + '.epub', output_epub_path + '.epub', method)
