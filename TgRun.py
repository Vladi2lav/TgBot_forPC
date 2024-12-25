import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import threading

class FilePathApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Path Saver")
        self.groups = {}  # Словарь для групп и их файлов
        self.single_files = []  # Список для одиночных файлов
        self.save_file = "file_paths.json"

        self.load_file_paths()  # Загружаем данные из файла при старте

        # Создаем элементы интерфейса
        self.frame = tk.Frame(root)
        self.frame.pack(pady=10, padx=10)

        # Поле для ввода группы
        self.group_name_label = tk.Label(self.frame, text="Group Name:")
        self.group_name_label.pack(side=tk.LEFT, padx=5)
        self.group_name_entry = tk.Entry(self.frame)
        self.group_name_entry.pack(side=tk.LEFT, padx=5)

        # Кнопка для добавления группы
        self.add_group_button = tk.Button(self.frame, text="Add Group", command=self.add_group)
        self.add_group_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для добавления одиночного файла
        self.add_single_file_button = tk.Button(self.frame, text="Add Single File", command=self.add_single_file)
        self.add_single_file_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для очистки списка
        self.clear_button = tk.Button(self.frame, text="Clear List", command=self.clear_list)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для итерации по путям
        self.iterate_button = tk.Button(self.frame, text="Iterate Paths", command=self.iterate_paths)
        self.iterate_button.pack(side=tk.LEFT, padx=5)

        # Список для отображения групп и одиночных файлов
        self.listbox = tk.Listbox(root, width=50, height=15)
        self.listbox.pack(pady=10)

        self.update_listbox()

        # Второе поле для одиночных файлов
        self.single_file_frame = tk.Frame(root)
        self.single_file_frame.pack(pady=10)

        # Кнопка для добавления одиночного файла
        self.add_single_file_button = tk.Button(self.single_file_frame, text="Add Single File", command=self.add_single_file)
        self.add_single_file_button.pack(side=tk.LEFT, padx=5)

        # Список для отображения одиночных файлов
        self.single_files_listbox = tk.Listbox(self.single_file_frame, width=50, height=15)
        self.single_files_listbox.pack(pady=10)

        self.update_single_files_listbox()

    def add_group(self):
        group_name = self.group_name_entry.get()
        if group_name:
            self.groups[group_name] = []  # Добавление пустой группы
            self.save_file_paths()
            self.update_listbox()
            self.group_name_entry.delete(0, tk.END)  # Очищаем поле ввода

    def add_single_file(self):
        group_name = self.group_name_entry.get()
        if group_name:
            if group_name not in self.groups:
                messagebox.showerror("Error", "Group does not exist!")
                return

            # Открываем диалог для выбора файла
            file_path = filedialog.askopenfilename(title="Select a File")
            if file_path:
                self.groups[group_name].append(file_path)  # Добавляем файл в группу
                self.save_file_paths()
                self.update_listbox()
                self.update_single_files_listbox()
        else:
            messagebox.showerror("Error", "Please enter a group name!")

    def clear_list(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the list?"):
            self.groups.clear()
            self.single_files.clear()
            self.save_file_paths()
            self.update_listbox()
            self.update_single_files_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for group_name, file_paths in self.groups.items():
            self.listbox.insert(tk.END, f"Group: {group_name} ({len(file_paths)} files)")

    def update_single_files_listbox(self):
        self.single_files_listbox.delete(0, tk.END)
        for file_path in self.single_files:
            self.single_files_listbox.insert(tk.END, f"File: {file_path}")

    def iterate_paths(self):
        if not self.groups and not self.single_files:
            messagebox.showinfo("Info", "No files to iterate.")
            return
        for group_name, paths in self.groups.items():
            print(f"Group: {group_name}")
            for path in paths:
                print(f"  Processing: {path}")
        for path in self.single_files:
            print(f"Processing: {path}")

    def save_file_paths(self):
        with open(self.save_file, "w") as f:
            json.dump({"groups": self.groups, "single_files": self.single_files}, f)

    def load_file_paths(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.groups = data.get("groups", {})
                        self.single_files = data.get("single_files", [])
                    else:
                        self.groups = {}
                        self.single_files = []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error loading data: {e}. Creating new file.")
                self.groups = {}
                self.single_files = []
        else:
            print("No saved file paths found, starting with an empty list.")
            self.groups = {}
            self.single_files = []



# Telegram Bot Integration
api = "7893070021:AAEFN5eSFQkM_OwDz11ULpO72eLjOid4CSU"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher()

# Reference to FilePathApp
file_path_app = None

@dp.message(Command("start"))
async def cmd_name(message: Message):
    await message.answer("Let's get started!")

@dp.message(Command("mode"))
async def cmd_mode(message: Message):
    if not file_path_app or not file_path_app.groups:
        await message.answer("File groups are empty.")
        return

    # Create buttons for each group
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=group_name, callback_data=f"group_{i}")]
        for i, group_name in enumerate(file_path_app.groups.keys())
    ])

    await message.answer("Select a group of files to run:", reply_markup=keyboard)

@dp.message(Command("init"))
async def cmd_init(message: Message):
    if not file_path_app or not file_path_app.single_files:
        await message.answer("No single files available.")
        return

    # Create buttons for single files
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=os.path.basename(file_path), callback_data=f"file_{i}")]
        for i, file_path in enumerate(file_path_app.single_files)
    ])

    await message.answer("Select a file to run:", reply_markup=keyboard)

@dp.callback_query(lambda callback_query: callback_query.data.startswith("group_"))
async def group_selected(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1])
    group_name = list(file_path_app.groups.keys())[index]
    if group_name in file_path_app.groups:
        selected_files = file_path_app.groups[group_name]
        await callback_query.message.answer(f"Group: {group_name}\nFiles: {len(selected_files)}")
        for file_path in selected_files:
            try:
                os.startfile(file_path)  # Открыть файл стандартной программой
                await callback_query.message.answer(f"Файл {os.path.basename(file_path)} успешно открыт.")
            except Exception as e:
                await callback_query.message.answer(f"Не удалось открыть файл {os.path.basename(file_path)}: {e}")




@dp.callback_query(lambda callback_query: callback_query.data.startswith("file_"))
async def file_selected(callback_query: CallbackQuery):
    index = int(callback_query.data.split("_")[1])
    if index < len(file_path_app.single_files):
        selected_file_path = file_path_app.single_files[index]
        try:
            os.startfile(selected_file_path)  # Open file with default program
            await callback_query.message.answer(f"File {os.path.basename(selected_file_path)} opened successfully.")
        except Exception as e:
            await callback_query.message.answer(f"Could not open the file: {e}")
    else:
        await callback_query.message.answer("File not found.")

async def telegram_main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    def run_tkinter():
        global file_path_app
        root = tk.Tk()
        file_path_app = FilePathApp(root)
        root.mainloop()

    tk_thread = threading.Thread(target=run_tkinter, daemon=True)
    tk_thread.start()

    asyncio.run(telegram_main())
