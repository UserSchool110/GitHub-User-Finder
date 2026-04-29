import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Глобальные переменные
favorites_file = "favorites.json"
favorites = []
search_results = []
search_entry = None
results_listbox = None
favorites_listbox = None
status_var = None
search_button = None
root = None


def load_favorites():
    #Загрузка избранных из JSON файла
    global favorites
    if os.path.exists(favorites_file):
        try:
            with open(favorites_file, 'r', encoding='utf-8') as f:
                favorites = json.load(f)
        except:
            favorites = []
    else:
        favorites = []


def save_favorites():
    #Сохранение избранных в JSON файл
    with open(favorites_file, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=2, ensure_ascii=False)


def refresh_favorites_list():
    #Обновление списка избранных в интерфейсе
    favorites_listbox.delete(0, tk.END)
    for fav in favorites:
        display_text = f"{fav['login']}"
        if fav.get('name'):
            display_text += f" - {fav['name']}"
        favorites_listbox.insert(tk.END, display_text)


def clear_results():
    #Очистка результатов поиска
    results_listbox.delete(0, tk.END)
    search_entry.delete(0, tk.END)
    status_var.set("Результаты удалены")


def get_user_details(username):
    #Получение информации о пользователе
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})

        if response.status_code == 200:
            return response.json()
        else:
            return {'login': username}
    except:
        return {'login': username}


def search_users():
    #Поиск пользователей на GitHub
    global search_results

    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
        status_var.set("Ошибка: поле поиска пустое")
        return

    status_var.set(f"Поиск пользователей по запросу '{query}'...")
    root.config(cursor="watch")
    search_button.config(state=tk.DISABLED)

    try:
        url = f"https://api.github.com/search/users?q={query}&per_page=30"
        response = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})

        if response.status_code == 200:
            data = response.json()
            users = data.get('items', [])

            results_listbox.delete(0, tk.END)

            if users:
                search_results = []

                for user in users:
                    user_details = get_user_details(user['login'])
                    search_results.append(user_details)

                    display_text = f"{user['login']}"
                    if user_details.get('name'):
                        display_text += f" - {user_details['name']}"

                    results_listbox.insert(tk.END, display_text)

                status_var.set(f"Найдено пользователей: {len(users)}")
            else:
                results_listbox.insert(tk.END, "Пользователи не найдены")
                status_var.set("Пользователи не найдены")
        else:
            messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
            status_var.set(f"Ошибка API: {response.status_code}")

    except requests.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
        status_var.set("Ошибка соединения с GitHub API")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        status_var.set("Произошла ошибка при поиске")
    finally:
        root.config(cursor="")
        search_button.config(state=tk.NORMAL)


def add_to_favorites():
    #Добавление выбранного пользователя в избранное
    selected = results_listbox.curselection()
    if not selected:
        messagebox.showinfo("Информация", "Пожалуйста, выберите пользователя из результатов поиска")
        return

    user_data = search_results[selected[0]]
    user_login = user_data['login']

    for fav in favorites:
        if fav['login'] == user_login:
            messagebox.showinfo("Информация", f"Пользователь {user_login} уже в избранном!")
            return

    favorite_user = {
        'login': user_data['login'],
        'name': user_data.get('name', ''),
        'html_url': user_data.get('html_url', ''),
        'bio': user_data.get('bio', '')
    }

    favorites.append(favorite_user)
    save_favorites()
    refresh_favorites_list()

    status_var.set(f"Пользователь {user_login} добавлен в избранное")
    messagebox.showinfo("Успех", f"Пользователь {user_login} добавлен в избранное!")


