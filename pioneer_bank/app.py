from flask import Flask, request, render_template, redirect, session, flash,  url_for, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc, or_
from sqlalchemy.orm import relationship
from PIL import Image
from io import BytesIO
import bcrypt
import base64
import hashlib
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:6381!Root$$@localhost/pioneer_bank'
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(20), unique=True, nullable=True)
    balance = db.Column(db.Float, default=10000.0)  # Initial balance set to $10,000
    profile_picture = db.Column(db.LargeBinary)

    # Relationships
    transactions_sent = db.relationship('TransactionHistory', foreign_keys='TransactionHistory.sender_id', backref='sender', lazy=True)
    transactions_received = db.relationship('TransactionHistory', foreign_keys='TransactionHistory.recipient_id', backref='recipient', lazy=True)

    bank_account = relationship('BankAccount', uselist=False, backref='user', lazy=True)
    
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.bank_account_number = None

    def save_profile_picture(self, image_data):
        self.profile_picture = image_data
        db.session.commit()

    def get_profile_picture(self):
        if self.profile_picture:
            return base64.b64encode(self.profile_picture).decode('utf-8')
        else:
            return None

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def generate_bank_account_number(self):
        count = User.query.filter(User.bank_account_number.isnot(None)).count()
        next_account_number = count + 1
        self.bank_account_number = f'piobnk{next_account_number:04d}'

    def update_balance(self, amount):
        self.balance += amount
        db.session.commit()        

class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_account_number = db.Column(db.String(20))  # Sender's account number
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_account_number = db.Column(db.String(20))  # Recipient's account number
    amount = db.Column(db.Float, nullable=False)  # Amount of the transaction
    transaction_type = db.Column(db.String(20))  # 'sent' or 'received'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, sender_id, sender_account_number, recipient_id, recipient_account_number, amount, transaction_type):
        self.sender_id = sender_id
        self.sender_account_number = sender_account_number
        self.recipient_id = recipient_id
        self.recipient_account_number = recipient_account_number
        self.amount = amount
        self.transaction_type = transaction_type




class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(10), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    citizenship = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    occupation = db.Column(db.String(50))
    monthly_income = db.Column(db.Float)
    id_proof = db.Column(db.String(100))
    transaction_pin_hash = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id, title, gender, telephone, street_address, city, state, postal_code, country, citizenship, dob, occupation, monthly_income, id_proof, transaction_pin):
        self.user_id = user_id
        self.title = title
        self.gender = gender
        self.telephone = telephone
        self.street_address = street_address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country
        self.citizenship = citizenship
        self.dob = dob
        self.occupation = occupation
        self.monthly_income = monthly_income
        self.id_proof = id_proof
        self.transaction_pin_hash = hashlib.sha256(transaction_pin.encode()).hexdigest()

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class LoanApplication(db.Model):
    __tablename__ = 'loan_applications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    employer = db.Column(db.String(100), nullable=False)
    income = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_duration = db.Column(db.Integer, nullable=False)
    loan_purpose = db.Column(db.String(100), nullable=False)
    id_photo = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    
    # Define the relationship to the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('loan_applications', lazy=True))

    def __repr__(self):
        return f'<LoanApplication(id={self.id}, user_id={self.user_id}, status={self.status})>'

class LoanGiven(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    loan_duration = db.Column(db.Integer, nullable=False)
    date_given = db.Column(db.Date, nullable=False, default=datetime.now().date())

    def __repr__(self):
        return f'<LoanGiven(id={self.id}, user_id={self.user_id}, amount={self.amount}, date_given={self.date_given})>'
    

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, default="Pioneer Bank")
    balance = db.Column(db.Float, nullable=False, default=10000000.0)

    def __repr__(self):
        return f'<Bank(name={self.name}, balance={self.balance})>'

# Insert the default value directly into the database
def insert_default_bank_name():
    bank = Bank.query.first()
    if not bank:
        new_bank = Bank(name="Pioneer Bank")
        db.session.add(new_bank)
        db.session.commit()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))



