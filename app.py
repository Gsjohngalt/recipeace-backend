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
users = db['users']

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/recipes')
def search_recipes():
    tags = request.args.get('tags', None)
    ingredients = request.args.get('ingredients', None)
    
    if tags:
        tags = tags.split(',')
        recipes_courser = recipes_collection.find({"tags" : {"$all": tags}})        
    else:
        recipes_courser = recipes_collection.find()
        
    if not ingredients:
        return json_util.dumps(recipes_courser)
    ingredients = ingredients.split(',')
    
    def matched_recipes(recipe):
            def _matched_ingredient(ingredient):
                return any(ingredient in recipe_ingredients
                       for recipe_ingredients in recipe['ingredients'])
            return any(_matched_ingredient(ingredient) for ingredient in ingredients)

    def add_match_score(recipe):
        recipe_ingredients = recipe['ingredients']

        matched_ingredients = filter(contained_in(ingredients), recipe_ingredients)

        return {
            **recipe,
            'match_score': len(list(matched_ingredients)) / float(len(recipe_ingredients))
        }

    return json_util.dumps(sorted((add_match_score(recipe) for recipe in filter(matched_recipes, recipes_courser)),
                                  key=lambda recipe: recipe.get('match_score'),
                                  reverse=True))


@app.route('/users/<username>/pantry')
def get_pantry(username):
    user_pantry = users.find({"name": username })
    return json_util.dumps(user_pantry)

@app.route('/users/<username>/pantry', methods=['POST'])
def add_pantry(username):
    new_item = request.get_json().get("new_item")
    update_status = users.update({"name": username}, {"$push": {"pantry": new_item}}, upsert=True)
    return json_util.dumps(update_status)
    
if __name__ == '__main__':
    app.run()
