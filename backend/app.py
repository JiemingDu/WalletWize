from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # allow react to access


@app.route('/user_info', methods=['GET','POST'])
def get_data():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON received"}), 400
    else:  # GET
        # Use query parameters for browser GET
        data = request.args.to_dict()

    user_data = {
    "name": data.get('name'),
    "address": data.get('address'),
    "school": data.get('school'),
    "year": data.get('year'),
    "program": data.get('program'),
    "neighbourhood": data.get('neighbourhood'),
    "housingType": data.get('housingType'),  # remove the trailing comma from your original code
    "transport": data.get('transport'),
    "eat_out": data.get('eat_out'),
    "grocery_stores": data.get('grocery_stores'),
    "grocery_budget": data.get('grocery_budget')
    }
    print(user_data.get('school'))
    return jsonify({
        "message": "User info received successfully!",
        "received": user_data
    }), 200

# @app.route('/user_info', methods=['GET'])
# def add_data():
#     data = request.json
    
    
#     return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
    