with app.app_context():
    db.create_all()
    insert_default_bank_name()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'error')
            return redirect('/register') 

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/register_account', methods=['POST'])
def register_account():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            bank_account = BankAccount(
                user_id=user.id,
                title=request.form['title'],
                gender=request.form['gender'],
                telephone=request.form['telephone'],
                street_address=request.form['street_address'],
                city=request.form['city'],
                state=request.form['state'],
                postal_code=request.form['postal_code'],
                country=request.form['country'],
                citizenship=request.form['citizenship'],
                dob=request.form['dob'],
                occupation=request.form['occupation'],
                monthly_income=request.form['monthly_income'],
                id_proof=request.files['id_proof'].filename,
                transaction_pin=request.form['transaction_pin']
            )
            db.session.add(bank_account)
            db.session.commit()
            if not user.bank_account_number:
                user.generate_bank_account_number()
                db.session.commit()
            return redirect('/dashboard')
    return redirect('/login')


@app.route('/update_account', methods=['POST'])
def update_account():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            bank_account = BankAccount.query.filter_by(user_id=user.id).first()
            if bank_account:
                bank_account.title = request.form['title']
                bank_account.gender = request.form['gender']
                bank_account.telephone = request.form['telephone']
                bank_account.street_address = request.form['street_address']
                bank_account.city = request.form['city']
                bank_account.state = request.form['state']
                bank_account.postal_code = request.form['postal_code']
                bank_account.country = request.form['country']
                bank_account.citizenship = request.form['citizenship']
                bank_account.dob = request.form['dob']
                bank_account.occupation = request.form['occupation']
                bank_account.monthly_income = request.form['monthly_income']
                bank_account.id_proof = request.files['id_proof'].filename
                bank_account.transaction_pin_hash = hashlib.sha256(request.form['transaction_pin'].encode()).hexdigest()
                db.session.commit()
            else:
                # If the user doesn't have a bank account, redirect to create account page
                return redirect('/create_account?edit=true')
            return redirect('/dashboard')
    return redirect('/login')

from werkzeug.security import check_password_hash, generate_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the provided email and password match the admin credentials
        if email == 'mdali.sheik1613@gmail.com':
            admin_password_hash = 'pbkdf2:sha256:260000$4ooCiftwQ8xh2Hv0$72e57351e753c20e726d4aa28f885ab323a5fbf0d5a73fe87feb30e92e119df2'
            if check_password_hash(admin_password_hash, password):
                # Set session variable to indicate admin login
                session['admin_logged_in'] = True
                session['email'] = email
                # Redirect to admin dashboard
                return redirect('/admin_dashboard')
            else:
                # If admin login fails, display an error message
                flash('Invalid email or password', 'error')
        else:
            # Check if the provided email and password match the regular user credentials
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                # Set session variables for regular user login
                session['email'] = user.email
                session['bank_account_number'] = user.bank_account_number
                # Redirect to user dashboard
                return redirect('/dashboard')
            
            # Check if the provided email and password match the admin credentials stored in the database
            admin = Admin.query.filter_by(email=email).first()
            if admin and admin.check_password(password):
                # Set session variables to indicate admin login
                session['admin_logged_in'] = True
                session['email'] = email
                # Redirect to admin dashboard
                return redirect('/admin_dashboard')
            
            # If login fails for both admin and regular user, display an error message
            flash('Invalid email or password', 'error')


    for message in get_flashed_messages():
        pass

    # If request method is GET or login failed, render the login page
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            # Fetch the last three transactions for the user
            transactions_sent = TransactionHistory.query.filter(
                TransactionHistory.sender_account_number == user.bank_account_number,
                TransactionHistory.transaction_type == 'sent'
            ).order_by(TransactionHistory.timestamp.desc()).limit(3).all()
            
            transactions_received = TransactionHistory.query.filter(
                TransactionHistory.recipient_account_number == user.bank_account_number,
                TransactionHistory.transaction_type == 'received'
            ).order_by(TransactionHistory.timestamp.desc()).limit(3).all()
            
            # Combine sent and received transactions and sort by timestamp
            transactions = sorted(transactions_sent + transactions_received, key=lambda x: x.timestamp, reverse=True)[:3]

            # Map sender's and recipient's bank account numbers to their corresponding user objects
            for transaction in transactions:
                if transaction.sender_id != user.id:
                    transaction.other_user_account_number = transaction.sender.bank_account_number
                    transaction.other_user_name = f"{transaction.sender.first_name} {transaction.sender.last_name}"
                else:
                    transaction.other_user_account_number = transaction.recipient.bank_account_number
                    transaction.other_user_name = f"{transaction.recipient.first_name} {transaction.recipient.last_name}"

            return render_template('dashboard.html', user=user, transactions=transactions)
    
    return redirect('/login')




