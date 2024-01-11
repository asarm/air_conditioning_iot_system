from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///device.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy instance
db = SQLAlchemy(app)

# Define a simple model
class StationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(80), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<{self.time}> {round(self.temperature, 3)} & {round(self.humidity, 3)}'

# Create the database tables
with app.app_context():
    db.create_all()

# Route to display data
@app.route('/get', methods=['GET'])
def get_data():
    with app.app_context():
        all_data = StationData.query.all()

    data_list = [{'id': data.id, 'time': data.time, 'temp': data.temperature, 'hum': data.humidity} for data in all_data]

    return jsonify(data=data_list)

@app.route('/add', methods=['POST'])
def add_record():
    data = request.get_json()
    print("Data come:", data)
    time = data["time"]
    temp = data["Temperature"]
    hum = data["Humidity"]

    record = StationData(time=time, temperature=temp, humidity=hum)
    with app.app_context():
        db.session.add(record)
        db.session.commit()

    return jsonify(message= "success!")

if __name__ == '__main__':
    app.run(debug=True)
