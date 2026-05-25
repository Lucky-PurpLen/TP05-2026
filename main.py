import json
import os

data_file = "data.json"

def load_recipes():
    if not os.path.exists(data_file):
        return []

    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data

def save_recipes(data):
    with open(data_file,"w",encoding="utf-8") as file:
        json.dump(data,file,ensure_ascii=False, indent=4)

if __name__ == "__main__":
    my_recipes = load_recipes()
    print(f"Загружено рецептов: {len(my_recipes)}")

    for recipe in my_recipes:
        print("-", recipe["title"])

    new_recipe = {
        "title": "Жареная картошка",
        "category": "Овощи и зелень",
        "ingredients": ["картофель", "подсолнечное масло", "соль", "укроп"],
        "time_minutes": 25,
        "instructions": "Нарежьте картофель и пожарьте на масле.",
        "image_path": "images/potato.jpg"
    }

    my_recipes.append(new_recipe)
    save_recipes(my_recipes)
    print("\nНовый рецепт успешно добавлен и сохранен в data.json!")