from flask import render_template, request, flash, redirect, url_for
from app.auth.forms import RegistrationForm, LoginForm
from app.auth import authentication
from app.auth.models import User
from flask_login import login_user, logout_user, login_required, current_user
import sqlite3 as sql
import requests

@authentication.route('/register', methods=['GET','post'])
def register_user():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('authentication.homepage'))
    form = RegistrationForm()

    if form.validate_on_submit():
        User.create_user(
            user=form.name.data,
            email=form.email.data,
            super_user=False,
            password=form.password.data
        )
        flash("Registration Successful")
        return redirect(url_for('authentication.log_in_user'))
        
    return render_template('registration.html', form=form)

@authentication.route('/')
def index():
    return homepage()

@authentication.route('/login', methods=['GET','POST'])
def log_in_user():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('authentication.homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid credentials")
            return redirect(url_for('authentication.log_in_user'))
        
        login_user(user, form.stay_loggedin.data)
        return(redirect(url_for('authentication.homepage')))
        
    return render_template('login.html', form=form)

@authentication.route('/homepage')
@login_required
def homepage():
    con=sql.connect("instance/db_employees.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from users WHERE ADMIN_ID = '" + str(current_user.id) + "'")
    data=cur.fetchall()
    return render_template('homepage.html',datas=data)

@authentication.route('/admin')
@login_required
def admin():
    if current_user.super_user == False:
        return(redirect(url_for('authentication.homepage')))
    con=sql.connect("instance/db_admins.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from users")
    data=cur.fetchall()
    return render_template('admin.html',datas=data)

@authentication.route('/logout', methods=['GET'])
@login_required
def log_out_user():
    #session.clear()  
    logout_user()
    return redirect(url_for('authentication.log_in_user'))

@authentication.route("/add_user",methods=['POST','GET'])
@login_required
def add_user():
    if request.method=='POST':
        con=sql.connect("instance/db_employees.db")
        cur=con.cursor()

        uname=request.form['uname']
        cur.execute("select * from users WHERE UNAME='" + uname + "'")
        data=cur.fetchall()
        if len(data)!=0:
            return render_template("add_user.html", error="Error: That username is taken")

        contact=request.form['contact']
        cur.execute("select * from users WHERE CONTACT='" + contact + "'")
        data=cur.fetchall()
        if len(data)!=0:
            return render_template("add_user.html", error="Error: That email address is taken")

        code=""
        unique_code = False
        while not unique_code:
            code = requests.get("https://www.passwordrandom.com/query?command=password").text
            cur.execute("select * from users WHERE CODE='" + code + "'")
            data=cur.fetchall()
            if len(data)==0:
                unique_code = True
        
        cur.execute("insert into users(UNAME,CONTACT,CODE,ADMIN_ID,ONSITE) values (?,?,?,?,?)",(uname,contact,code,current_user.id,False))
        con.commit()
        flash('User Added','success')
        return redirect(url_for("authentication.homepage"))
    return render_template("add_user.html")

@authentication.route("/edit_user/<string:uid>",methods=['POST','GET'])
@login_required
def edit_user(uid):
    if request.method=='POST':
        uname=request.form['uname']
        contact=request.form['contact']
        onsite=True
        try:
            request.form['onsite']
        except:
            onsite=False
        con=sql.connect("instance/db_employees.db")
        cur=con.cursor()
        cur.execute("update users set UNAME=?,CONTACT=?,ONSITE=? where UID=?",(uname,contact,onsite,uid))
        con.commit()
        flash('User Updated','success')
        return redirect(url_for("authentication.index"))
    con=sql.connect("instance/db_employees.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from users where UID=?",(uid,))
    data=cur.fetchone()
    return render_template("edit_user.html",datas=data)

@authentication.route("/scan_user",methods=['POST','GET'])
def scan_user():
    if request.method=='POST':
        code=request.form['code']
        onsite=True
        try:
            request.form['onsite']
        except:
            onsite=False
        con=sql.connect("instance/db_employees.db")
        cur=con.cursor()
        cur.execute("select UNAME from users WHERE CODE='" + code + "'")
        data=cur.fetchone()
        if len(data) == 0:
            return render_template("scan_user.html", error="Error: this user doesn't exist")
        cur.execute("update users set ONSITE=? where CODE=?",(onsite,code))
        con.commit()
        if (onsite):
            flash(data[0] + ' is now on site','success')
        else:
            flash(data[0] + ' is now off site','success')
        return redirect(url_for("authentication.index"))
    return render_template("scan_user.html")
    
@authentication.route("/delete_user/<string:uid>",methods=['GET'])
def delete_user(uid):
    con=sql.connect("instance/db_employees.db")
    cur=con.cursor()
    cur.execute("delete from users where UID=?",(uid,))
    con.commit()
    flash('User Deleted','warning')
    return redirect(url_for("authentication.index"))
    
@authentication.route("/delete_admin/<string:id>",methods=['GET'])
def delete_admin(id):
    con=sql.connect("instance/db_admins.db")
    cur=con.cursor()
    cur.execute("delete from users where id=?",(id))
    con.commit()
    flash('User Deleted','warning')
    return redirect(url_for("authentication.index"))
    
@authentication.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404