@app.route('/create_account')
def create_account():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            # Check if the edit parameter is present in the URL
            edit_mode = request.args.get('edit', False)
            if edit_mode:
                # Render the create account form in edit mode
                return render_template('create_account.html', editing=True, user=user)
            else:
                # Render the create account form in create mode
                return render_template('create_account.html', editing=False)
    # Redirect to login if not logged in or handle other cases

    return redirect('/login')


@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            bank_account = BankAccount.query.filter_by(user_id=user.id).first()
            if bank_account:
                if request.method == 'POST':
                    transaction_pin = request.form['transaction_pin']
                    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
                    if hashed_transaction_pin == bank_account.transaction_pin_hash:
                        return render_template('check_balance.html', balance=user.balance)
                    else:
                        error = "Incorrect transaction PIN. Please try again."
                        return render_template('check_balance.html', error=error)
                return render_template('check_balance.html')
    return redirect('/dashboard')


@app.route('/send_money', methods=['GET'])
def send_money_form():
    return render_template('send_money.html')

from flask import render_template

@app.route('/send_money', methods=['POST'])
def send_money():
    try:
        if 'email' in session:
            sender = User.query.filter_by(email=session['email']).first()
            if sender:
                sender_account = BankAccount.query.filter_by(user_id=sender.id).first()
                if sender_account:
                    transaction_pin = request.form['transaction_pin']
                    hashed_transaction_pin = hashlib.sha256(transaction_pin.encode()).hexdigest()
                    if hashed_transaction_pin == sender_account.transaction_pin_hash:
                        recipient_account_number = request.form['recipient_account_number']
                        
                        # Check if sender is trying to send money to their own account
                        if recipient_account_number == sender.bank_account_number:
                            flash('You cannot send money to your own account!', 'error')
                            return render_template('send_money.html')

                        amount = float(request.form['amount'])

                        recipient_user = User.query.filter_by(bank_account_number=recipient_account_number).first()
                        if recipient_user:
                            recipient_account = BankAccount.query.filter_by(user_id=recipient_user.id).first()
                            if recipient_account:
                                if sender.balance >= amount:
                                    sender.update_balance(-amount)
                                    recipient_user.update_balance(amount)

                                    # Create a transaction record for the sender
                                    sender_transaction = TransactionHistory(
                                        sender_id=sender.id,
                                        sender_account_number=sender.bank_account_number,
                                        recipient_id=recipient_user.id,
                                        recipient_account_number=recipient_account_number,
                                        amount=amount,
                                        transaction_type='sent'
                                    )
                                    db.session.add(sender_transaction)

                                    # Create a transaction record for the recipient
                                    recipient_transaction = TransactionHistory(
                                        sender_id=sender.id,
                                        sender_account_number=sender.bank_account_number,
                                        recipient_id=recipient_user.id,
                                        recipient_account_number=recipient_account_number,
                                        amount=amount,
                                        transaction_type='received'
                                    )
                                    db.session.add(recipient_transaction)

                                    # Commit the session to save the changes to the database
                                    db.session.commit()

                                    # Provide feedback to the user
                                    flash('Money sent successfully!', 'success')
                                    return render_template('send_money.html')
                                else:
                                    flash('Insufficient balance!', 'error')
                            else:
                                flash('Recipient bank account details not found.', 'error')
                        else:
                            flash('Recipient not found!', 'error')
                    else:
                        flash('Incorrect transaction PIN. Please try again.', 'error')
                else:
                    flash('Sender bank account details not found.', 'error')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        db.session.rollback()  # Rollback changes if an error occurs
    return render_template('send_money.html')


