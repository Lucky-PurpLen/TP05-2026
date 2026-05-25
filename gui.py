import tkinter as tk

def create_app():
    root = tk.Tk()
    root.title("Что приготовить?")

    root.geometry("1280x720")

    root.resizable(False,False)

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
        btn = tk.Button(left_panel, text=cat, font=("Arial",11), bg="#e0e0e0", anchor="w", relief="flat")
        btn.pack(fill="x",padx=10,pady=2)

    lbl_category_title = tk.Label(central_panel, text="Ингредиенты: Мясо и птица", bg="#ffffff", font=("Arial", 16, "bold"))
    lbl_category_title.pack(pady=20)
    grid_frame = tk.Frame(central_panel, bg="#ffffff")
    grid_frame.pack(fill="both", expand=True, padx=40)
    sample_ingredients = [
        "Куриное филе", "Говядина", "Свинина", "Индейка",
        "Фарш мясной", "Бекон", "Утка", "Колбаса", "Сосиски",
        "Печень", "Фарш куриный", "Сало"
    ]
    row_num = 0
    col_num = 0
    for ingredient in sample_ingredients:
        var = tk.IntVar()
        chk = tk.Checkbutton(grid_frame, text=ingredient, variable=var, bg="#ffffff", font=("Arial", 11))
        chk.grid(row=row_num, column=col_num, padx=15, pady=10, sticky="w")
        col_num += 1
        if col_num > 2:
            col_num = 0
            row_num += 1

    lbl_counter = tk.Label(bottom_panel, text="Выбрано ингредиентов: 0", bg="#e0e0e0", font=("Arial", 12, "bold"))
    lbl_counter.pack(side="left", padx=20)
    btn_search = tk.Button(bottom_panel, text="Найти рецепты", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=15)
    btn_search.pack(side="right", padx=20)

    root.mainloop()

if __name__ == "__main__":
    create_app()