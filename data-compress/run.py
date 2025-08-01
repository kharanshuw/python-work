from app import create_app
from extensions import db
from flask import jsonify
from exception import CustomException

app = create_app()


with app.app_context():
    db.create_all()


@app.errorhandler(CustomException)
def handle_custom_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    app.run(debug=False, port=5000)
