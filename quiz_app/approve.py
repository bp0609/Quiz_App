from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort
from quiz_app.auth import login_required, admin_login_required
from quiz_app.db import get_db
from datetime import datetime
import random

bp = Blueprint('approve', __name__, url_prefix='/')

@bp.route('/approve_users', methods=('GET', 'POST'))
@login_required
def approve_users():
    db = get_db()
    
    # Fetch all users except the current approver
    users = db.execute(
        'SELECT id, username FROM Users WHERE id != ?', (g.user['id'],)
    ).fetchall()
    
    if request.method == 'POST':
        approved_usernames = request.form.getlist('approved_users')
        if approved_usernames:
            quiz_id = session.get('quiz_id', None)
            
            if quiz_id:
                approver_id = g.user['id']
                for username in approved_usernames:
                    approved_user = db.execute(
                        'SELECT id FROM Users WHERE username = ?', (username,)
                    ).fetchone()
                    
                    if approved_user:
                        db.execute(
                            'INSERT INTO ApprovedUsers (approver_id, approved_id, quiz_id, approval_time)'
                            ' VALUES (?, ?, ?, ?)',
                            (approver_id, approved_user['id'], quiz_id, db.execute('SELECT DATETIME("now", "localtime")').fetchone()[0])
                        )
                        db.commit()
                        flash('Users approved successfully.')
                        return redirect(url_for('interface.quiz_interface'))
            else:
                flash('Quiz ID not found in session.')
        else:
            flash('No users selected for approval.')
    
    return render_template('approval.html', users=users)


nums = list([])

@bp.route('/appr_num/<int:quiz_id>', methods=('GET', 'POST'))
@admin_login_required
def appr_num(quiz_id,nums=nums):
    session['quiz_id'] = quiz_id
    db = get_db()
    if request.method == 'POST':
        appr_num = request.form['appr_num']
        db.execute('UPDATE Quizzes SET appr_num = ? WHERE quiz_id = ?', (appr_num, quiz_id))
        db.commit()
        flash('Approval Number is set Successfully.')
        return redirect(url_for('quiz.start_quiz',quiz_id=quiz_id))
    nums[0:3] = random.sample(range(1, 100), 3)
    return render_template('admin_appr_no.html',quiz_id=quiz_id,nums=nums)


@bp.route('/check_appr_num/<int:quiz_id>', methods=('GET', 'POST'))
@login_required
def check_appr_num(quiz_id,nums=nums):
    db = get_db()
    if request.method == 'POST':
        appr_num = db.execute('SELECT appr_num FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()['appr_num']
        if appr_num == int(request.form['selected_num']):
            return redirect(url_for('interface.information',quiz_id=quiz_id))
        else:
            flash('Approval Number is Incorrect.')
            return redirect(url_for('interface.dashboard'))
    return render_template('check_appr_num.html',nums=nums,quiz_id=quiz_id)