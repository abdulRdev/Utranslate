
from wtforms.widgets import TextArea
from wtforms_components import ColorField, DateRange
from datetime import date
logged = False
go = False
liname = []
licat = []
licolor = []
lipost = []
lidate = []
from flask import Flask, url_for, render_template, request, flash, session, redirect
from flask_login import current_user
from wtforms.fields.html5 import DateField, EmailField
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField  # , DateField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, Length, Regexp
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import csv
import smtplib

#Bootstrap(app)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'unknown'
#app.config['MAIL_SERVER']= 'smtp.gmail.com'
#app.config['MAIL_PORT']=465
#app.config['MAIL_USE_SSL']=True
#app.config['MAIL_USERNAME'] = 'USERNAME'
#app.config['MAIL_PASSWORD'] = '*****'

#mail=Mail(app)


@app.route('/')
def home():
   # session.clear()
    return render_template('Home.html')

#@app.route('/sending')
#def sending():
#    message= Message('Hellooo',sender='EMAIL',recipients=['EMAIL'])
#    mail.send(message)
#    return 'Message sent!'

@app.route('/new')
def new():
    if "user" in session:
        user = session["user"]
        f = open('data/userpost.csv', 'r')
        reader = csv.reader(f)
        liname = []
        licat = []
        licolor = []
        lipost = []
        lidate = []

        for row in reader:
            liname.insert(0,row[0])
            licat.insert(0,row[1])
            licolor.insert(0,row[2])
            lipost.insert(0,row[3])
            lidate.insert(0,row[4])

        go = True
        # return'<h1>match<h1/>'
        f.close()

        length = len(liname)
        return render_template('WhatNew.html', logged=True,go=go,length=length,licolor=licolor,liname=liname,licat=licat,
                               lipost=lipost,lidate=lidate)
    else:
        return render_template('WhatNew.html', logged=False)


class FormPost (FlaskForm):
    select = SelectField ('Category', validators=[InputRequired()],
                          choices=[('General','General'),('Technology','Technology'),('Food','Food'),('School','School'),
                                   ('Long phrases or paragraphs','Long phrases or paragraphs')])
    color = RadioField('Color of post',validators=[InputRequired()],
                             choices=[('lightblue', 'Light Blue'),('lightyellow', 'Light Yellow'), ('lightgreen', 'Light Green'),
                                      ('#ffe160', 'Orange')],render_kw={'required': True})
    date = DateField('Date', format='%Y-%m-%d', validators=[InputRequired() ])


    content = StringField (u'Text',widget=TextArea(), validators=[InputRequired()] ) #should it be u'Text'
    submit = SubmitField('Post!')

@app.route('/post', methods=['GET','POST'])
def post():
    if "user" not in session:
        return redirect(url_for('login'))

    user = session["user"]
    form = FormPost()
    if form.validate_on_submit():
       go = True
       f = open('data/userpost.csv', 'a')
       f.write("{},{},{},{},{}\n".format(user,form.select.data,form.color.data,form.content.data,form.date.data))
       f.close()

       liname.append(user)
       licat.append(form.select.data)
       licolor.append(form.color.data)
       lipost.append(form.content.data)
       lidate.append(form.date.data)

       length = len(liname)
       length = len(liname)


       return render_template('WhatNew.html',logged=True,liname=liname,licat=licat,licolor=licolor,lipost=lipost,lidate=lidate,length=length,go=go)
    else:
        return render_template('Post.html', logged=True, user=user,form=form)

@app.route('/translate')
def translate():
    if "user" in session:
        user = session["user"]
        return render_template('Translate.html', logged=True)
    else:
        return render_template('Translate.html', logged=False)

    # REGISTER
class Register(FlaskForm):  # inherits from flask form
        # '*Usernames must start with a letter and must have only letters, numbers, dots or underscores'

        newuser = StringField('Username',
                              validators=[InputRequired(), Length(6, 20), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, )])
        newpass = PasswordField('Password', validators=[InputRequired(), Length(6, 10)])
        newpass2 = PasswordField('Retype password',
                                 validators=[InputRequired(), EqualTo('newpass', message='Password must match.')])
        email = EmailField('Email', validators=[InputRequired()])

        submit = SubmitField('Sign me up!')

