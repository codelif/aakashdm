import base64
import os
import sys
from collections.abc import Callable

import click
from myaakash import SessionService

import aakashdm.pdf
import aakashdm.sessionizer


@click.group("targets")
def targets():
    """Downloads for Aakash Targets/Books"""


def choose(options: list, desc: str, extractor: Callable, args=[]) -> int:
    print()
    for i, option in enumerate(options, start=1):
        if extractor:
            option = extractor(option, *args)
        index = f"{i}) "
        option_texts = option.splitlines()
        print(f"{i}) {option_texts[0]}")
        for line in option_texts[1:]:
            print(" " * len(index) + line)
        else:
            print()

    prompt = f"\nChoose a {desc} [1-{len(options)}]: "
    while True:
        choice = input(prompt)
        if (not choice.isdigit()) or (not 1 <= int(choice) <= len(options)):
            print("Please choose a number from given options!")
            continue
        break

    return int(choice) - 1


def prepare_session_choice(key: dict, sessions: dict):
    session = sessions[key]

    name = session["name"]
    psid = session["PSID"]
    return f"NAME: {name}\nPSID: {psid}"


@targets.command("interactive")
def book_download():
    print(
        "Welcome to one-of-a-kind SessionService Assets Downloader! Sail the Low Seas...\n"
    )
    sessions = aakashdm.sessionizer.get_sessions()

    if sessions:
        keys = list(sessions.keys())
        choice = choose(keys, "Session", prepare_session_choice, (sessions,))
        session = sessions[keys[choice]]
    else:
        click.echo(
            "No active session found. Please add session with the command 'aakashdm session add'."
        )
        sys.exit(1)

    myaakash = SessionService()
    myaakash.token_login(session["tokens"])
    aakashdm.sessionizer.save_session(myaakash)

    packages = myaakash.get_packages()
    choice = choose(packages, "Package", lambda x: x["title"])
    package = packages[choice]

    courses = package["courses"]
    choice = choose(courses, "Subject", lambda x: x["subject_name"])
    course = courses[choice]

    package_id = package["id"]
    course_id = course["id"]

    chapters = myaakash.get_course(package_id, course_id)
    choice = choose(chapters, "Chapter", lambda x: x["name"])
    chapter = chapters[choice]
    chapter_id = chapter["id"]

    assets = myaakash.get_chapter_assets(package_id, course_id, chapter_id)
    choice = choose(assets["assets"]["ebooks"], "Book", lambda x: x["title"])
    asset = assets["assets"]["ebooks"][choice]
    asset_id = asset["id"]

    book = myaakash.get_asset(package_id, course_id, chapter_id, asset_id, "ebook")
    url = book["url"]
    pdf_pswd_b64 = book["license"]
    pdf_pswd = base64.b64decode(pdf_pswd_b64).decode("utf-8")

    aakashdm.pdf.download_pdf(url, os.path.basename(url), asset["title"])
    aakashdm.pdf.deDRM_pdf(os.path.basename(url), pdf_pswd)


@targets.command("bulk")
def bulk_download():
    print(
        "Welcome to one-of-a-kind SessionService Assets Downloader! Sail the Low Seas...\n"
    )
    sessions = aakashdm.sessionizer.get_sessions()

    if sessions:
        keys = list(sessions.keys())
        choice = choose(keys, "Session", prepare_session_choice, (sessions,))
        session = sessions[keys[choice]]
    else:
        print(
            "No active session found. Please add session with the command 'aakashdm session add'."
        )
        sys.exit(1)

    myaakash = SessionService()
    myaakash.token_login(session["tokens"])
    aakashdm.sessionizer.save_session(myaakash)

    packages = myaakash.get_packages()
    choice = choose(packages, "Package", lambda x: x["title"])
    package = packages[choice]

    root = (
        f"~/Downloads/aakashdm_downloads/{myaakash.profile['psid']}/{package['title']}"
    )
    root = os.path.expanduser(root)

    for course in package["courses"]:
        print("Getting Subject '%s'..." % course["subject_name"])
        course_folder = os.path.join(root, course["subject_name"])
        package_id = package["id"]
        course_id = course["id"]

        chapters = myaakash.get_course(package_id, course_id)

        for i, chapter in enumerate(chapters, start=1):
            print(f"Getting Chapter '{chapter['name']}' [{i}/{len(chapters)}]")
            chapter_folder = os.path.join(course_folder, chapter["name"])
            chapter_id = chapter["id"]

            assets = myaakash.get_chapter_assets(package_id, course_id, chapter_id)
            asset = assets["assets"]["ebooks"][0]
            asset_id = asset["id"]

            book = myaakash.get_asset(
                package_id, course_id, chapter_id, asset_id, "ebook"
            )
            url = book["url"]
            pdf_pswd_b64 = book["license"]
            pdf_pswd = base64.b64decode(pdf_pswd_b64).decode("utf-8")
            pdf_file = os.path.join(chapter_folder, os.path.basename(url))

            os.makedirs(chapter_folder, exist_ok=True)
            aakashdm.pdf.download_pdf(url, pdf_file, asset["title"])
            aakashdm.pdf.deDRM_pdf(pdf_file, pdf_pswd)
