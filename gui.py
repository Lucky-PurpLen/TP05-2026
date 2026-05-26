import tkinter as tk
from tkinter import messagebox
from main import load_recipes

def create_app():
    root = tk.Tk()
    root.title("Что приготовить?")
    root.geometry("1280x720")
    root.resizable(False,False)

    all_recipes = load_recipes()

    left_panel = tk.Frame(root, width=320, bg="#f0f0f0", relief="sunken", borderwidth=1)
    left_panel.pack(side="left", fill="y")
    left_panel.pack_propagate(False)

    bottom_panel = tk.Frame(root, height=80,bg="#e0e0e0", relief="raised",borderwidth=1)
    bottom_panel.pack(side="bottom", fill="x")
    bottom_panel.pack_propagate(False)

    central_panel = tk.Frame(root, bg="#ffffff")
    central_panel.pack(side="left",expand=True,fill="both")

    tk.Label(left_panel, text="Категории", bg="#f0f0f0", font=("Arial", 14, "bold")).pack(pady=15)
    categories = [
        "Мясо и птица", "Рыба и морепродукты", "Овощи и зелень",
        "Сыры и яйца", "Молочные продукты", "Крупы и макароны",
        "Фрукты и ягоды", "Грибы", "Орехи и бобовые",
        "Специи и травы", "Соусы и масла", "Хлебобулочные", "Разное"
    ]
    for cat in categories:
        btn = tk.Button(left_panel, text=cat, font=("Arial",11), bg="#e0e0e0", anchor="w", relief="flat", command=lambda c=cat: update_grid(c))
        btn.pack(fill="x",padx=10,pady=2)

    lbl_category_title = tk.Label(central_panel, text="Ингредиенты: Мясо и птица", bg="#ffffff", font=("Arial", 16, "bold"))
    lbl_category_title.pack(pady=20)
    grid_frame = tk.Frame(central_panel, bg="#ffffff")
    grid_frame.pack(fill="both", expand=True, padx=40)

    def get_ingredients_by_category(category_name):
        ingredients_set = set()

        for recipe in all_recipes:
            if category_name in recipe["ingredients"]:
                ingredients_set.update(recipe["ingredients"][category_name])
        return sorted(list(ingredients_set))

    ingredient_vars = {}
    def update_counter():
        count = sum(1 for var in ingredient_vars.values() if var.get() == 1)
        lbl_counter.config(text=f"Выбрано ингредиентов: {count}")

    def find_recipes():
        selected_ingredients = [ing for ing, var in ingredient_vars.items() if var.get() == 1]

        if not selected_ingredients:
            messagebox.showinfo("Внимание", "Пожалуйста, выберите хотя бы один продукт!")
            return

        found_recipes = []

        for recipe in all_recipes:
            recipe_ingredients = []
            for cat_ings in recipe["ingredients"].values():
                recipe_ingredients.extend(cat_ings)

            if set(recipe_ingredients).issubset(set(selected_ingredients)):
                found_recipes.append(recipe["title"])

        if found_recipes:
            result_text = "\n".join(found_recipes)
            messagebox.showinfo("Найденные рецепты:", result_text)
        else:
            messagebox.showinfo("Нет совпадений", "Из этих продуктов не получится собрать полный рецепт. \nДобавьте еще ингредиентов!")

    current_category = categories[0]
    ingredients_to_show = get_ingredients_by_category(current_category)

    def update_grid(category_name):
        lbl_category_title.config(text=f"Ингредиенты: {category_name}")

        for widget in grid_frame.winfo_children():
            widget.destroy()

        ingredients = get_ingredients_by_category(category_name)

        row_num = 0
        col_num = 0
        for ingredient in ingredients:
            if ingredient not in ingredient_vars:
                ingredient_vars[ingredient] = tk.IntVar()

            var = ingredient_vars[ingredient]

            chk = tk.Checkbutton(grid_frame, text=ingredient, variable=var, bg="#ffffff", font=("Arial", 11), command=update_counter)
            chk.grid(row=row_num, column=col_num, padx=15, pady=10, sticky="w")

            col_num += 1
            if col_num > 2:
                col_num = 0
                row_num += 1

    lbl_counter = tk.Label(bottom_panel, text="Выбрано ингредиентов: 0", bg="#e0e0e0", font=("Arial", 12, "bold"))
    lbl_counter.pack(side="left", padx=20)
    btn_search = tk.Button(bottom_panel, text="Найти рецепты", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=15, command=find_recipes)
    btn_search.pack(side="right", padx=20)

    update_grid(categories[0])
    root.mainloop()

if __name__ == "__main__":
    create_app()