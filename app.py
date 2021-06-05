from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests


app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'f576jbfiv7t47bu4787t7d36cx43wfvh457vtrwddfgtyscw67681'

db = SQLAlchemy(app)

class City(db.Model):
	id = db.Column(db.Integer , primary_key= True)
	name = db.Column(db.String(60), nullable= False)


def get_weather(city):

	url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=90b5d4cec0fad19659d43a454b81df52"
	r = requests.get(url.format(city)).json()
	return r



@app.route('/', methods=['GET', 'POST'])
def index():

	err_msg = ""

	if request.method == 'POST':
		name = request.form.get('city')
		if name:
			exist_city = City.query.filter_by(name = name).first()

			if not exist_city:
				new_city_data = get_weather(name)

				if new_city_data['cod'] == 200:
					db.session.add(City(name=name))
					db.session.commit()
				else:
					err_msg = 'City does not exist!'
			else:
				err_msg = 'City already exist!'
		if err_msg:
			flash(err_msg, 'error')
		else:
			flash("City added successfully!")

	cities = City.query.all()

	# url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=90b5d4cec0fad19659d43a454b81df52"
	# city = 'Delhi'

	weather_data=[]

	for city in cities:

		# r = requests.get(url.format(city.name)).json()
		# print(r)
		r = get_weather(city.name)

		weather = {
			'city': city.name,
			'temperature': r['main']['temp'],
			'description': r['weather'][0]['description'],
			'icon':r['weather'][0]['icon']
		}

		weather_data.append(weather)
		# print(weather)


	return render_template('weather.html', weather_data= weather_data)


@app.route('/delete/<name>')
def delete_city(name):
	city = City.query.filter_by(name = name).first()
	db.session.delete(city)
	db.session.commit()

	flash(f"Successfully deleted {city.name}")

	return redirect( url_for('index') )