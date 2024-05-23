import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from quiz_app.db import get_db
from quiz_app.auth import login_required
import json
bp = Blueprint('interface', __name__, url_prefix='/')

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    Quizzes = get_db().execute(
        'SELECT * FROM Quizzes'
    ).fetchall()
    print("hello\n\n")
    print(Quizzes)
    if(request.method == 'POST'):
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        print(session)
        return redirect(url_for('interface.student_interface'))
    return render_template('dashboard.html', Quizzes=Quizzes)


@bp.route('/student_interface', methods=('GET', 'POST'), endpoint='student_interface')
@login_required
def student_interface():
    quiz = get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)
    ).fetchone()
    ques_count = get_db().execute(
        'SELECT COUNT(*) FROM Questions WHERE quiz_id = ?', (quiz['quiz_id'],)
    ).fetchone()
    current_question = get_db().execute(
        'SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], session['current_question'],)
    ).fetchone()
    if request.method == 'POST':
        session['current_question'] = session['current_question'] + 1
        if(session['current_question'] > ques_count[0]):
            return redirect(url_for('interface.thankyou'))
        return redirect(url_for('interface.student_interface'))
    try:
        options = current_question['options']
        options = json.loads(options)
    except:
        return redirect(url_for('interface.dashboard'))
        
    return render_template('student_interface.html' ,quiz=quiz, ques=current_question, ques_count=ques_count[0], options=options)


@bp.route('/thankyou')
@login_required
def thankyou():
    return render_template('thankyou.html')
