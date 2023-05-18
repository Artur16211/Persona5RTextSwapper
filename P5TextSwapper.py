import os
import subprocess
import re
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter
import sv_ttk
import sys
import configparser

from tkinter import filedialog
from deep_translator import GoogleTranslator


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)
        self.widget.update()
        root.update()

    def flush(self):
        pass


# Make a config parser
config = configparser.ConfigParser()

# Read the config file if it exists
if os.path.isfile('config.ini'):
    config.read('config.ini')
else:
    # If it doesn't exist, create it with default values
    config['Folders'] = {'mod_folder': '',
                         'output_folder': '', 'game': 'Persona 5 Royal'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Get the saved values or set default values if they don't exist
mod_folder = config.get('Folders', 'mod_folder', fallback='')
# language_folder = config.get('Folders', 'language_folder', fallback='')
output_folder = config.get('Folders', 'output_folder', fallback='')
game = config.get('Folders', 'game', fallback='Persona 5 Royal')

root = customtkinter.CTk()


def disable_button():
    run_button.config(state="disabled")
    dropdown.config(state="disable")
    mod_folder_button.config(state="disable")
    language_folder_button.config(state="disable")
    output_folder_button.config(state="disable")
    mod_folder_entry.config(state="disable")
    language_folder_entry.config(state="disable")
    output_folder_entry.config(state="disable")


def enable_button():
    run_button.config(state="normal")
    dropdown.config(state="normal")
    mod_folder_button.config(state="normal")
    # language_folder_button.config(state="normal")
    output_folder_button.config(state="normal")
    mod_folder_entry.config(state="normal")
    # language_folder_entry.config(state="normal")
    output_folder_entry.config(state="normal")


# Log box with scrollbar and no text editing
log_box = tk.Text(root, height=20, width=50)
log_box.grid(row=5, columnspan=3, column=0, sticky='ew')
# use columnspan to make the widget span multiple columns
# log_box.grid(columnspan=2)
# Create a scrollbar and associate it with log_box
scrollbar = ttk.Scrollbar(root, command=log_box.yview)
scrollbar.grid(row=5, column=4, sticky='ns')
# Disable editing
log_box.config(state=tk.DISABLED, yscrollcommand=scrollbar.set)


sys.stdout = TextRedirector(log_box, "stdout")


def on_select(event):
    # Make the variable global so it can be used
    global game
    game = dropdown.get()
    # Clear the log box
    log_box.config(state=tk.NORMAL)
    log_box.delete('1.0', tk.END)
    log_box.config(state=tk.DISABLED)
    print(f"Game: {game}")


# Options for the dropdown
options = ["Persona 5 Royal", "Persona 5", "Persona Q2"]

# Make the dropdown
dropdown = ttk.Combobox(root, values=options)

# Check if the saved value in the config file exists in the options list
if game in options:
    # Set the saved value in the config file as the default option
    dropdown.current(options.index(game))
else:
    dropdown.current(0)

# Disable write in the dropdown
dropdown.configure(state="readonly")

# Add the on_select function to the dropdown
dropdown.bind("<<ComboboxSelected>>", on_select)

# Run the on_select function when the program starts
on_select(None)

# Set the position of the dropdown in the window
dropdown.grid(row=3, column=0, padx=10, pady=10)


# specify the size of the window
root.geometry("680x600")

# disable resizing the GUI
root.resizable(False, False)


def browse_mod_folder():
    mod_folder = filedialog.askdirectory()
    mod_folder_entry.delete(0, tk.END)
    mod_folder_entry.insert(0, mod_folder)


def browse_language_folder():
    language_folder = filedialog.askdirectory()
    language_folder_entry.delete(0, tk.END)
    language_folder_entry.insert(0, language_folder)


def browse_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)