@app.route('/register', methods=['GET', 'POST'])
def register():
        form = Register()
        if form.validate_on_submit():
            f = open('data/users.csv', 'a')
            f.write("\n{},{}".format(form.newuser.data, form.newpass.data))
            message= "\tHi! Welcome to Utranslate!   Learning a language can often be confusing and difficult. There are times when you may need to know how to say a phrase in another language on the go. Although, common translators such as Google Translate may be able to give you quick answers, their responses are often times inaccurate and not what you are looking for. These common translators are also unable to understand the contemporary language that is used such as slang. Try writing out some slang on a common translator and see for yourself. This is why Utranslate has been introduced!\n\nUtranslate will allow you to have any phrase or word precisely translated in the language that you want. Furthermore,each user will also have the opportunity to help others out by translating their inquiries. This is all done through the Utranslate community.No more language barriers! Begin writing your post to get started."

            #Email and password functionality disabled for privacy
         #   server= smtplib .SMTP("smtp.gmail.com",587)
         #   server.starttls()
         #   server.login("EMAIL","PASSWORD")#Write pw heree
         #   server.sendmail("EMAIL",form.email.data,message)
            return redirect(url_for('login'))

        else:
            flash('Here are some tips when creating an account:')
            flash('*Usernames must start with a letter and must have only letters, numbers, dots or underscores')
            flash('*Usernames must be atleast 6 characters long')
            flash('*Password must be 6-10 characters long')
            return render_template('Register.html', form=form, logged=False)

    # LOGIN
class LoginForm(FlaskForm):  # inherits from flask form
        username = StringField('Username', validators=[InputRequired()])
        password = PasswordField('Password', validators=[InputRequired()])
        submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
        error = None
        form = LoginForm()

        if "user" in session:
            user = session["user"]
            session.clear()
            return redirect(url_for('login'))

        if form.validate_on_submit():

            session["user"] = form.username.data  # saving user's name
            f = open('data/users.csv', 'r')
            reader = csv.reader(f)
            for row in reader:
                if form.username.data == row[0] and form.password.data == row[1]:
                    session["user"] = form.username.data
                    f.close()
                    return render_template("WhatNew.html", logged=True)
                else:
                    session.clear()
                    flash('*Incorrect username or password')
                   # return render_template("Login.html", form=form, error=error, logged=False)

        return render_template("Login.html", form=form, error=error, logged=False)

    #FORGOT
class Forgot (FlaskForm): #inherits from flask form
    newuser = StringField('Username', validators=[InputRequired(), Length(6,20),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,)])
    submit = SubmitField('Confirm username')

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    form = Forgot()

    if form.validate_on_submit():

        f = open('data/users.csv', 'r+')
        reader = csv.reader(f)
        for row in reader:
            if form.newuser.data == row[0]:
                name=form.newuser.data
                f.write('\n{},'.format(form.newuser.data))
                f.close()
                #return name
                return redirect(url_for('reset'))

    return render_template('Forgot.html', form=form, logged=False)


    #RESET
class Reset(FlaskForm):
    newpass = PasswordField('Password', validators=[InputRequired(), Length(6, 10)])
    newpass2 = PasswordField('Retype password',
                             validators=[InputRequired(), EqualTo('newpass', message='Password must match.')])

    submit = SubmitField('Change password')


@app.route('/reset', methods=['GET','POST'])
def reset():
    form=Reset()
    if form.validate_on_submit():
        f = open('data/users.csv', 'a')#check this out
        writer = csv.writer(f)
        f.write(form.newpass.data)

        flash('Your password has been reset')
        return redirect(url_for('login'))
    return render_template("Reset.html", form=form, logged=False)



    #CONTACT
@app.route('/contact')
def contact():

    if "user" in session:
        user = session["user"]
        return render_template('ContactUs.html', logged=True)
    else:
        return render_template('ContactUs.html', logged=False)

if __name__ == '__main__':
    app.run()