@app.route('/transaction_history')
def transaction_history():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            # Retrieve transactions where the logged-in user's bank account is either the sender or recipient
            transactions_sent = TransactionHistory.query.filter_by(sender_account_number=user.bank_account_number).filter_by(transaction_type='sent').all()
            transactions_received = TransactionHistory.query.filter_by(recipient_account_number=user.bank_account_number).filter_by(transaction_type='received').all()
            
            # Combine sent and received transactions
            transactions = transactions_sent + transactions_received
            
            # Sort transactions by timestamp in descending order
            transactions_sorted = sorted(transactions, key=lambda x: x.timestamp, reverse=True)
            
            return render_template('transaction_history.html', transactions=transactions_sorted)
    return redirect('/login')

@app.route('/emi_calculator')
def emi_calculator():
    return render_template('emi_calculator.html')


from flask import render_template

@app.route('/profile')
def profile():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            # Fetch the bank account information associated with the user
            user_bank_account = BankAccount.query.filter_by(user_id=user.id).first()
            return render_template('profile.html', user=user, user_bank_account=user_bank_account)
    return redirect('/login')




@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()
        # Render the template with the thank you message
        return render_template('contact.html', thank_you=True)
    # Render the template with the contact form
    return render_template('contact.html', thank_you=False)


@app.route('/loan_eligibility')
def loan_eligibility():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            # Retrieve loan applications for the user
            loan_applications = user.loan_applications
            if loan_applications:
                # Display loan applications if they exist
                return render_template('loan_eligibility.html', loan_applications=loan_applications)
            else:
                # If no loan applications exist, retrieve loans given to the user
                loans_given = LoanGiven.query.filter_by(user_id=user.id).all()
                return render_template('loan_eligibility.html', loans_given=loans_given)
        else:
            flash('User not found', 'error')
            return redirect('/login')
    else:
        flash('Please login to access this page', 'error')
        return redirect('/login')


@app.route('/loan_application', methods=['GET', 'POST'])
def loan_application():
    if request.method == 'POST':
        # Process loan application form submission
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        address = request.form.get('address')
        employer = request.form.get('employer')
        income = float(request.form.get('income', 0))
        loan_amount = float(request.form.get('loanAmount', 0))
        loan_duration = int(request.form.get('loanDuration', 0))
        loan_purpose = request.form.get('loanPurpose')
        id_photo = request.files.get('idPhoto')

        # Perform validation checks
        if not all([name, email, phone, dob, address, employer, income, loan_amount, loan_duration, loan_purpose, id_photo]):
            flash('All fields are required.', 'error')
            return redirect('/loan_application')

        # Retrieve the user based on the session email
        user = User.query.filter_by(email=session.get('email')).first()
        if not user:
            flash('User not found.', 'error')
            return redirect('/login')

        # Create a new LoanApplication instance associated with the retrieved user's id
        new_loan_application = LoanApplication(
            name=name,
            email=email,
            phone=phone,
            dob=dob,
            address=address,
            employer=employer,
            income=income,
            loan_amount=loan_amount,
            loan_duration=loan_duration,
            loan_purpose=loan_purpose,
            id_photo=id_photo.filename,  # Store filename for now, update this to file path
            user_id=user.id  # Set the user_id to the retrieved user's id
        )
        db.session.add(new_loan_application)
        db.session.commit()

        flash('Loan application submitted successfully!', 'success')
        return render_template('loan_application.html')  
    else:
        return render_template('loan_application.html')



@app.route('/about')
def about():
    return render_template('about_us.html')



@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        image_data = file.read()
        
        # Resize the image
        img = Image.open(BytesIO(image_data))
        img.thumbnail((300, 300))  # Adjust the size as needed
        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG')
        resized_image_data = output_buffer.getvalue()
        
        user = User.query.filter_by(email=session['email']).first()
        
        # Check if the user already has a profile picture
        if user.profile_picture:
            # Overwrite the existing profile picture with the new one
            user.save_profile_picture(resized_image_data)
        else:
            # Save the new picture as the profile picture
            user.save_profile_picture(resized_image_data)
        
        return redirect('/profile')
    else:
        return 'No picture uploaded'



