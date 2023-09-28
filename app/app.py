#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate

from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return '<h1>Initial page landing site</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_data = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes]
    return jsonify(hero_data)

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": [{"id": power.id, "name": power.name, "description": power.description} for power in hero.powers]
        }
        return jsonify(hero_data)
    else:
        return jsonify({"error": "Hero not found"}), 404

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    power_data = [{"id": power.id, "name": power.name, "description": power.description} for power in powers]
    return jsonify(power_data)

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power:
        power_data = {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        return jsonify(power_data)
    else:
        return jsonify({"error": "Power not found"}), 404

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if "description" in data:
        power.description = data["description"]
        db.session.commit()
        return jsonify({
            "id": power.id,
            "name": power.name,
            "description": power.description
        })
    else:
        return jsonify({"errors": ["validation errors"]}), 400

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Check if the required fields are present in the request
    if "strength" in data and "power_id" in data and "hero_id" in data:
        # Validate strength value
        valid_strengths = ['Strong', 'Weak', 'Average']
        if data["strength"] not in valid_strengths:
            return jsonify({"errors": ["validation errors"]}), 400

        # Check if Hero and Power exist
        hero = Hero.query.get(data["hero_id"])
        power = Power.query.get(data["power_id"])

        if not hero or not power:
            return jsonify({"errors": ["validation errors"]}), 400

        hero_power = HeroPower(strength=data["strength"], hero=hero, power=power)
        db.session.add(hero_power)
        db.session.commit()

        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": [{"id": p.id, "name": p.name, "description": p.description} for p in hero.powers]
        }
        return jsonify(hero_data), 201
    else:
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
