from flask import Blueprint, abort, render_template

from aakashdm import PROG
from aakashdm.database import DB_FILE, QuestionsDB

router = Blueprint("router", PROG, template_folder="server/templates")


@router.get("/")
def home():
    db = QuestionsDB(DB_FILE)
    GET_SUBJECTS_CHAPTERS = (
        f"SELECT chapter_name, subject_name FROM {db.CHAPTERS_TABLE};"
    )

    db.cur.execute(GET_SUBJECTS_CHAPTERS)
    r = db.cur.fetchall()
    del db

    chapters = {}
    for i in r:
        if not isinstance(chapters.get(i[1]), set):
            chapters[i[1]] = set()

        chapters[i[1]].add(i[0])

    for i, k in chapters.items():
        chapters[i] = sorted(k, key=lambda x: x)
        for j in chapters[i]:
            print(repr(j))

    return render_template("index.html", chapters=chapters)


@router.get("/question/<int:qid>")
def question(qid: int):
    db = QuestionsDB(DB_FILE)
    SELECT_QUESTION = f"SELECT question_id, question_blob, answer_id, is_correct FROM {db.QUESTIONS_TABLE} WHERE question_id=?"
    SELECT_ANSWER = f"SELECT question_type,answer,solution,choice1,choice2,choice3,choice4 FROM {db.ANSWERS_TABLE} WHERE id=?"
    db.cur.execute(SELECT_QUESTION, (qid,))
    ques = db.cur.fetchone()

    if not ques:
        abort(404)

    db.cur.execute(SELECT_ANSWER, (ques[2],))
    ans = db.cur.fetchone()
    del db
    choice_type = True if ans[0] == "SCMCQ" else False
    question = ques[1]
    choice = (ans[-4], ans[-3], ans[-2], ans[-1])

    return render_template(
        "question.html",
        is_correct=bool(ques[-1]),
        question_id=qid,
        question=question,
        choice_type=choice_type,
        choice=choice,
        answer=ans[1],
        solution=ans[2],
    )


@router.get("/s/<string:subject>/c/<string:chapter>")
def get_chapter(subject: str, chapter: str):
    db = QuestionsDB(DB_FILE)
    SELECT_QUESTIONS = f"select question_id, is_correct, question_blob, answer_id from {db.QUESTIONS_TABLE} where chapter_id in (select chapter_id from {db.CHAPTERS_TABLE} where chapter_name = ? and subject_name = ?)"
    SELECT_ANSWER = f"SELECT question_type,answer,solution,choice1,choice2,choice3,choice4 FROM {db.ANSWERS_TABLE} WHERE id=?"

    db.cur.execute(SELECT_QUESTIONS, (chapter, subject))
    questions = db.cur.fetchall()
    if not questions:
        abort(404)

    serialize_questions = []
    for i, (question_id, is_correct, question, answer_id) in enumerate(
        questions, start=1
    ):

        db.cur.execute(SELECT_ANSWER, (answer_id,))
        ans = db.cur.fetchone()
        choice_type = True if ans[0] == "SCMCQ" else False
        choice = (ans[-4], ans[-3], ans[-2], ans[-1])

        q = (
            i,
            bool(is_correct),
            question_id,
            question,
            choice_type,
            choice,
            ans[1],
            ans[2],
        )
        serialize_questions.append(q)

    del db

    return render_template(
        "chapter.html", questions=serialize_questions, subject=subject, chapter=chapter
    )
