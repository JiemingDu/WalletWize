from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # allow your React dev server to call this API

# Keep the last posted payload in memory so a GET can display it
LAST_USER_INFO = None

@app.route("/user_info", methods=["GET", "POST", "OPTIONS"])
def user_info():
    global LAST_USER_INFO

    if request.method == "POST":
        # Try JSON body first (your React code sends this)
        data = request.get_json(silent=True)

        # If not JSON, accept form posts too (just in case)
        if not data and request.form:
            data = request.form.to_dict()

        # If still nothing, try raw body parse
        if not data and request.data:
            try:
                data = json.loads(request.data.decode("utf-8"))
            except Exception:
                data = None

        if not data:
            return jsonify({
                "error": "No data received. Send JSON with Content-Type: application/json."
            }), 400

        LAST_USER_INFO = {
            "data": data,
            "received_at": datetime.utcnow().isoformat() + "Z",
            "source": "POST"
        }
        print("Saved payload:", LAST_USER_INFO)
        return jsonify({"status": "ok", "received": data}), 200

    # GET — show last posted payload (so you can open the URL in a browser)
    if request.method == "GET":
        if LAST_USER_INFO:
            return jsonify({
                "message": "Last posted user info",
                **LAST_USER_INFO
            }), 200
        else:
            # If nothing has been posted yet, also show any query params (optional)
            qp = request.args.to_dict()
            return jsonify({
                "message": "No data posted yet. Submit the form in your React app.",
                "hint": "POST JSON to /user_info or add query params like ?name=Alice",
                "received_query_params": qp
            }), 200

    # OPTIONS preflight (CORS) — flask-cors covers this, but returning 204 is fine.
    return ("", 204)


# Optional: small helper to clear memory while testing
@app.route("/user_info/clear", methods=["POST"])
def clear_user_info():
    global LAST_USER_INFO
    LAST_USER_INFO = None
    return jsonify({"status": "cleared"}), 200


if __name__ == "__main__":
    # Run on 127.0.0.1:5000
    app.run(debug=True)





# from flask import Flask, jsonify, request
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app) # allow react to access


# @app.route('/user_info', methods=['GET','POST'])
# def get_data():
#     print("METHOD:", request.method)
#     print("HEADERS:", dict(request.headers))
#     print("RAW BODY:", request.get_data(as_text=True))
#     if request.method == 'POST':
#         print("IS JSON?:", request.is_json)
#         data = request.get_json()
#         print("PARSED JSON:", data)
#         if not data:
#             return jsonify({"error": "No JSON received"}), 400
#         return jsonify({"status": "success", "received": data})
#     else:  # GET
#         # Use query parameters for browser GET
#         data = request.args.to_dict()
#         print("QUERY PARAMS:", data)
        
#         # data = {
#         #     "name": data.get('name'),
#         #     "address": data.get('address'),
#         #     "school": data.get('school'),
#         #     "year": data.get('year'),
#         #     "program": data.get('program'),
#         #     "neighbourhood": data.get('neighbourhood'),
#         #     "housingType": data.get('housingType'),  # remove the trailing comma from your original code
#         #     "transport": data.get('transport'),
#         #     "eat_out": data.get('eat_out'),
#         #     "grocery_stores": data.get('grocery_stores'),
#         #     "grocery_budget": data.get('grocery_budget')
#         #     }
#         print(type(data))


#     #print(user_data.get('school'))
#     return jsonify({
#         "message": "User info received successfully!",
#         "received": data
#     }), 200

# # @app.route('/user_info', methods=['GET'])
# # def add_data():
# #     data = request.json
    
    
# #     return jsonify(data), 200

# if __name__ == '__main__':
#     app.run(debug=True)
    
