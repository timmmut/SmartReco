from flask import Flask, render_template, request, redirect, url_for, session
from models import User, Preferences, Rating
import json

app = Flask(__name__)
app.secret_key = 'simple_secret_key_123'

@app.route('/')
def index():
    if 'user_email' in session:
        prefs = Preferences.get_by_email(session['user_email'])
        if not prefs:
            return redirect(url_for('preferences'))
        return render_template('home.html', email=session['user_email'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.authenticate(email, password)
        if user:
            session['user_email'] = user.email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Wrong email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.find_by_email(email):
            return render_template('register.html', error='User already exists')
        
        user = User(email, password)
        user.save()
        session['user_email'] = user.email
        return redirect(url_for('preferences'))
    
    return render_template('register.html')

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        countries = request.form.getlist('countries')
        genres = request.form.getlist('genres')
        year_from = request.form.get('year_from')
        year_to = request.form.get('year_to')
        
        prefs = Preferences(session['user_email'], countries, genres, year_from, year_to)
        prefs.save()
        return redirect(url_for('index'))
    
    return render_template('preferences.html')

@app.route('/movies')
def movies():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    with open('movies.json', 'r', encoding='utf-8') as f:
        movies_list = json.load(f)
    
    user_ratings = Rating.get_user_ratings(session['user_email'])
    
    return render_template('movies.html', movies=movies_list, user_ratings=user_ratings)

@app.route('/rate', methods=['POST'])
def rate():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    movie_id = request.form.get('movie_id')
    rating_value = request.form.get('rating')
    
    rating = Rating(session['user_email'], movie_id, int(rating_value))
    rating.save()
    
    return redirect(url_for('movies'))

@app.route('/criteria-recommendation', methods=['GET', 'POST'])
def criteria_recommendation():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        countries = request.form.getlist('countries')
        genres = request.form.getlist('genres')
        year_from = request.form.get('year_from')
        year_to = request.form.get('year_to')
        
        with open('movies.json', 'r', encoding='utf-8') as f:
            all_movies = json.load(f)
        
        recommended = []
        for movie in all_movies:
            match = True
            if countries and movie['country'] not in countries:
                match = False
            if genres and movie['genre'] not in genres:
                match = False
            if year_from and movie['year'] < int(year_from):
                match = False
            if year_to and movie['year'] > int(year_to):
                match = False
            if match:
                recommended.append(movie)
        
        return render_template('recommendations.html', movies=recommended, rec_type='Criteria')
    
    return render_template('criteria.html')

@app.route('/ai-recommendation')
def ai_recommendation():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return "Coming soon"

@app.route('/personal-recommendation')
def personal_recommendation():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    prefs = Preferences.get_by_email(session['user_email'])
    if not prefs:
        return redirect(url_for('preferences'))
    
    with open('movies.json', 'r', encoding='utf-8') as f:
        all_movies = json.load(f)
    
    recommended = []
    for movie in all_movies:
        if movie['country'] in prefs.countries:
            if movie['genre'] in prefs.genres:
                if int(prefs.year_from) <= movie['year'] <= int(prefs.year_to):
                    recommended.append(movie)
    
    return render_template('recommendations.html', movies=recommended, rec_type='Personal')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

