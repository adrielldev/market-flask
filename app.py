from market import app
from market import db


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True,host='0.0.0.0')