def run_program():
    if not mod_folder_entry.get() or not output_folder_entry.get():
        messagebox.showerror(
            "Error", "Please fill in all fields.")
        return
    disable_button()
    # Clear the log box
    log_box.config(state=tk.NORMAL)
    log_box.delete('1.0', tk.END)
    log_box.config(state=tk.DISABLED)

    mod_folder = mod_folder_entry.get()
    output_folder = output_folder_entry.get()

    # List files and folders in mod_folder including those in subfolders and full path
    mod_files_list = []
    for root, dirs, files in os.walk(mod_folder):
        for file in files:
            path = os.path.join(root, file)
            mod_files_list.append(path)

    # Delete the value of mod_folder from the path
    mod_files_list = [x.replace(mod_folder, '') for x in mod_files_list]

    mod_files_list_updated = []
    for root, dirs, files in os.walk(mod_folder):
        for file in files:
            path = os.path.join(root, file)
            mod_files_list_updated.append(path)

    # Delete the path of mod_folder from the list
    mod_files_list_updated = [x.replace(mod_folder, '')
                              for x in mod_files_list_updated]

    for file in mod_files_list_updated:
        full_path = mod_folder + file
        if not file.lower().endswith((".bf", ".bmd")):
            # print(f"El archivo {file} no es .bf o .bmd, se eliminará.")
            os.remove(full_path)

    # Path to the dependencies
    personaeditor_path = os.path.join(
        'dependencies', 'personaeditor', 'personaeditorcmd.exe')
    atlus_script_tools_path = os.path.join(
        "dependencies", "atlusscripttools", "AtlusScriptCompiler.exe")

    # Current directory
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Define the functions that will be executed in each case

    # AtlusScriptCompiler functions
    def ASCDecompile(input_file_path):
        input_file_name = os.path.basename(input_file_path)
        if game == "Persona 5 Royal":

            print(f"Decompiling BMD file: {input_file_name} with P5R library")
            subprocess.run([atlus_script_tools_path, input_file_path,
                            "-Decompiled", "-Library", "P5R", "-Encoding", "P5"])
        elif game == "Persona 5":
            print(f"Decompiling BMD file: {input_file_name} with P5 library")
            subprocess.run([atlus_script_tools_path, input_file_path,
                            "-Decompiled", "-Library", "P5", "-Encoding", "P5"])
        elif game == "Persona Q2":
            print(f"Decompiling BMD file: {input_file_name} with PQ2 library")
            subprocess.run([atlus_script_tools_path, input_file_path,
                            "-Decompiled", "-Library", "PQ2", "-Encoding", "SJ"])

    def ASCCompile(input_file_path):
        input_file_name = os.path.basename(input_file_path)
        if game == "Persona 5 Royal":
            print(f"Compiling BMD file: {input_file_name} with P5R library")
            output_file_path = os.path.splitext(input_file_path)[0] + '.bmd'
            subprocess.run([atlus_script_tools_path, input_file_path, "-Out",
                            output_file_path, "-Compile", "-OutFormat", "V1BE", "-Library", "P5R", "-Encoding", "P5"])
        elif game == "Persona 5":
            print(f"Compiling BMD file: {input_file_name} with P5 library")
            output_file_path = os.path.splitext(input_file_path)[0] + '.bmd'
            subprocess.run([atlus_script_tools_path, input_file_path, "-Out",
                            output_file_path, "-Compile", "-OutFormat", "V1BE", "-Library", "P5", "-Encoding", "P5"])
        elif game == "Persona Q2":
            print(f"Compiling BMD file: {input_file_name} with PQ2 library")
            output_file_path = os.path.splitext(input_file_path)[0] + '.bmd'
            subprocess.run([atlus_script_tools_path, input_file_path, "-Out",
                            output_file_path, "-Compile", "-OutFormat", "V1BE", "-Library", "PQ2", "-Encoding", "SJ"])

    # PersonaEditor functions
    def PEExport(input_file_path):
        subprocess.run([personaeditor_path, input_file_path, '-expall'])

    def PEImport(input_file_path):
        subprocess.run([personaeditor_path, input_file_path,
                        '-impall', '-save', input_file_path])

    def des_case_bmd(name_file):
        ASCDecompile(name_file)

    def des_case_bf(path_file):
        PEExport(path_file)
        # the name_file is a path, so we need to get the name of the file
        name_file = os.path.basename(path_file)
        print(f"Extracting all files from bf file: {path_file}")
        # change the extension of the file to .bmd
        name_file_bmd = os.path.splitext(path_file)[0] + '.bmd'
        # the name of the file without the extension
        name_file_only = os.path.splitext(name_file)[0]
        # search for the bf file on the mod_folder
        for root, dirs, files in os.walk(mod_folder):
            for file in files:
                if file.lower() == name_file.lower() and file.lower().endswith('.bf'):
                    print(
                        f"Searching for the bf file: {name_file} in the mod folder")
                    name_file_bf_mod = os.path.join(root, file)
                    rel_path = os.path.relpath(name_file_bf_mod, mod_folder)
                    output_file = os.path.join(output_folder, rel_path)
                    output_dir = os.path.dirname(output_file)
                    # create the output directory if it doesn't exist
                    os.makedirs(output_dir, exist_ok=True)
                    shutil.copy(name_file_bf_mod, output_file)
                    break

        # check if the file exists
        if os.path.isfile(name_file_bmd):
            des_case_bmd(name_file_bmd)
        # dirname
        name_file_dirname = os.path.dirname(path_file)
        # get all the .dat files in the folder
        # get all the .dat files in the folder
        dat_files = []
        for root, dirs, files in os.walk(name_file_dirname):
            for file in files:
                if file.endswith('.DAT'):
                    dat_files.append(os.path.join(root, file))

        # if the files name start with name_file.name, copy the .dat files to the output folder
        for dat_file in dat_files:
            if dat_file.startswith(name_file_dirname):
                # replace the mod_folder or language_folder with the output_folder
                name_file_dirname_output = name_file_dirname.replace(
                    mod_folder, output_folder)
        # create the output directory if it doesn't exist
                os.makedirs(os.path.dirname(
                    name_file_dirname_output), exist_ok=True)
        # copy the file to the output directory
                shutil.copy(dat_file, name_file_dirname_output)

    # replace
    def process_msg(name_file):

        # get the name of the file without the extension and add .msg
        name_file_msg = os.path.splitext(name_file)[0] + '.msg'

        # make a list with the msg
        mod_msgs = []

        match = r"\[[^\[\]]*\]|\[[^\[]*[^\s\[\]]\]"

        # Read the lines of the mod .msg file when not starting with [msg or empty line or // and create a list with the lines
        with open(name_file_msg, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                if not line.startswith('[msg') and not line.startswith('//') and not line.strip() == '' and not line.startswith('[sel'):
                    # Apply regular expression to remove text between brackets
                    result = []
                    position = 0
                    while True:
                        coincidencia = re.search(match, line[position:])
                        if coincidencia:
                            result.append(coincidencia.group(0))
                            position += coincidencia.end()
                        else:
                            break

                        # Check if the next character is a space or a bracket
                        if len(line[position:].strip()) == 0 or line[position:position+5] == "[var " or line[position:position+7] == "[f 4 1]" or line[position:position+7] == "[f 4 2]" or line[position:position+5] == "[clr " or line[position] != "[":
                            break

                    # Remove the text between brackets and the characters "[w]" and "[e]"
                    for item in result:
                        line = line.replace(item, "")
                    line = line.replace("[w]", "").replace("[e]", "")
                    last_occurrence_index = line.rfind("[n]")
                    if game == "Persona Q2":
                        # Delete all lines after the last occurrence of "[n]"
                        if last_occurrence_index != -1:
                            line = line[:last_occurrence_index]
                    if game == "Persona 5" or game == "Persona 5 Royal":
                        if last_occurrence_index != -1:
                            line = line[:last_occurrence_index] + line[last_occurrence_index:].replace("[n]", "", 1)
                    # add the line to the list
                    mod_msgs.append(line)

        # Copy the .msg file to the output folder
        name_file_output = name_file_msg.replace(mod_folder, output_folder)
        os.makedirs(os.path.dirname(name_file_output), exist_ok=True)
        shutil.copy(name_file_msg, name_file_output)

        # Make a list with the messages in spanish
        mod_msgs_es = []
        # Translate the messages to spanish
        for msg in mod_msgs:
            # replace the "[n]" with "" to avoid errors
            msgn = msg.replace("[n]", "")
            mod_msgs_es.append(GoogleTranslator(
                source='en', target='es').translate(msgn))

        # Create a dictionary with the messages in english as keys and the messages in spanish as values
        mod_msgs_dict = dict(zip(mod_msgs, mod_msgs_es))

        # print the dictionary
        # for key, value in mod_msgs_dict.items():
        # print(key, ' : ', value)

        print(
            f"Reemplazando mensajes en el archivo .msg de {name_file_output}...")

        # Delete the \n from the key
        mod_msgs_dict = {key.replace(
            '\n', ''): value for key, value in mod_msgs_dict.items()}
        
        # change values in the dictionary depending of the game value
        if game == "Persona 5" or game == "Persona 5 Royal":
            replacement_dict = {
                'á': '茨',
                'é': '姻',
                'í': '胤',
                'ó': '吋',
                'ú': '雨',
                'ñ': '隠',
                '¿': '夷',
                '¡': '斡',
                'Á': '威',
                'É': '畏',
                'Í': '緯',
                'Ó': '遺',
                'Ú': '郁',
                'Ñ': '謂'
            }
        elif game == "Persona Q2":
            replacement_dict = {
                'á': '係',
                'é': '契',
                'í': '慶',
                'ó': '矩',
                'ú': '具',
                'ñ': '狗',
                '¿': '空',
                '¡': '緊',
                'Á': '寓',
                'É': '掘',
                'Í': '轡',
                'Ó': '繰',
                'Ú': '訓',
                'Ñ': '粂'
            }

        for key, value in mod_msgs_dict.items():
            if value is not None:
                for char, replacement in replacement_dict.items():
                    value = value.replace(char, replacement)
                # if the value no has [n], replace "" with "[n]" one time if the character count is more than 37
                # Agregar [n] en intervalos de 37 caracteres completos
                if len(value) >= 37:
                    resultado = ""
                    inicio = 0

                    while inicio + 37 <= len(value):
                        fin = inicio + 37

                        espacio_idx = value.rfind(" ", inicio, fin)  # Encuentra el último espacio en el intervalo actual
                        if espacio_idx != -1:
                            resultado += value[inicio:espacio_idx] + "[n]" + value[espacio_idx:fin]
                        else:
                            resultado += value[inicio:fin]

                        inicio = fin

                    resultado += value[inicio:]  # Agrega el resto del texto después del último intervalo completo

                    value = resultado
                # Delete the spaces before and after the [n]
                value = value.replace(' [n] ', '[n]').replace(' [n]', '[n]').replace('[n] ', '[n]')
                # La primera letra del mensaje debe ser mayúscula
                value = value[0].upper() + value[1:]
                #
                mod_msgs_dict[key] = value

        # Replace the text strings that match the dictionary keys
        with open(name_file_output, 'r', encoding='utf-8-sig', errors='ignore') as f:
            filedata = f.read()

        for key, value in mod_msgs_dict.items():
            if value is not None:
                filedata = filedata.replace(key, value)

        with open(name_file_output + ".tmp", 'w', encoding='utf-8-sig', errors='ignore') as f:
            f.write(filedata)


        # Delete the original file
        os.remove(name_file_output)
        # Rename the temporary file to the original name
        os.rename(name_file_output + ".tmp", name_file_output)

    # Delete all files that are not .bin, .bmd, .pak or .bf
    for folder in [mod_folder]:
        for file in os.scandir(folder):
            if file.is_file() and not file.name.lower().endswith((".bin", ".bmd", ".pak", ".bf")):
                os.remove(file.path)

    # Check all types of files in the "Mod" folder
    # Read all files in the root and its subfolders
    for folder_name, subfolders, files in os.walk(mod_folder):
        # Read all files in the current folder
        for name_file in files:
            print(f"Processing file: {name_file}")
            file_extension = name_file.split('.')[-1]
            switcher = {
                'bmd': des_case_bmd,
                'bf': des_case_bf,
                'BMD': des_case_bmd,
                'BF': des_case_bf
            }
            if file_extension in switcher:
                print(f"Processing switcher file: {name_file}")
                switcher[file_extension](os.path.join(folder_name, name_file))

    # Proccess all .msg files in the "Mod" folder and make the changes in the "Output" folder
    for root, dirs, files in os.walk(mod_folder):
        for name_file in files:
            if name_file.lower().endswith('.msg'):
                # print(f"Processing file: {root}/{name_file}")
                process_msg(os.path.join(root, name_file))

    for root, dirs, files in os.walk(output_folder):
        for msg_file in files:
            if msg_file.lower().endswith('.msg'):
                print(f"Compiling {msg_file}")
                ASCCompile(os.path.join(root, msg_file))

    # Change all the endwith .bmd.bmd to .bmd
    for root, dirs, files in os.walk(output_folder):
        for name in files:
            if name.lower().endswith('.bmd.bmd'):
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, name[:-8] + ".bmd")
                print(f"Renaming {old_path} to {new_path}")
                try:
                    os.rename(old_path, new_path)
                except FileExistsError:
                    print(f"Skipping {old_path} as {new_path} already exists")
                    continue

    # Import all .bf files in the "Output" folder with PEImport
    for root, dirs, files in os.walk(output_folder):
        for mod_file in files:
            if mod_file.lower().endswith('.bf'):
                mod_file_path = os.path.join(root, mod_file)
                print(f"Importing {mod_file} in {root}")
                PEImport(mod_file_path)
            mod_file_name_new = mod_file.split('.')[0]

    # print(f"Deleting extra files from {output_folder}...")

    def delete_files_not_in_list(folder_path, files_list):
        # Make a list with all the files in the folder including the ones in the subfolders
        Del_files = []
        for root, dirs, files in os.walk(folder_path):
            for name in files:
                Del_files.append(os.path.join(root, name))
        Mod_List_Keep = []
        for i in range(len(files_list)):
            Mod_List_Keep.append(
                folder_path + files_list[i])
        # Delete all lines from Del_files that are in Mod_List_Keep
        for i in range(len(Mod_List_Keep)):
            for j in range(len(Del_files)):
                if Mod_List_Keep[i].lower() == Del_files[j].lower():
                    Del_files[j] = ""
        # Delete all the empty lines
        while "" in Del_files:
            Del_files.remove("")
        # Delete the files that are left in the keep_files list
        for file in Del_files:
            try:
                print(f"Deleting {file}")
                os.remove(file)
            except FileNotFoundError:
                print(f"Skipping {file} as it doesn't exist")
                continue

    delete_files_not_in_list(output_folder, mod_files_list)
    delete_files_not_in_list(mod_folder, mod_files_list)
    # delete_files_not_in_list(language_folder, language_files_list)

    def delete_empty_folders(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                full_path = os.path.join(root, name)
                if not os.listdir(full_path):  # check if directory is empty
                    os.rmdir(full_path)
                else:
                    # recursively delete all files and subfolders
                    delete_empty_folders(full_path)

    delete_empty_folders(output_folder)
    delete_empty_folders(mod_folder)
    # delete_empty_folders(language_folder)

    print("Done!")
    enable_button()
    tk.messagebox.showinfo("Finished", "Replaced all the names in the mod!")


# Mod folder
mod_folder_label = ttk.Label(root, text="Mod folder:", background="#242424")
mod_folder_entry = ttk.Entry(root, width=60)
mod_folder_button = ttk.Button(root, text="Browse", command=browse_mod_folder)
mod_folder_entry.insert(0, mod_folder)  # Insert the saved value

mod_folder_label.grid(row=0, column=0, padx=5, pady=10)
mod_folder_entry.grid(row=0, column=1, padx=5, pady=10)
mod_folder_button.grid(row=0, column=2, padx=5, pady=10)

# Language folder
language_folder_label = ttk.Label(
    root, text="Language folder:", background="#242424")
language_folder_entry = ttk.Entry(root, width=60)
language_folder_button = ttk.Button(
    root, text="Browse", command=browse_language_folder)
# language_folder_entry.insert(0, language_folder)  # Insert the saved value
# Disable the language folder entry and button
language_folder_entry.config(state="disabled")
language_folder_button.config(state="disabled")

language_folder_label.grid(row=1, column=0, padx=5, pady=10)
language_folder_entry.grid(row=1, column=1, padx=5, pady=10)
language_folder_button.grid(row=1, column=2, padx=5, pady=10)

# Output folder
output_folder_label = ttk.Label(
    root, text="Output folder:", background="#242424")
output_folder_entry = ttk.Entry(root, width=60)
output_folder_button = ttk.Button(
    root, text="Browse", command=browse_output_folder)
output_folder_entry.insert(0, output_folder)  # Insert the saved value

output_folder_label.grid(row=2, column=0, padx=5, pady=10)
output_folder_entry.grid(row=2, column=1, padx=5, pady=10)
output_folder_button.grid(row=2, column=2, padx=5, pady=10)

# Run button
run_button = ttk.Button(root, text="Replace", command=run_program)
run_button.grid(row=4, column=1, padx=0, pady=15)


def save_config():
    # Save the values in the config file
    config['Folders'] = {
        'mod_folder': mod_folder_entry.get(),
        # 'language_folder': language_folder_entry.get(),
        'output_folder': output_folder_entry.get(),
        'game': game
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def on_closing():
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        save_config()
        root.destroy()


# Run the on_closing function when the window is closed
root.protocol("WM_DELETE_WINDOW", on_closing)

sv_ttk.set_theme("dark")

# set theme dark in cttk
customtkinter.set_appearance_mode("dark")

root.iconbitmap("dependencies/test2.ico")

root.title("Persona 5 Text Translator")

root.mainloop()
