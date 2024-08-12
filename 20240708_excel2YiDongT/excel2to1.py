import pandas as pd
import tkinter as tk
from tkinter import filedialog

# GUI setup
def setup_gui():
    global root
    root = tk.Tk()
    root.title("Excel处理工具")
    root.geometry("350x600")
    root.configure(bg="#F0F0F0")
    root.resizable(True, True)

    # Mode selection
    mode_var = tk.StringVar(value="it_assets")  # Default mode
    tk.Label(root, text="选择处理模式:", font=("Arial", 12), bg="#F0F0F0").pack(pady=10)
    tk.Radiobutton(root, text="IT资产管理", variable=mode_var, value="it_assets", font=("Arial", 12), bg="#F0F0F0").pack()
    tk.Radiobutton(root, text="移动话费", variable=mode_var, value="mobile_billing", font=("Arial", 12), bg="#F0F0F0").pack()

    # ... rest of your GUI elements ...

    # Submit button
    submit_button = tk.Button(root, text="开始处理",
                              command=lambda: submit(input_entry1, input_entry2, output_entry, submit_button, mode_var),
                              font=("Arial", 12), bg="#4CAF50", fg="white", activebackground="#45a049", relief=tk.FLAT,
                              cursor="hand2")
    submit_button.pack(pady=20, padx=10)

    root.mainloop()


# Function to handle the submit button click
def submit(input_entry1, input_entry2, output_entry, submit_button, mode_var):
    mode = mode_var.get()
    if mode == "it_assets":
        process_data_it_assets(file_path1, file_path2, output_path)
    elif mode == "mobile_billing":
        process_data_mobile_billing(file_path1, file_path2, output_path)
    submit_button.config(text="处理完成")

# Your data processing functions for each mode
def process_data_it_assets(file_path1, file_path2, output_path):
    # IT asset management processing logic here
    pass

def process_data_mobile_billing(file_path1, file_path2, output_path):
    # Mobile billing processing logic here
    pass

# Main execution
if __name__ == "__main__":
    setup_gui()
