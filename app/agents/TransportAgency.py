import random

from flask import Flask, jsonify, request

app = Flask(__name__)

delivery_guys = ["John Doe", "Jane Smith",
                 "Mike Johnson", "Anna Brown", "Chris Lee"]


@app.route('/')
def home():
    return "<h1>Bienvenido a la Agencia de Transporte</h1>"


@app.route('/GetOffer', methods=['POST'])
def get_offer():
    try:
        data = request.get_json()
        city = data['city']
        price = round(random.uniform(10, 100), 2)
        time_of_delivery = f"{random.randint(1, 7)} days"
        delivery_guy = random.choice(delivery_guys)
        offer = {
            "city": city,
            "price": price,
            "time_of_delivery": time_of_delivery,
            "delivery_guy": delivery_guy
        }

        print(f"Offer generated: {offer}")

        return jsonify(offer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5014)
