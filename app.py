from flask import (Flask,
                   request)
from bson import (json_util)
from pymongo import MongoClient

from util import contained_in

app = Flask(__name__)
app.debug = True
mongo_client = MongoClient(
    'mongodb://recipeace-db:vMXgHpTl23Lvr7O3O1VMDeHQGF9H36W3L' +
    'rN8z4X3RObvd9gtD2sdiRLKhvWhRDrMfKU0e14jNL9sWhyLnZaoYQ==@' +
    'recipeace-db.mongo.cosmos.azure.com:10255/?ssl=true&repl' +
    'icaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&a' +
    'ppName=@recipeace-db@')
db = mongo_client.test  # Select the database
db.authenticate(
    name='recipeace-db',
    password='vMXgHpTl23Lvr7O3O1VMDeHQGF9H36W3LrN8z4X3RObvd9gtD2sdiRLKhvWhRDrMfKU0e14jNL9sWhyLnZaoYQ==')
recipes_collection = db['recipes']


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/recipes')
def search_recipes():
    ingredients = request.args['ingredients'].split(',')
    recipes_courser = recipes_collection.find()

    if len(ingredients) == 0:
        return json_util.dumps(recipes_courser)

    def matched_recipes(recipe):
        def _matched_ingredient(ingredient):
            return any(ingredient in recipe_ingredients
                       for recipe_ingredients in recipe['ingredients'].split())

        return any(_matched_ingredient(ingredient) for ingredient in ingredients)

    def add_match_score(recipe):
        recipe_ingredients = recipe['ingredients']

        matched_ingredients = filter(contained_in(ingredients), recipe_ingredients)

        return {
            **recipe,
            'match_score': len(list(matched_ingredients)) / float(len(recipe_ingredients))
        }

    return json_util.dumps(sorted((add_match_score(recipe) for recipe in filter(matched_recipes, recipes_courser)),
                                  key=lambda recipe: recipe.match_score,
                                  reverse=True))


if __name__ == '__main__':
    app.run()
