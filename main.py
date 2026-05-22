import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime

# Константа для файла данных
DATA_FILE = "expenses.json"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker v1.0")
        self.root.geometry("750x650")
        self.root.configure(bg="#f5f6fa")
        self.root.resizable(False, False)

        # Категории по умолчанию
        self.categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Покупки", "Другое"]
        
        # Загрузка данных
        self.expenses = self.load_expenses()

        # Инициализация интерфейса
        self.create_widgets()
        self.update_table(self.expenses)

    # --- ЛОГИКА РАБОТЫ С JSON ---
    def load_expenses(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_expenses(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(self.expenses, file, ensure_ascii=False, indent=4)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные на диск.")

    # --- ВАЛИДАЦИЯ ---
    def validate_input(self, amount_str, date_str):
        # 1. Валидация суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть строго больше нуля."
        except ValueError:
            return False, "Сумма должна быть числом (например: 150 или 250.50)."

        # 2. Валидация даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 2026-05-22)."

        return True, ""

    # --- СОЗДАНИЕ ИНТЕРФЕЙСА ---
    def create_widgets(self):
        # Стиль для таблиц
        style = ttk.Style()
        style.theme_use("clam")

        # Блок 1: Форма добавления
        frame_add = tk.LabelFrame(self.root, text=" Добавить новый расход ", font=("Arial", 10, "bold"), bg="#f5f6fa", padx=10, pady=10)
        frame_add.pack(padx=15, pady=10, fill="x")

        tk.Label(frame_add, text="Сумма:", bg="#f5f6fa").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_amount = tk.Entry(frame_add, font=("Arial", 10), width=15)
        self.entry_amount.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        tk.Label(frame_add, text="Категория:", bg="#f5f6fa").grid(row=0, column=2, sticky="w", pady=5)
        self.combo_category = ttk.Combobox(frame_add, values=self.categories, state="readonly", width=15)
        self.combo_category.set(self.categories[0])
        self.combo_category.grid(row=0, column=3, pady=5, padx=5)

        tk.Label(frame_add, text="Дата (ГГГГ-ММ-ДД):", bg="#f5f6fa").grid(row=0, column=4, sticky="w", pady=5)
        self.entry_date = tk.Entry(frame_add, font=("Arial", 10), width=12)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Подстановка текущей даты
        self.entry_date.grid(row=0, column=5, pady=5, padx=5)

        btn_add = tk.Button(frame_add, text="➕ Добавить", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.add_expense, cursor="hand2")
        btn_add.grid(row=0, column=6, padx=10)

        # Блок 2: Фильтры и Период
        frame_filter = tk.LabelFrame(self.root, text=" Фильтрация и Аналитика ", font=("Arial", 10, "bold"), bg="#f5f6fa", padx=10, pady=10)
        frame_filter.pack(padx=15, pady=5, fill="x")

        # Фильтр по категории
        tk.Label(frame_filter, text="Категория:", bg="#f5f6fa").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_filter_cat = ttk.Combobox(frame_filter, values=["Все"] + self.categories, state="readonly", width=12)
        self.combo_filter_cat.set("Все")
        self.combo_filter_cat.grid(row=0, column=1, pady=5, padx=5)

        # Фильтр по датам (Период)
        tk.Label(frame_filter, text="С:", bg="#f5f6fa").grid(row=0, column=2, sticky="w", pady=5)
        self.entry_start_date = tk.Entry(frame_filter, font=("Arial", 10), width=10)
        self.entry_start_date.grid(row=0, column=3, pady=5, padx=5)

        tk.Label(frame_filter, text="По:", bg="#f5f6fa").grid(row=0, column=4, sticky="w", pady=5)
        self.entry_end_date = tk.Entry(frame_filter, font=("Arial", 10), width=10)
        self.entry_end_date.grid(row=0, column=5, pady=5, padx=5)

        btn_apply = tk.Button(frame_filter, text="🔍 Применить фильтр", bg="#3498db", fg="white", font=("Arial", 9, "bold"), command=self.apply_filters, cursor="hand2")
        btn_apply.grid(row=0, column=6, padx=5)

        btn_reset = tk.Button(frame_filter, text="🔄 Сбросить", bg="#95a5a6", fg="white", font=("Arial", 9), command=self.reset_filters, cursor="hand2")
        btn_reset.grid(row=0, column=7, padx=5)

        # Блок 3: Вывод данных (Таблица Treeview)
        frame_table = tk.Frame(self.root, bg="#f5f6fa")
        frame_table.pack(padx=15, pady=10, fill="both", expand=True)

        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма (руб.)")
        
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("category", width=250, anchor="w")
        self.tree.column("amount", width=200, anchor="e")

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Блок 4: Итоговая сумма
        self.lbl_total = tk.Label(self.root, text="Итого за период: 0.00 руб.", font=("Arial", 14, "bold"), bg="#f5f6fa", fg="#2c3e50")
        self.lbl_total.pack(padx=15, pady=15, anchor="e")

    # --- ЛОГИКА ФУНКЦИОНАЛА ---
    def update_table(self, data_list):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        total = 0.0
        # Сортировка расходов по дате от новых к старым
        sorted_data = sorted(data_list, key=lambda x: x["date"], reverse=True)
        
        for item in sorted_data:
            self.tree.insert("", tk.END, values=(item["date"], item["category"], f"{item['amount']:.2f}"))
            total += item["amount"]
        
        self.lbl_total.config(text=f"Итого за период: {total:.2f} руб.")

    def add_expense(self):
        amount_str = self.entry_amount.get().strip()
        category = self.combo_category.get()
        date_str = self.entry_date.get().strip()

        is_valid, error_msg = self.validate_input(amount_str, date_str)
        if not is_valid:
            messagebox.showwarning("Ошибка валидации", error_msg)
            return

        new_expense = {
            "amount": float(amount_str),
            "category": category,
            "date": date_str
        }

        self.expenses.append(new_expense)
        self.save_expenses()
        self.reset_filters() # Сбрасываем фильтры, чтобы увидеть добавленный расход
        
        # Очистка поля суммы после успешного ввода
        self.entry_amount.delete(0, tk.END)

    def apply_filters(self):
        category_filter = self.combo_filter_cat.get()
        start_date_str = self.entry_start_date.get().strip()
        end_date_str = self.entry_end_date.get().strip()

        filtered_list = self.expenses

        # Фильтр по категории
        if category_filter != "Все":
            filtered_list = [x for x in filtered_list if x["category"] == category_filter]

        # Фильтр по дате "С"
        if start_date_str:
            try:
                datetime.strptime(start_date_str, "%Y-%m-%d")
                filtered_list = [x for x in filtered_list if x["date"] >= start_date_str]
            except ValueError:
                messagebox.showwarning("Ошибка фильтра", "Неверный формат даты начала (ГГГГ-ММ-ДД).")
                return

        # Фильтр по дате "По"
        if end_date_str:
            try:
                datetime.strptime(end_date_str, "%Y-%m-%d")
                filtered_list = [x for x in filtered_list if x["date"] <= end_date_str]
            except ValueError:
                messagebox.showwarning("Ошибка фильтра", "Неверный формат даты конца (ГГГГ-ММ-ДД).")
                return

        self.update_table(filtered_list)

    def reset_filters(self):
        self.combo_filter_cat.set("Все")
        self.entry_start_date.delete(0, tk.END)
        self.entry_end_date.delete(0, tk.END)
        self.update_table(self.expenses)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
