from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import cfg
from flask.cli import with_appcontext
from click import command, echo
import os



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =cfg.MYSQL_DB_RESOURCE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SECRET_KEY'] = cfg.SECRET_KEY


db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import *
from routes import *

@command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.session.flush()
    if os.path.exists(cfg.DB_FILE):
        os.remove(cfg.DB_FILE)
        print("Database Removed")
    db.create_all()
    echo("Initialized the database.")
app.cli.add_command(init_db_command)

if __name__ == '__main__':
    app.run()
