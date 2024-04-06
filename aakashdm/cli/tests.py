import datetime
import sys

import click
import requests
from myaakash import SessionService, TestPlatform

from aakashdm.cli.sessions import sessions_shell_completion
from aakashdm.database import DB_FILE, QuestionsDB
from aakashdm.sessionizer import get_session


@click.group("tests")
def tests():
    "Download tests and analysis or generate retests"


def _generate_filters(test_types: str):
    tests = [i.lower() for i in test_types.split(",")]

    AVAILABLE_TESTS = {
        "fts": "Final Test Series",
        "ats": "Archive Test Series",
        "aiats": "AIATS",
    }

    filters = {
        "type": [],
        "user_state": ["completed"],
        "status": ["passed"],
        "mode": ["Online"],
    }
    for test in tests:
        if AVAILABLE_TESTS.get(test):
            filters["type"].append(AVAILABLE_TESTS[test])

    return filters


@tests.command("hoard")
@click.option(
    "--types", type=str, default="", help="Type of tests to hoard. ex: fts,ats"
)
@click.option(
    "--session",
    "session_psid",
    type=str,
    required=True,
    help="Session PSID",
    shell_complete=sessions_shell_completion,
)
def hoard_tests(types: str, session_psid: str):
    filters = _generate_filters(types)

    aakash = SessionService()
    session = get_session(session_psid)
    if not session:
        click.echo(
            "No active session found. Please add session with the command 'aakashdm session add'."
        )
        sys.exit(1)

    aakash.token_login(session["tokens"])

    unfiltered_tests = []
    for status in filters["status"]:
        unfiltered_tests.extend(aakash.get_tests(status))

    tests = []
    for test in unfiltered_tests:
        if test["status"] not in filters["status"]:
            continue
        elif test["type"] not in filters["type"]:
            continue
        elif test["user_state"] not in filters["user_state"]:
            continue
        elif test["mode"] not in filters["mode"]:
            continue
        elif datetime.datetime.now() < datetime.datetime.fromisoformat(
            test["result_date_time"][:-6]
        ):
            continue
        elif test["short_code"][-2] == "P":
            continue

        tests.append(test)

    db = QuestionsDB(DB_FILE)

    for i, test in enumerate(tests, start=1):
        test_id = test["id"]
        test_number = test["number"]
        test_short_code = test["short_code"]
        db.add_test(test_id, test["type"], test_short_code)

        print(
            f"Hoarding Test '{test_short_code}' [{i}/{len(tests)}]     ",
            end="\r",
            flush=True,
        )

        url = aakash.get_url(
            test_id,
            test_number,
            test_short_code,
            "result",
        )["result_url"]

        test_platform = TestPlatform(url)
        question_json_link = test_platform.attempt(False)["questions_url"]
        questions = requests.get(question_json_link).json()["questions"]
        answers = test_platform.get_analysis_answers()

        for question_id, question in questions.items():
            db.add_chapter(
                question["chapters"][0]["id"],
                question["chapters"][0]["name"],
                question["subjects"][0]["name"],
                commit=False,
            )
            answer = {}
            for a in answers:
                if int(a["question_id"]) == int(question_id):
                    answer = a
                    break

            if answer["question_type"] == "SCMCQ":
                choice_map = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0}
                answer_id = db.add_answer(
                    answer["question_type"],
                    choice_map[answer["answer"][0]],
                    answer["language_data"]["en"]["solution"],
                    tuple(question["language_data"]["en"]["choices"]),
                    commit=False,
                )
            else:
                answer_id = db.add_answer(
                    answer["question_type"],
                    float(answer["answer"][0]),
                    answer["language_data"]["en"]["solution"],
                    commit=False,
                )

            db.add_question(
                question_id,
                int(session_psid),
                bool(answer["is_correct"]),
                (question["marks"], question["negative_marks"]),
                question["language_data"]["en"]["text"],
                question["language_data"]["en"]["short_text"],
                int(answer_id if answer_id else 0),
                question["chapters"][0]["id"],
                test_id,
                commit=False,
            )
            db.conn.commit()

    print()
