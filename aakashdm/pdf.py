import requests
import pikepdf
import tqdm


def download_pdf(url: str, save_file: str, title: str):
    DESC_LENGTH = 20
    if len(title) > DESC_LENGTH:
        title = title[:18] + "..."
    with requests.get(url, stream=True) as s, open(save_file, "wb") as f:
        size = s.headers.get("content-length")
        chunk_size = 2 * 1024 * 1024
        bar = tqdm.tqdm(
            total=int(size) if size else None, unit="bytes", unit_scale=True, desc=title
        )
        for chunk in s.iter_content(chunk_size):
            f.write(chunk)
            bar.update(chunk_size)


def deDRM_pdf(pdf_file: str, password: str, save_file=None):
    pdf = pikepdf.open(pdf_file, password=password, allow_overwriting_input=True)

    if save_file:
        pdf_file = save_file
    pdf.save(pdf_file)
