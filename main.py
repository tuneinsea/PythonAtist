import tkinter as tk
from tkinter import messagebox
import json
import re

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
CONTACTS_FILE = "contacts.json"

# --- ЛОГИКА РАБОТЫ С ДАННЫМИ ---
def load_contacts():
    """Загрузка контактов из JSON-файла с обработкой ошибок."""
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_contacts(data):
    """Сохранение контактов в JSON-файл."""
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError:
        messagebox.showerror("Ошибка", "Не удалось сохранить данные на диск.")

# --- ВАЛИДАЦИЯ ВВОДА ---
def validate_input(name, number):
    """Валидация полей ввода. Возвращает (True, "") или (False, "Текст ошибки")."""
    if not name or not number:
        return False, "Все поля (Имя и Номер) должны быть заполнены."
    
    if len(name) < 2:
        return False, "Имя должно содержать не менее 2 символов."
        
    # Регулярное выражение для проверки номера (цифры, знаки +, -, (), пробелы)
    phone_pattern = r"^\+?[0-9\s\-\(\)]{6,20}$"
    if not re.match(phone_pattern, number):
        return False, "Некорректный формат номера телефона.\nПример: +7 (999) 123-45-67"
        
    return True, ""

# --- ФУНКЦИИ ИНТЕРФЕЙСА ---
def update_listbox(data_to_show=None):
    """Обновление списка на экране."""
    contact_listbox.delete(0, tk.END)
    
    # Если список пуст или не передан, берем актуальный глобальный список
    current_list = data_to_show if data_to_show is not None else contacts
    
    if not current_list:
        contact_listbox.insert(tk.END, " Контакты не найдены или список пуст")
        return

    for idx, contact in enumerate(current_list):
        contact_listbox.insert(tk.END, f" 👤 {contact['name']} — 📱 {contact['number']}")

def add_contact():
    """Добавление нового контакта."""
    name = entry_name.get().strip()
    number = entry_number.get().strip()
    
    # Валидация
    is_valid, error_msg = validate_input(name, number)
    if not is_valid:
        messagebox.showwarning("Ошибка валидации", error_msg)
        return
        
    # Проверка на дубликаты
    for contact in contacts:
        if contact['name'].lower() == name.lower():
            messagebox.showwarning("Предупреждение", f"Контакт с именем '{name}' уже существует.")
            return

    # Добавление
    contacts.append({"name": name, "number": number})
    save_contacts(contacts)
    update_listbox()
    
    # Очистка полей
    entry_name.delete(0, tk.END)
    entry_number.delete(0, tk.END)
    entry_name.focus()

def delete_contact():
    """Удаление выбранного контакта."""
    selected_indices = contact_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Предупреждение", "Выберите контакт из списка для удаления.")
        return
        
    index = selected_indices[0]
    text = contact_listbox.get(index)
    
    # Защита от удаления строки-заглушки
    if "Список пуст" in text or "Контакты не найдены" in text:
        return

    # Парсим имя из строки Listbox, чтобы найти его в исходном списке (важно при активном поиске)
    try:
        # Извлекаем часть между иконкой '👤 ' и ' — 📱'
        parsed_name = text.split("👤 ")[1].split(" — 📱")[0]
    except IndexError:
        messagebox.showerror("Ошибка", "Не удалось распознать контакт.")
        return

    # Находим и удаляем элемент из глобального списка по имени
    global contacts
    contacts = [c for c in contacts if c['name'] != parsed_name]
    
    save_contacts(contacts)
    
    # Сбрасываем поиск и обновляем экран
    entry_search.delete(0, tk.END)
    update_listbox()

def search_contact():
    """Поиск контактов по совпадению в имени или номере."""
    query = entry_search.get().strip().lower()
    if not query:
        update_listbox()
        return
        
    filtered = [c for c in contacts if query in c['name'].lower() or query in c['number']]
    update_listbox(filtered)

def reset_search():
    """Сброс фильтра поиска."""
    entry_search.delete(0, tk.END)
    update_listbox()

# --- ИНИЦИАЛИЗАЦИЯ ИНТЕРФЕЙСА (Tkinter) ---
root = tk.Tk()
root.title("Менеджер контактов v1.0")
root.geometry("450x550")
root.configure(bg="#f4f6f9")
root.resizable(False, False)

contacts = load_contacts()

# --- Блок 1: Форма добавления ---
frame_form = tk.LabelFrame(root, text=" Новый контакт ", font=("Arial", 10, "bold"), bg="#f4f6f9", padx=10, pady=10)
frame_form.pack(padx=15, pady=10, fill="x")

tk.Label(frame_form, text="Имя:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
entry_name = tk.Entry(frame_form, font=("Arial", 10), width=32)
entry_name.grid(row=0, column=1, pady=5, padx=5)

tk.Label(frame_form, text="Телефон:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
entry_number = tk.Entry(frame_form, font=("Arial", 10), width=32)
entry_number.grid(row=1, column=1, pady=5, padx=5)

btn_add = tk.Button(frame_form, text="➕ Добавить", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), 
                    command=add_contact, width=12, cursor="hand2")
btn_add.grid(row=2, column=1, sticky="e", pady=5, padx=5)

# --- Блок 2: Поиск ---
frame_search = tk.Frame(root, bg="#f4f6f9")
frame_search.pack(padx=15, pady=5, fill="x")

entry_search = tk.Entry(frame_search, font=("Arial", 10), width=28)
entry_search.pack(side="left", ipady=3)
entry_search.bind("<KeyRelease>", lambda event: search_contact()) # Поиск «на лету»

btn_clear = tk.Button(frame_search, text="🔄 Сброс", bg="#95a5a6", fg="white", font=("Arial", 9), 
                      command=reset_search, cursor="hand2")
btn_clear.pack(side="right", padx=5)

# --- Блок 3: Вывод данных (Listbox) ---
frame_list = tk.Frame(root, bg="#f4f6f9")
frame_list.pack(padx=15, pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side="right", fill="y")

contact_listbox = tk.Listbox(frame_list, font=("Arial", 11), yscrollcommand=scrollbar.set,
                             selectbackground="#3498db", selectforeground="white", bd=1)
contact_listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=contact_listbox.yview)

# --- Блок 4: Удаление ---
btn_delete = tk.Button(root, text="🗑️ Удалить выбранный контакт", bg="#e74c3c", fg="white", 
                       font=("Arial", 10, "bold"), command=delete_contact, height=2, cursor="hand2")
btn_delete.pack(padx=15, pady=15, fill="x")

# Первичный запуск
update_listbox()
root.mainloop()
