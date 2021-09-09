import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    drink = Drink(
        title='ماء',
        recipe='[{"name": "water", "color": "#d4f1f9", "parts": 1}]'
    )
    drink.insert()
    drink = Drink(
        title='شاي أخضر',
        recipe='[{"name": "milk", "color": "#addfad", "parts": 1},{"name": "matcha", "color": "#69bf64", "parts": 2}]'
    )
    drink.insert()
    drink = Drink(
        title='فلات-وايت',
        recipe='[{"name": "milk", "color": "#eae0c8", "parts": 1},{"name": "coffee", "color": "#654321", "parts": 2}]'
    )
    drink.insert()
    drink = Drink(
        title='كابتشينو',
        recipe='[{"name": "foam", "color": "#eae0c8", "parts": 1},{"name": "milk", "color": "#f8f8ff", "parts": 2},{"name": "coffee", "color": "#654321", "parts": 1}]'
    )
    drink.insert()
    drink = Drink(
        title='اميريكانو',
        recipe='[{"name": "Coffee", "color": "#81613c", "parts": 1},{"name": "Water", "color": "#6b4423", "parts": 2},{"name": "Water", "color": "#654321", "parts": 1}]'
    )
    drink.insert()
    drink = Drink(
        title='عصير برتقال',
        recipe='[{"name": "foam", "color": "#ffbf00", "parts": 1},{"name": "Orange", "color": "#ffb347", "parts": 2},{"name": "Orange", "color": "#ffb347", "parts": 1}]'
    )
    drink.insert()

    drink = Drink(
        title='قهوة عربية',
        recipe='[{"name": "Coffee", "color": "#967117", "parts": 1}]'
    )
    drink.insert()

# ROUTES

'''
Drink
a persistent drink entity, extends the base SQLAlchemy Model
'''


class Drink(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe = Column(String(180), nullable=False)

    '''
    short()
        short form representation of the Drink model
    '''

    def short(self):
        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    '''
    long()
        long form representation of the Drink model
    '''

    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''

    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
