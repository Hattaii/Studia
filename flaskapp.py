from flask import Flask, Response, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import pymongo
import json
from bson.objectid import ObjectId
app = Flask(__name__)
jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = "super_mega_tajny_klucz"

try:
    mongo = pymongo.MongoClient(
        host="localhost",
        port=27017,
        serverSelectionTimeoutMS = 1000
    )
    db = mongo.signals
    mongo.server_info() # trigger exception if cannot connect to database
except:
    print("ERROR - nie łączy się do bazy")
#######################
@app.route("/users", methods=["GET"])
def get_some_users():
    try:
        data = list(db.users.find())
        for user in data:
            user['_id'] = str(user['_id'])

        return Response(
            response=json.dumps(data),
            status=500,
            mimetype='application/json'
        )
    except Exception as ex:
        print(ex)
        return Response(response=json.dumps({'message': 'cannot read users'}),status=500,mimetype='application/json')
####################### create user
@app.route("/signal_user", methods=["POST"])
def create_user():
    email = request.form["email"]
    test = db.users.find_one({"email": email})
    if test:
        return jsonify(message="User Already Exist"), 409
    else:
        name = request.form["name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        signals = []
        user_info = dict(name=name, last_name=last_name, email=email, password=password,signals=signals)
        db.users.insert_one(user_info)
        return jsonify(message="User added sucessfully"), 201
####################### stop.... login time!
@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]

    test = db.users.find_one({"email": email, "password": password})
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token), 201
    else:
        return jsonify(message="Bad Email or Password"), 401
####################### zdobycie danych z tokenu
@app.route("/details", methods=["GET"])
@jwt_required()
def details():
    current_user = get_jwt_identity()
    detail = db.users.find({"email":current_user})
    for result in detail:
        res1=result["name"]
        res2=result["last_name"]
        res3 = result["signals"]
    return jsonify(name=res1,last_name=res2,signals=res3), 200

####################### KOPIA NIEPOTRZEBNE DO INZYNIERKI
@app.route("/signall", methods=["POST"])
def create_user11():
    try:
      user = {"mail":request.form["mail"],
              "password": request.form["password"],
              "name":request.form["name"],
              "lastName":request.form["lastName"]}
      dbResponse = db.users.insert_one(user)
      print(dbResponse.inserted_id)
      #for attr in dir(dbResponse):
      #    print(attr)
      return Response(
          response= json.dumps(
            {'message':'user created',
            'id':f'{dbResponse.inserted_id}'
            }
          ),
          status=200,
          mimetype='application/json'
      )
    except Exception as ex:
        print("**********")
        print(ex)
        print("**********")
#######################update za pomoca post - NIEPOTRZEBNE DO INZYNIERKI
@app.route("/add_signal", methods=["POST"])
def add_signal():
    token_post = request.form["token"]
    x = "Bearer " + token_post
    hmm_decode = decode_token(x)
    print(hmm_decode)
    #token_post = request.form["token"]
    #signal_name = request.form["signal_name"]
    #signal = request.form["signal"]
    #test = db.users.find_one({"email": email})

    #if test:
    #    return jsonify(message="User Already Exist"), 409
    #else:
    #    name = request.form["name"]
    #    last_name = request.form["last_name"]
    #    password = request.form["password"]
    #   signals = []
    #    user_info = dict(name=name, last_name=last_name, email=email, password=password,signals=signals)
    #    db.users.insert_one(user_info)
#    return jsonify(message="User added sucessfully"), 201
####################### NIEPOTRZEBNE DO INZYNIERKI
@app.route("/users/<id>", methods=["PATCH"])
def update_user(id):
    try:
        dbResponse = db.users.update_one(
            {'_id':ObjectId(id)},
            {'$set':{'name':request.form['name']}}

        )
        if dbResponse.modified_count == 1:
            return Response(
                response=json.dumps(
                    {'message': 'user updated'}),
                status=200,
                mimetype='application/json'
            )
        else:
            return Response(
                response=json.dumps(
                    {'message': 'nothing to update'}),
                status=200,
                mimetype='application/json'
            )

    except Exception as ex:
        print("********")
        print(ex)
        print("********")
        return Response(
            response=json.dumps(
                {'message': 'cant update'}),
            status=500,
            mimetype='application/json'
        )
####################### NIEPOTRZEBNE DO INZYNIERKI
@app.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        dbResponse = db.users.delete_one({'_id':ObjectId(id)})
        if dbResponse.deleted_count == 1:
            return Response(
                response=json.dumps(
                    {'message': 'user deleted', 'id': f'{id}'}),
                status=200,
                mimetype='application/json'
            )
        return Response(
            response=json.dumps(
                {'message': 'user not found', 'id': f'{id}'}),
            status=200,
            mimetype='application/json'
        )
    except Exception as ex:
        print("********")
        print(ex)
        print("**********")
        return Response(
            response=json.dumps(
                {'message': 'cant delete user'}),
            status=500,
            mimetype='application/json'
        )
#######################

if __name__ == "__main__":
    app.run(port=80, debug=True)