def remove_from_favorites():
    #Удаление пользователя из избранного
    selected = favorites_listbox.curselection()
    if not selected:
        messagebox.showinfo("Информация", "Пожалуйста, выберите пользователя из избранного")
        return

    user_display = favorites_listbox.get(selected[0])
    user_login = user_display.split(' -')[0].strip()

    for i, fav in enumerate(favorites):
        if fav['login'] == user_login:
            del favorites[i]
            break

    save_favorites()
    refresh_favorites_list()

    status_var.set(f"Пользователь {user_login} удален из избранного")
    messagebox.showinfo("Успех", f"Пользователь {user_login} удален из избранного!")


# Создание главного окна
root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("850x550")
root.configure(bg='#f0f0f0')

# Верхняя панель с поиском
search_frame = tk.Frame(root, bg='#ffffff', relief=tk.RAISED, bd=1)
search_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Label(search_frame, text="GitHub User Finder", font=('Arial', 14, 'bold'),
         bg='#ffffff', fg='#333333').pack(pady=10)

search_row = tk.Frame(search_frame, bg='#ffffff')
search_row.pack(pady=10)

tk.Label(search_row, text="Логин:", font=('Arial', 10), bg='#ffffff').pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_row, width=35, font=('Arial', 10), relief=tk.SUNKEN, bd=1)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind("<Return>", lambda e: search_users())

search_button = tk.Button(search_row, text="Найти", command=search_users,
                          bg='#4CAF50', fg='white', font=('Arial', 9),
                          relief=tk.RAISED, bd=1, padx=15, pady=2)
search_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(search_row, text="Очистить", command=clear_results,
                         bg='#f44336', fg='white', font=('Arial', 9),
                         relief=tk.RAISED, bd=1, padx=15, pady=2)
clear_button.pack(side=tk.LEFT, padx=5)

# Основная панель
main_frame = tk.Frame(root, bg='#f0f0f0')
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Левая часть - результаты поиска
left_panel = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

tk.Label(left_panel, text="Результаты поиска", font=('Arial', 11, 'bold'),
         bg='#ffffff', fg='#333333').pack(anchor=tk.W, padx=10, pady=5)

results_listbox = tk.Listbox(left_panel, height=20, font=('Arial', 10),
                             bg='#fafafa', relief=tk.SUNKEN, bd=1)
results_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

add_favorite_btn = tk.Button(left_panel, text="+ Добавить в избранное",
                             command=add_to_favorites,
                             bg='#2196F3', fg='white', font=('Arial', 9),
                             relief=tk.RAISED, bd=1, padx=10, pady=3)
add_favorite_btn.pack(pady=10)

# Правая часть - избранное
right_panel = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

tk.Label(right_panel, text="Избранное", font=('Arial', 11, 'bold'),
         bg='#ffffff', fg='#333333').pack(anchor=tk.W, padx=10, pady=5)

favorites_listbox = tk.Listbox(right_panel, height=20, font=('Arial', 10),
                               bg='#fafafa', relief=tk.SUNKEN, bd=1)
favorites_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

fav_buttons_frame = tk.Frame(right_panel, bg='#ffffff')
fav_buttons_frame.pack(pady=10)

remove_favorite_btn = tk.Button(fav_buttons_frame, text="- Удалить",
                                command=remove_from_favorites,
                                bg='#ff9800', fg='white', font=('Arial', 9),
                                relief=tk.RAISED, bd=1, padx=15, pady=3)
remove_favorite_btn.pack(side=tk.LEFT, padx=5)

refresh_fav_btn = tk.Button(fav_buttons_frame, text="⟳ Обновить",
                            command=refresh_favorites_list,
                            bg='#9E9E9E', fg='white', font=('Arial', 9),
                            relief=tk.RAISED, bd=1, padx=15, pady=3)
refresh_fav_btn.pack(side=tk.LEFT, padx=5)

# Статусная строка
status_var = tk.StringVar()
status_var.set("Готов к работе")
status_bar = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN,
                      anchor=tk.W, bg='#e0e0e0', font=('Arial', 9), padx=5)
status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

# Загрузка избранных при запуске
load_favorites()
refresh_favorites_list()

# Запуск приложения
root.mainloop()