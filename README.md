# 🏦 Pioneer Bank – Digital Banking Simulator

A secure, full-stack **Flask + MySQL** web application simulating a real-world digital bank. Features include user registration, login, balance checking, money transfer, profile photo handling, and transaction history — all backed by a clean UI and secure backend.

---

## 📘 README.md

```markdown
# 🏦 Pioneer Bank – Flask-Based Digital Bank Simulator

A complete banking simulation system built with Flask and MySQL, ideal for educational or prototype-level digital finance applications.

---

## 🚀 Features

- 🔐 **Secure Authentication** using `bcrypt`
- 💳 **Transfer Funds** between registered users
- 📁 **Profile Picture Upload** (Base64 encoded and rendered)
- 📊 **Transaction History** with timestamps and filtering
- 🌐 **Responsive UI** with Flask & Jinja2 templates
- 🧠 **ORM Support** with SQLAlchemy
- 🔒 **Session Management** and flash-based notifications

---

## 🛠 Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2
- **Database:** MySQL (via PyMySQL)
- **Security:** bcrypt password hashing
- **Image Handling:** Pillow (PIL)

---

## 🗂 Directory Structure

```
pioneer-bank/
├── static/               # CSS, images, etc.
├── templates/            # Jinja2 HTML templates
├── app.py                # Main Flask app
├── requirements.txt      # Python dependencies
└── README.md             # Project overview
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sheik-md-ali/pioneer-bank.git
cd pioneer-bank
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup the MySQL Database

- Create a database named `pioneer_bank`
- Configure DB URI in `app.py` or `__init__.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/pioneer_bank'
```

### 5. Run the Flask App

```bash
flask run
```

> 🔗 Visit the app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Sample Test Data

You can register a new account directly from the frontend. All transfers are logged in the transaction table.

---

## 🙋‍♂️ Author

**Sheik Mohammed Ali M.**  
📧 mdali.sheik1613@gmail.com  
🌐 [GitHub](https://github.com/sheik-md-ali)

---

## 📜 License

MIT License – free to use, modify, and distribute.
```

