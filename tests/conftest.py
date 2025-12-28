import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configure l'application Flask pour les tests
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