@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        # If admin is not logged in, redirect to admin login page
        return redirect('/admin_login')
    
    # Fetch statistics from the database
    num_users = User.query.count()
    num_bank_accounts = BankAccount.query.count()
    num_contacts = ContactMessage.query.count()
    num_loan_applications = LoanApplication.query.count()
    total_bank_balance = db.session.query(db.func.sum(User.balance)).scalar()
    loans_given = db.session.query(db.func.count(LoanGiven.id)).scalar()
    regular_transactions_count = TransactionHistory.query.filter_by(transaction_type='sent').count()
    loan_given_transactions_count = LoanGiven.query.count()
    total_transactions = regular_transactions_count + loan_given_transactions_count
    total_admins = Admin.query.count() # Fetch total admins from the database

    admin_email = session.get('email')  # Assuming you store the admin's email in the session
    if admin_email == 'mdali.sheik1613@gmail.com':
        admin_name = 'Sheik Md Ali'
    else:
        admin = Admin.query.filter_by(email=admin_email).first()
        if admin:
            admin_name = admin.name
        else:
            admin_name = None


    # Render the admin dashboard template with the fetched statistics
    return render_template('admin/admin_dashboard.html', 
                           num_users=num_users,
                           num_bank_accounts=num_bank_accounts,
                           num_contacts=num_contacts,
                           num_loan_applications=num_loan_applications,
                           total_bank_balance=total_bank_balance,
                           loans_given=loans_given,
                           total_transactions=total_transactions,
                           total_admins=total_admins,
                           admin_name=admin_name)


@app.route('/admin/users')
def view_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/bank_accounts')
def bank_accounts():
    # Fetch users with bank accounts and their associated bank account details from the database
    users_with_bank_accounts = User.query.filter(User.bank_account_number.isnot(None)).all()
    
    # Render the bank accounts template with the fetched data
    return render_template('/admin/bank_accounts.html', users_with_bank_accounts=users_with_bank_accounts)

@app.route('/admin/contact_messages')
def contact_messages():
    # Fetch all contact messages from the database
    messages = ContactMessage.query.all()
    return render_template('/admin/contact_messages.html', messages=messages)


@app.route('/admin/loan_applications')
def view_loan_applications():
    loan_applications = LoanApplication.query.all()
    return render_template('admin/loan_applications.html', loan_applications=loan_applications)


# Route to approve a loan application
@app.route('/admin/approve_loan/<int:loan_id>', methods=['POST'])
def approve_loan(loan_id):
    loan_application = LoanApplication.query.get(loan_id)
    if loan_application:
        # Update loan status to approved
        loan_application.status = 'approved'
        db.session.commit()

        # Reduce bank balance by the loan amount
        bank = Bank.query.first()  # Assuming there's only one bank record
        if bank:
            bank.balance -= loan_application.loan_amount
            db.session.commit()

        # Add loan amount to user's balance
        user = loan_application.user
        user.balance += loan_application.loan_amount
        db.session.commit()

        # Create a record in the loans given table
        loan_given_date = datetime.now().date()  # Current date
        new_loan_given = LoanGiven(
            user_id=user.id,
            name=f"{user.first_name} {user.last_name}",
            account_number=user.bank_account_number,
            amount=loan_application.loan_amount,
            loan_duration=loan_application.loan_duration,
            date_given=loan_given_date
        )
        db.session.add(new_loan_given)
        db.session.commit()

        # Delete the loan application from the database
        db.session.delete(loan_application)
        db.session.commit()

        flash('Loan application approved successfully!', 'success')
    else:
        flash('Loan application not found!', 'error')
    return redirect('/admin/loan_applications')



# Route to reject a loan application
@app.route('/admin/reject_loan/<int:loan_id>', methods=['POST'])
def reject_loan(loan_id):
    loan_application = LoanApplication.query.get(loan_id)
    if loan_application:
        loan_application.status = 'rejected'
        db.session.commit()

        # Delete the rejected loan application from the database
        db.session.delete(loan_application)
        db.session.commit()

        flash('Loan application rejected!', 'success')
    else:
        flash('Loan application not found!', 'error')
    return redirect('/admin/loan_applications')


@app.route('/admin/loans_given')
def view_loans_given():
    loans_given = LoanGiven.query.order_by(desc(LoanGiven.id), desc(LoanGiven.date_given)).all()
    return render_template('admin/loans_given.html', loans_given=loans_given)



