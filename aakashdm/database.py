import os
import sqlite3
from typing import Literal

from aakashdm.utils import get_user_data_folder

DB_FILE = os.path.join(get_user_data_folder(), "questions_hoard.sqlite")


class QuestionsDB:
    """
    Questions class.

    Contains methods to (add, update or lookup) questions, answers and chapters.

    """

    QUESTIONS_TABLE = "questions"
    ANSWERS_TABLE = "answers"
    CHAPTERS_TABLE = "chapters"
    TESTS_TABLE = "tests"

    def __init__(self, db_path: str) -> None:
        """Creates a database (if it doesn't exist), connects to it and sets up all the tables.

        Args:
            db_path (str): Database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

        self.__setup_database()

    def __del__(self) -> None:
        self.cur.fetchall()
        self.cur.close()
        self.conn.close()

    def __setup_database(self, commit=True):
        CREATE_QUESTIONS_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.QUESTIONS_TABLE}(
            user_psid INTEGER,
            question_id INTEGER PRIMARY KEY NOT NULL,
            is_correct INTEGER,
            positive_marks INTEGER,
            negative_marks INTEGER,
            question_blob BLOB,
            question_short TEXT,
            answer_id INTEGER,
            chapter_id INTEGER,
            test_id INTEGER,
            FOREIGN KEY(answer_id) REFERENCES {self.ANSWERS_TABLE}(id),
            FOREIGN KEY(chapter_id) REFERENCES {self.CHAPTERS_TABLE}(chapter_id),
            FOREIGN KEY(test_id) REFERENCES {self.TESTS_TABLE}(test_id)
        )"""

        CREATE_ANSWERS_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.ANSWERS_TABLE}(
            id INTEGER PRIMARY KEY,
            question_type TEXT,
            choice1 BLOB,
            choice2 BLOB,
            choice3 BLOB,
            choice4 BLOB,
            answer REAL,
            solution BLOB
        )"""

        CREATE_CHAPTERS_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.CHAPTERS_TABLE}(
            chapter_id INTEGER PRIMARY KEY,
            chapter_name TEXT,
            subject_name TEXT

        )"""

        CREATE_TESTS_TABLE = f"""CREATE TABLE IF NOT EXISTS {self.TESTS_TABLE}(
                test_id INTEGER PRIMARY KEY,
                test_type TEXT,
                short_code TEXT
                )"""

        self.cur.execute(CREATE_CHAPTERS_TABLE)
        self.cur.execute(CREATE_TESTS_TABLE)
        self.cur.execute(CREATE_ANSWERS_TABLE)
        self.cur.execute(CREATE_QUESTIONS_TABLE)

        if commit:
            self.conn.commit()

    def add_chapter(
        self, chapter_id: int, chapter_name: str, subject_name: str, commit=True
    ):
        SEARCH_CHAPTER = f"SELECT * FROM {self.CHAPTERS_TABLE} WHERE chapter_id=?"

        self.cur.execute(SEARCH_CHAPTER, (chapter_id,))
        already_has = self.cur.fetchall()
        if already_has:
            return

        INSERT = f"INSERT INTO {self.CHAPTERS_TABLE} VALUES (?, ?, ?)"
        self.cur.execute(INSERT, (chapter_id, chapter_name, subject_name))

        if commit:
            self.conn.commit()

    def add_test(self, test_id: int, test_type: str, short_code: str, commit=True):
        SEARCH_CHAPTER = f"SELECT * FROM {self.TESTS_TABLE} WHERE test_id=?"

        self.cur.execute(SEARCH_CHAPTER, (test_id,))

        already_has = self.cur.fetchall()
        if already_has:
            return

        INSERT = f"INSERT INTO {self.TESTS_TABLE} VALUES (?, ?, ?)"
        self.cur.execute(INSERT, (test_id, test_type, short_code))

        if commit:
            self.conn.commit()

    def add_answer(
        self,
        question_type: Literal["SAN", "SCMCQ"],
        answer: float,
        solution: str,
        choices: tuple[dict, dict, dict, dict] = ({}, {}, {}, {}),
        commit=True,
    ):

        if question_type == "SAN":
            INSERT = f"INSERT INTO {self.ANSWERS_TABLE}(question_type, answer, solution) VALUES (?, ?, ?)"
            self.cur.execute(INSERT, (question_type, answer, solution))
        else:
            INSERT = f"INSERT INTO {self.ANSWERS_TABLE}(question_type, choice1, choice2, choice3, choice4, answer, solution) VALUES (?, ?, ?, ?, ?, ?, ?)"
            self.cur.execute(
                INSERT,
                (
                    question_type,
                    choices[0]["text"],
                    choices[1]["text"],
                    choices[2]["text"],
                    choices[3]["text"],
                    answer,
                    solution,
                ),
            )

        if commit:
            self.conn.commit()
        return self.cur.lastrowid

    def add_question(
        self,
        question_id: int,
        user_psid: int,
        is_correct: bool,
        marking_scheme: tuple[int, int],
        question_blob: str,
        question_short: str,
        answer_id: int,
        chapter_id: int,
        test_id: int,
        commit=True,
    ):
        QUERY = f"SELECT * FROM {self.QUESTIONS_TABLE} WHERE question_id=?"

        self.cur.execute(QUERY, (question_id,))
        already_has = self.cur.fetchall()
        if already_has:
            return

        INSERT = (
            f"INSERT INTO {self.QUESTIONS_TABLE} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )

        self.cur.execute(
            INSERT,
            (
                user_psid,
                question_id,
                int(is_correct),
                marking_scheme[0],
                marking_scheme[1],
                question_blob,
                question_short,
                answer_id,
                chapter_id,
                test_id,
            ),
        )

        if commit:
            self.conn.commit()
