import os
import json

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def save(self):
        with open('users.txt', 'a', encoding='utf-8') as f:
            f.write(f"{self.email}:{self.password}\n")
    
    @staticmethod
    def find_by_email(email):
        if not os.path.exists('users.txt'):
            return None
        
        with open('users.txt', 'r', encoding='utf-8') as f:
            for line in f:
                user_email, user_password = line.strip().split(':')
                if user_email == email:
                    return User(user_email, user_password)
        return None
    
    @staticmethod
    def authenticate(email, password):
        user = User.find_by_email(email)
        if user and user.password == password:
            return user
        return None

class Preferences:
    def __init__(self, email, countries, genres, year_from, year_to):
        self.email = email
        self.countries = countries
        self.genres = genres
        self.year_from = year_from
        self.year_to = year_to
    
    def save(self):
        prefs = self.load_all()
        prefs[self.email] = {
            'countries': self.countries,
            'genres': self.genres,
            'year_from': self.year_from,
            'year_to': self.year_to
        }
        with open('preferences.txt', 'w', encoding='utf-8') as f:
            json.dump(prefs, f)
    
    @staticmethod
    def load_all():
        if not os.path.exists('preferences.txt'):
            return {}
        with open('preferences.txt', 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    
    @staticmethod
    def get_by_email(email):
        prefs = Preferences.load_all()
        if email in prefs:
            data = prefs[email]
            return Preferences(email, data['countries'], data['genres'], data['year_from'], data['year_to'])
        return None

class Rating:
    def __init__(self, email, movie_id, rating):
        self.email = email
        self.movie_id = movie_id
        self.rating = rating
    
    def save(self):
        ratings = Rating.load_all()
        key = f"{self.email}:{self.movie_id}"
        ratings[key] = self.rating
        with open('ratings.txt', 'w', encoding='utf-8') as f:
            json.dump(ratings, f)
    
    @staticmethod
    def load_all():
        if not os.path.exists('ratings.txt'):
            return {}
        with open('ratings.txt', 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    
    @staticmethod
    def get_user_rating(email, movie_id):
        ratings = Rating.load_all()
        key = f"{email}:{movie_id}"
        return ratings.get(key, 0)
    
    @staticmethod
    def get_user_ratings(email):
        ratings = Rating.load_all()
        user_ratings = {}
        for key, value in ratings.items():
            if key.startswith(f"{email}:"):
                movie_id = key.split(':')[1]
                user_ratings[int(movie_id)] = value
        return user_ratings