@app.route('/deduct_money/<int:loan_given_id>', methods=['POST'])
def deduct_money(loan_given_id):
    loan_given = LoanGiven.query.get(loan_given_id)
    if loan_given:
        # Check if loan period is expired
        if loan_given.loan_period_expired:
            # Get the user associated with the loan
            user = User.query.get(loan_given.user_id)
            if user:
                # Deduct money from the user's balance
                user.balance -= loan_given.amount
                db.session.commit()
                
                # Update the bank balance
                bank = Bank.query.first()  # Assuming there's only one bank record
                if bank:
                    bank.balance += loan_given.amount  # Deduct the amount back to bank
                    db.session.commit()
                
                flash('Money deducted successfully!', 'success')
            else:
                flash('User not found!', 'error')
        else:
            flash('Loan period has not expired yet!', 'error')
    else:
        flash('Loan given not found!', 'error')
    return redirect(url_for('view_loans_given'))



@app.route('/admin/bank_balance')
def total_bank_balance():
    # Retrieve the sum of user balances
    total_user_balance = db.session.query(db.func.sum(User.balance)).scalar()

    # Retrieve the bank balance from the database
    bank = Bank.query.first()  # Assuming there's only one bank record
    if bank:
        bank_balance = bank.balance
    else:
        # Set default bank balance if no record is found
        bank_balance = 0

    # Calculate the total bank balance
    total_bank_balance = bank_balance + total_user_balance

    # Retrieve all users
    users = User.query.all()

    # Render the template with the total bank balance, total user balance, and the list of users
    return render_template('admin/bank_balance.html', bank_balance=bank_balance, total_balance=total_bank_balance, user_balance=total_user_balance, users=users)



@app.route('/admin/transaction_history_admin')
def transaction_history_admin():
    # Query regular transactions ordered by timestamp
    regular_transactions = TransactionHistory.query.filter_by(transaction_type='sent').order_by(TransactionHistory.timestamp.desc()).all()

    # Query loan given transactions ordered by date given
    loan_transactions = LoanGiven.query.order_by(desc(LoanGiven.id), desc(LoanGiven.date_given)).all()

    return render_template('admin/transaction_history_admin.html', regular_transactions=regular_transactions, loan_transactions=loan_transactions)

@app.route('/admin/add_admin', methods=['GET', 'POST'])
def add_admin():
    # Check if admin is logged in and if the logged-in email is authorized
    if session.get('admin_logged_in') and session.get('email') == 'mdali.sheik1613@gmail.com':
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            # Create a new Admin instance
            admin = Admin(name=name, email=email)
            admin.set_password(password)

            # Add the admin to the database session and commit the transaction
            db.session.add(admin)
            db.session.commit()

            # Display a success message
            flash('Admin added successfully', 'success')

            # Redirect to the add_admin page to display the updated list of admins
            return redirect('/admin/add_admin')

        else:
            # If it's a GET request, fetch all admins from the database
            admins = Admin.query.all()

            # Render the add_admin.html template with the list of admins
            return render_template('/admin/add_admin.html', admins=admins)
    else:
        # If admin is not logged in or email is not authorized, redirect to admin dashboard
        flash('You are not authorized to access this page', 'error')
        return redirect('/admin_dashboard')    


@app.route('/admin/delete_admin', methods=['POST'])
def delete_admin():
    # Check if the admin is logged in
    if session.get('admin_logged_in'):
        # Check if the logged-in admin is authorized
        if session.get('email') == 'mdali.sheik1613@gmail.com':
            admin_id = request.form['admin_id']
            admin = Admin.query.get(admin_id)
            if admin:
                db.session.delete(admin)
                db.session.commit()
                flash('Admin deleted successfully', 'success')
            else:
                flash('Admin not found', 'error')
        else:
            flash('You are not authorized to perform this action', 'error')
    else:
        flash('You need to log in as an admin to perform this action', 'error')

    return redirect('/admin/add_admin') 
    
@app.route('/ourservices')
def about_bank():
    return render_template('ourservices.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('bank_account_number', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)
