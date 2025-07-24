from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
import os
import openai
import sqlite3

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('interest'))
        else:
            return "<h3>Invalid credentials</h3>"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "<h3>Username already exists. Try another!</h3>"

        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contacts (name, email, phone, message)
        VALUES (?, ?, ?, ?)
    ''', (name, email, phone, message))
    conn.commit()
    conn.close()

    return render_template('contact_success.html', name=name)

@app.route('/interest', methods=['GET', 'POST'])
def interest():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_interest = request.form['interest']
        session['interest'] = selected_interest
        return redirect(url_for('dashboard'))

    return render_template('interest.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or 'interest' not in session:
        return redirect(url_for('login'))

    interest = session['interest']

    content = {
        'business': {
            'articles': [
                {'title': '5 Ways to Grow Your Business', 'url': 'https://hbr.org/2020/05/growth-strategies'},
                {'title': 'Leadership in Modern Business', 'url': 'https://www.forbes.com/sites/leadership/'}
            ],
            'videos': [
                {'title': 'Business Strategy Masterclass', 'url': 'https://www.youtube.com/watch?v=2ISD8BqV6Uo'},
                {'title': 'How to Build a Startup', 'url': 'https://www.youtube.com/watch?v=9kJVYpOqcVU'}
            ]
        },
        'finance': {
            'articles': [
                {'title': 'Personal Finance Basics', 'url': 'https://www.investopedia.com/personal-finance-4427765'},
                {'title': 'How to Save and Invest', 'url': 'https://www.nerdwallet.com/article/investing/how-to-invest-money'}
            ],
            'videos': [
                {'title': 'Money Management Tips', 'url': 'https://www.youtube.com/watch?v=wTijdv5_LBs'},
                {'title': 'Investing 101', 'url': 'https://www.youtube.com/watch?v=9o1_1M9llU8'}
            ]
        },
        'career': {
            'articles': [
                {'title': 'Career Planning Guide', 'url': 'https://www.themuse.com/advice/the-best-career-advice'},
                {'title': 'Resume & Interview Tips', 'url': 'https://zety.com/blog/resume-tips'}
            ],
            'videos': [
                {'title': 'Career Guidance Webinar', 'url': 'https://www.youtube.com/watch?v=bHbTtv3FfZo'},
                {'title': 'How to Choose the Right Career', 'url': 'https://www.youtube.com/watch?v=KqFNbCcyFkk'}
            ]
        },
        'it': {
            'articles': [
                {'title': 'Latest Trends in Tech', 'url': 'https://techcrunch.com'},
                {'title': 'Choosing the Right Stack', 'url': 'https://dev.to'}
            ],
            'videos': [
                {'title': 'How to Learn Programming', 'url': 'https://www.youtube.com/watch?v=8PopR3x-VMY'},
                {'title': 'Cybersecurity Essentials', 'url': 'https://www.youtube.com/watch?v=nb4fJjdf3Vk'}
            ]
        },
        'legal': {
            'articles': [
                {'title': 'Basics of Business Law', 'url': 'https://www.legalzoom.com/articles/what-is-business-law'},
                {'title': 'How to Protect IP', 'url': 'https://www.wipo.int/about-ip/en/'}
            ],
            'videos': [
                {'title': 'Understanding Legal Contracts', 'url': 'https://www.youtube.com/watch?v=sh_zKBoDZv0'},
                {'title': 'Startup Legal Advice', 'url': 'https://www.youtube.com/watch?v=2xdnB83DUe0'}
            ]
        },
        'marketing': {
            'articles': [
                {'title': 'Social Media Marketing Guide', 'url': 'https://blog.hootsuite.com/social-media-marketing-strategy/'},
                {'title': 'What is Branding?', 'url': 'https://www.investopedia.com/terms/b/branding.asp'}
            ],
            'videos': [
                {'title': 'Marketing Strategy Explained', 'url': 'https://www.youtube.com/watch?v=qux4lBzN5U8'},
                {'title': 'Branding for Beginners', 'url': 'https://www.youtube.com/watch?v=dkNfNR1WY4Q'}
            ]
        }
    }

    print(f"User: {session.get('user')}, Interest: {session.get('interest')}")
    data = content.get(interest, {'articles': [], 'videos': []})
    return render_template('dashboard.html', interest=interest, articles=data['articles'], videos=data['videos'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json['message'].lower()

    replies = {
        "business": {
            "text": "Explore strategic planning, leadership, and scaling tips for your business.",
            "video": "https://www.youtube.com/watch?v=2ISD8BqV6Uo"
        },
        "finance": {
            "text": "Understand personal finance, budgeting, and smart investments.",
            "video": "https://www.youtube.com/watch?v=9o1_1M9llU8"
        },
        "career": {
            "text": "Find clarity on your career path, resume tips, and interview guidance.",
            "video": "https://www.youtube.com/watch?v=bHbTtv3FfZo"
        },
        "it": {
            "text": "Keep up with tech trends, app/web development, and cybersecurity basics.",
            "video": "https://www.youtube.com/watch?v=8PopR3x-VMY"
        },
        "legal": {
            "text": "Learn about legal contracts, intellectual property, and business regulations.",
            "video": "https://www.youtube.com/watch?v=sh_zKBoDZv0"
        },
        "marketing": {
            "text": "Master branding, digital marketing strategies, and customer engagement.",
            "video": "https://www.youtube.com/watch?v=qux4lBzN5U8"
        }
    }

    reply = "I'm here to listen. Could you tell me more about your concern?"
    for keyword, response in replies.items():
        if keyword in user_msg:
            reply = f"{response['text']}<br><br>🎥 Suggested Video: <a href='{response['video']}' target='_blank'>Watch on YouTube</a>"
            break

    return jsonify({'reply': reply})


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
