import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from main import load_recipes
import json
from PIL import Image, ImageTk

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
                for ing in recipe["ingredients"][category_name]:
                    ingredients_set.add(ing["name"])
        return sorted(list(ingredients_set))

    ingredient_vars = {}
    def update_counter():
        count = sum(1 for var in ingredient_vars.values() if var.get() == 1)
        lbl_counter.config(text=f"Выбрано ингредиентов: {count}")

    # Функция для сброса всех выбранных ингредиентов
    def reset_all():
        # Пробегаемся по всем переменным в нашей "памяти" и устанавливаем их в 0 (снимаем галочку)
        for var in ingredient_vars.values():
            var.set(0)

        # Принудительно вызываем обновление счетчика на экране
        update_counter()

    # Функция для отрисовки окна с результатами и калькулятором
    def show_results_window(recipes):
        top = tk.Toplevel(root)
        top.title("Найденные рецепты")
        top.geometry("650x650") # Сделали окно чуть выше
        top.configure(bg="#f4f4f4")

        control_frame = tk.Frame(top, bg="#f4f4f4")
        control_frame.pack(pady=15, fill="x", padx=20)

        lbl_portions = tk.Label(control_frame, text="Количество порций:", font=("Arial", 12, "bold"), bg="#f4f4f4")
        lbl_portions.pack(side="left")

        portion_var = tk.StringVar(value="1")

        txt_result = tk.Text(top, font=("Arial", 12), wrap="word", bg="#ffffff", padx=15, pady=15)
        txt_result.pack(expand=True, fill="both", padx=20, pady=10)

        # Настраиваем визуальные стили, добавили оранжевый для предупреждений
        txt_result.tag_config("header", font=("Arial", 14, "bold"), foreground="#4CAF50")
        txt_result.tag_config("bold", font=("Arial", 12, "bold"))
        txt_result.tag_config("warning", font=("Arial", 11, "bold"), foreground="#E65100") # Темно-оранжевый
        txt_result.tag_config("warning_text", font=("Arial", 11, "italic"), foreground="#E65100")

        def render_recipes(*args):
            txt_result.config(state="normal")
            txt_result.delete("1.0", tk.END)

            # ВАЖНО: Создаем список для хранения ссылок на картинки,
            # чтобы сборщик мусора Python их не удалил
            txt_result.image_list = []

            try:
                multiplier = int(portion_var.get())
                if multiplier < 1: multiplier = 1
            except Exception:
                multiplier = 1

            for r in recipes:
                # 1. Заголовок
                txt_result.insert(tk.END, f"🍳 {r['title']}\n", "header")

                # --- НОВЫЙ БЛОК: ДОБАВЛЕНИЕ КАРТИНКИ ---
                img_path = r.get("image", "")
                if img_path: # Если путь к картинке указан в JSON
                    try:
                        # Открываем картинку
                        img = Image.open(img_path)
                        # Пропорционально сжимаем её, чтобы она не была огромной (максимум 300x300 пикселей)
                        img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                        # Преобразуем в формат, понятный Tkinter
                        photo = ImageTk.PhotoImage(img)
                        txt_result.image_list.append(photo) # Сохраняем от удаления

                        # Вставляем картинку прямо в текстовое поле
                        txt_result.image_create(tk.END, image=photo)
                        txt_result.insert(tk.END, "\n\n")
                    except Exception as e:
                        print(f"Ошибка загрузки картинки {img_path}: {e}")
                # ----------------------------------------

                # 2. Умный поиск: Вывод подсказки о покупках
                missing = r.get("missing_details", [])
                if missing:
                    txt_result.insert(tk.END, "⚠️ Почти готово! Осталось докупить:\n", "warning")
                    for m in missing:
                        calc_m = round(m['amount'] * multiplier, 1)
                        if calc_m == int(calc_m): calc_m = int(calc_m)
                        txt_result.insert(tk.END, f"  • {m['name']} — {calc_m} {m['unit']}\n", "warning_text")
                    txt_result.insert(tk.END, "\n")

                # 3. Основные ингредиенты
                txt_result.insert(tk.END, "Что понадобится (всего):\n", "bold")
                for cat_name, items in r["ingredients"].items():
                    for item in items:
                        calc_amount = round(item['amount'] * multiplier, 1)
                        if calc_amount == int(calc_amount):
                            calc_amount = int(calc_amount)
                        txt_result.insert(tk.END, f" • {item['name']}: {calc_amount} {item['unit']}\n")

                # 4. Инструкция
                txt_result.insert(tk.END, f"\nКак готовить:\n{r['instructions']}\n")
                txt_result.insert(tk.END, "-"*40 + "\n\n")

            txt_result.config(state="disabled")

        spin_portions = tk.Spinbox(control_frame, from_=1, to=20, textvariable=portion_var, font=("Arial", 12), width=5)
        spin_portions.pack(side="left", padx=10)

        portion_var.trace_add("write", render_recipes)
        render_recipes()

    def open_add_recipe_window():
        add_win = tk.Toplevel(root)
        add_win.title("Добавить новый рецепт")
        add_win.geometry("550x650")
        add_win.configure(bg="#f4f4f4")
        add_win.grab_set() # Блокирует основное окно, пока открыто это

        # --- Поля ввода основных данных ---
        tk.Label(add_win, text="Название блюда:", font=("Arial", 11, "bold"), bg="#f4f4f4").pack(anchor="w", padx=20, pady=(15, 2))
        ent_title = tk.Entry(add_win, font=("Arial", 11), width=50)
        ent_title.pack(padx=20, fill="x")

        # --- Секция добавления ингредиентов ---
        ing_frame = tk.LabelFrame(add_win, text=" Добавление ингредиента ", font=("Arial", 10, "bold"), bg="#f4f4f4", padx=10, pady=10)
        ing_frame.pack(padx=20, pady=15, fill="x")

        tk.Label(ing_frame, text="Категория:", bg="#f4f4f4").grid(row=0, column=0, sticky="w")
        cb_category = ttk.Combobox(ing_frame, values=categories, state="readonly", width=18)
        cb_category.grid(row=1, column=0, padx=(0, 5))
        cb_category.current(0)

        tk.Label(ing_frame, text="Название:", bg="#f4f4f4").grid(row=0, column=1, sticky="w")
        cb_ing_name = ttk.Combobox(ing_frame, width=15)
        cb_ing_name.grid(row=1, column=1, padx=5)

        tk.Label(ing_frame, text="Кол-во:", bg="#f4f4f4").grid(row=0, column=2, sticky="w")
        ent_ing_amount = tk.Entry(ing_frame, width=7)
        ent_ing_amount.grid(row=1, column=2, padx=5)

        tk.Label(ing_frame, text="Ед. изм.:", bg="#f4f4f4").grid(row=0, column=3, sticky="w")
        ent_ing_unit = tk.Entry(ing_frame, width=6)
        ent_ing_unit.grid(row=1, column=3, padx=5)

        # --- НОВАЯ ЛОГИКА АВТОЗАПОЛНЕНИЯ ---
        # Словарь для хранения связок "Имя продукта" -> "Его единица измерения"
        known_units = {}

        def update_ingredient_names(event=None):
            cat = cb_category.get()
            known_units.clear() # Очищаем словарь при смене категории
            if cat:
                # Пробегаемся по базе и собираем не только имена, но и единицы измерения
                for recipe in all_recipes:
                    if cat in recipe.get("ingredients", {}):
                        for ing in recipe["ingredients"][cat]:
                            known_units[ing["name"]] = ing["unit"]

                # Заполняем выпадающий список только именами
                cb_ing_name.config(values=sorted(list(known_units.keys())))
                cb_ing_name.set('')
                ent_ing_unit.delete(0, tk.END) # Очищаем старую единицу измерения

        def autofill_unit(event=None):
            # Получаем текущее введенное или выбранное имя
            name = cb_ing_name.get().strip()
            # Если это имя уже есть в нашей базе, автоматически подставляем единицу
            if name in known_units:
                ent_ing_unit.delete(0, tk.END)
                ent_ing_unit.insert(0, known_units[name])

        # Привязываем события
        cb_category.bind("<<ComboboxSelected>>", update_ingredient_names)

        # Автозаполнение срабатывает при выборе из списка (ComboboxSelected)
        # или когда пользователь кликает в другое поле (FocusOut)
        cb_ing_name.bind("<<ComboboxSelected>>", autofill_unit)
        cb_ing_name.bind("<FocusOut>", autofill_unit)

        # Инициализация при открытии окна
        cb_category.current(0)
        update_ingredient_names()

        tk.Label(ing_frame, text="Кол-во:", bg="#f4f4f4").grid(row=0, column=2, sticky="w")
        ent_ing_amount = tk.Entry(ing_frame, width=7)
        ent_ing_amount.grid(row=1, column=2, padx=5)

        tk.Label(ing_frame, text="Ед. изм.:", bg="#f4f4f4").grid(row=0, column=3, sticky="w")
        ent_ing_unit = tk.Entry(ing_frame, width=6)
        ent_ing_unit.grid(row=1, column=3, padx=5)

        # Список для временного хранения добавляемых ингредиентов в текущий рецепт
        temp_ingredients = {}

        # Текстовая область для предпросмотра добавленных продуктов
        lbl_preview = tk.Label(add_win, text="Добавленные ингредиенты отсутствуют", font=("Arial", 10, "italic"), bg="#f4f4f4", fg="#666666", justify="left")

        def add_ingredient_to_list():
            cat = cb_category.get()
            name = cb_ing_name.get().strip()
            amount_str = ent_ing_amount.get().strip()
            unit = ent_ing_unit.get().strip()

            if not name or not amount_str or not unit:
                messagebox.showerror("Ошибка", "Заполните все поля ингредиента!")
                return
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Количество должно быть числом!")
                return

            if cat not in temp_ingredients:
                temp_ingredients[cat] = []

            # Сохраняем в структуру нашего JSON
            temp_ingredients[cat].append({"name": name, "amount": amount, "unit": unit})

            # Обновляем предпросмотр на экране
            preview_lines = []
            for c, items in temp_ingredients.items():
                preview_lines.append(f"{c}:")
                for item in items:
                    preview_lines.append(f"  • {item['name']} — {item['amount']} {item['unit']}")

            lbl_preview.config(text="\n".join(preview_lines), font=("Arial", 10), fg="black", justify="left", anchor="w")
            if not lbl_preview.winfo_manager():
                lbl_preview.pack(padx=20, anchor="w", pady=5)

            # Очищаем поля ввода ингредиента для следующего продукта
            cb_ing_name.set('')
            ent_ing_amount.delete(0, tk.END)
            ent_ing_unit.delete(0, tk.END)

        btn_add_ing = tk.Button(ing_frame, text="+", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", width=3, command=add_ingredient_to_list)
        btn_add_ing.grid(row=1, column=4, padx=(5, 0))

        # --- Поле ввода инструкции ---
        tk.Label(add_win, text="Инструкция по приготовлению:", font=("Arial", 11, "bold"), bg="#f4f4f4").pack(anchor="w", padx=20, pady=(10, 2))
        txt_instructions = tk.Text(add_win, font=("Arial", 11), height=8, wrap="word")
        txt_instructions.pack(padx=20, fill="x")

        # --- Логика сохранения в файл ---
        def save_new_recipe():
            title = ent_title.get().strip()
            instructions = txt_instructions.get("1.0", tk.END).strip()

            if not title:
                messagebox.showerror("Ошибка", "Укажите название блюда!")
                return
            if not temp_ingredients:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один ингредиент!")
                return
            if not instructions:
                messagebox.showerror("Ошибка", "Заполните инструкцию!")
                return

            # Генерируем уникальный ID на основе существующих рецептов
            next_id = max([r["id"] for r in all_recipes], default=0) + 1

            new_recipe = {
                "id": next_id,
                "title": title,
                "ingredients": temp_ingredients,
                "instructions": instructions
            }

            # Добавляем в локальный массив приложения
            all_recipes.append(new_recipe)

            # Перезаписываем data.json физически на диске
            try:
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(all_recipes, f, ensure_ascii=False, indent=4)

                messagebox.showinfo("Успех", f"Рецепт «{title}» успешно сохранен!")

                # Обновляем сетку чекбоксов на главном экране, чтобы сразу появились новые продукты
                update_grid(lbl_category_title.cget("text").replace("Ингредиенты: ", ""))
                add_win.destroy() # Закрываем окно добавления
            except Exception as e:
                messagebox.showerror("Ошибка файла", f"Не удалось сохранить рецепт: {e}")

        btn_save = tk.Button(add_win, text="Сохранить рецепт", font=("Arial", 12, "bold"), bg="#2196F3", fg="white", command=save_new_recipe)
        btn_save.pack(pady=20, fill="x", padx=20)

    # Функция открытия окна удаления рецепта
    def open_delete_recipe_window():
        # Защита: если база пуста, даже не открываем окно
        if not all_recipes:
            messagebox.showinfo("Пусто", "База рецептов пуста. Удалять нечего!")
            return

        del_win = tk.Toplevel(root)
        del_win.title("Удалить рецепт")
        del_win.geometry("400x250")
        del_win.configure(bg="#f4f4f4")
        del_win.grab_set() # Блокируем главное окно

        tk.Label(del_win, text="Выберите рецепт для удаления:", font=("Arial", 11, "bold"), bg="#f4f4f4").pack(pady=(20, 10))

        # Собираем список названий всех рецептов
        recipe_titles = [r["title"] for r in all_recipes]

        # Создаем выпадающий список
        cb_recipes = ttk.Combobox(del_win, values=recipe_titles, state="readonly", font=("Arial", 11), width=30)
        cb_recipes.pack(pady=10)
        cb_recipes.current(0) # Выбираем первый по умолчанию

        # Логика физического удаления
        def delete_selected():
            selected_title = cb_recipes.get()

            # Всплывающее окно подтверждения (защита от случайных кликов)
            confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить рецепт «{selected_title}»?\nЭто действие нельзя отменить.")

            if confirm:
                # 1. Ищем рецепт в оперативной памяти и удаляем его из списка
                for i, recipe in enumerate(all_recipes):
                    if recipe["title"] == selected_title:
                        del all_recipes[i]
                        break # Выходим из цикла, так как уже нашли и удалили

                # 2. Перезаписываем файл data.json обновленным списком
                try:
                    with open("data.json", "w", encoding="utf-8") as f:
                        json.dump(all_recipes, f, ensure_ascii=False, indent=4)

                    messagebox.showinfo("Успех", "Рецепт успешно удален!")

                    # 3. Обновляем главный экран (чтобы исчезли ингредиенты удаленного блюда)
                    update_grid(lbl_category_title.cget("text").replace("Ингредиенты: ", ""))
                    del_win.destroy() # Закрываем окно
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обновить файл: {e}")

        # Красная кнопка удаления
        btn_confirm_del = tk.Button(del_win, text="Удалить безвозвратно", font=("Arial", 11, "bold"),
                                    bg="#F44336", fg="white", command=delete_selected)
        btn_confirm_del.pack(pady=20)

    # УМНЫЙ ПОИСК: Функция поиска рецептов с допущением нехватки продуктов
    def find_recipes():
        # Собираем названия (имена) выбранных продуктов
        selected_names = set([ing for ing, var in ingredient_vars.items() if var.get() == 1])

        if not selected_names:
            messagebox.showinfo("Внимание", "Пожалуйста, выберите хотя бы один продукт!")
            return

        found_recipes = []

        for recipe in all_recipes:
            # Собираем все ингредиенты рецепта в один плоский список
            required_items = []
            for cat_ings in recipe["ingredients"].values():
                required_items.extend(cat_ings)

            # Получаем множество имен продуктов, которые нужны для рецепта
            required_names = set([item["name"] for item in required_items])

            # Математика множеств: вычитаем из нужных то, что есть у пользователя
            missing_names = required_names - selected_names

            # ГЛАВНОЕ ПРАВИЛО: Разрешаем нехватку не более 2-х ингредиентов
            if len(missing_names) <= 2:
                # Делаем поверхностную копию рецепта, чтобы временно добавить туда список недостающего
                recipe_copy = recipe.copy()
                # Вытаскиваем полные данные (граммы, штуки) только для недостающих продуктов
                recipe_copy["missing_details"] = [item for item in required_items if item["name"] in missing_names]
                found_recipes.append(recipe_copy)

        if found_recipes:
            # Сортируем выдачу: рецепты, где хватает ВСЕГО (0 недостающих), будут на самом верху!
            found_recipes.sort(key=lambda r: len(r.get("missing_details", [])))
            show_results_window(found_recipes)
        else:
            messagebox.showwarning("Нет совпадений", "Даже с учетом докупки 1-2 продуктов мы ничего не нашли.\nВыберите больше ингредиентов!")

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
    btn_reset = tk.Button(bottom_panel, text="Сбросить всё", font=("Arial", 10),bg="#FF9800", fg="white", command=reset_all)
    btn_reset.pack(side="left", padx=(0, 10))
    btn_add_recipe = tk.Button(bottom_panel, text="Добавить рецепт", font=("Arial", 11),bg="#9E9E9E", fg="white", width=15, command=open_add_recipe_window)
    btn_add_recipe.pack(side="left", padx=10)
    btn_del_recipe = tk.Button(bottom_panel, text="Удалить рецепт", font=("Arial", 11),bg="#E53935", fg="white", width=15, command=open_delete_recipe_window)
    btn_del_recipe.pack(side="left", padx=5)
    btn_search = tk.Button(bottom_panel, text="Найти рецепты", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=15, command=find_recipes)
    btn_search.pack(side="right", padx=20)

    update_grid(categories[0])
    root.mainloop()

if __name__ == "__main__":
    create_app()