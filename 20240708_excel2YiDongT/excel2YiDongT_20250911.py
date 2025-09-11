import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os
import re
import sys
import subprocess

# Define file paths initially as empty strings
file_path1 = ""
file_path2 = ""  # 新增：第二个文件路径
output_path = ""

# Function to get the directory where the script/exe is located
def get_script_dir():
    if getattr(sys, 'frozen', False):
        # If the application is frozen (bundled with PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # If running as a script
        return os.path.dirname(os.path.abspath(__file__))

# Get the directory where the script is located
script_dir = get_script_dir()
# Define the fixed file path for 人员手机号.xlsx
fixed_file_path = os.path.join("人员手机号.xlsx")


# Function to select the first input file
def select_input_file(entry):
    global file_path1
    file_path1 = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path1)
    
    # Automatically generate output filename based on input filename
    generate_output_filename()


# Function to select the second input file (新增)
def select_input_file2(entry):
    global file_path2
    file_path2 = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path2)


# Function to automatically generate output filename based on input filename
def generate_output_filename():
    global file_path1, output_path
    if file_path1:
        # Extract filename without extension
        filename = os.path.basename(file_path1)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Search for YYYYMM pattern in the filename
        match = re.search(r'(20\d{4})', name_without_ext)
        if match:
            yyyymm = match.group(1)
            year = yyyymm[:4]
            month = yyyymm[4:]
            # Generate output filename
            output_filename = f"电话费{year}年{month}月.xlsx"
            # Set default output path to the same directory as input file
            input_dir = os.path.dirname(file_path1)
            output_path = os.path.join(input_dir, output_filename)
            
            # Update the output entry field using the saved reference
            try:
                output_entry_ref.delete(0, tk.END)
                output_entry_ref.insert(0, output_path)
            except NameError:
                # If output_entry_ref is not defined, skip updating the entry field
                pass


# Function to select the output directory
def select_output_directory(entry):
    global output_path
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                               initialfile=os.path.basename(output_path) if output_path else "电话费.xlsx")
    entry.delete(0, tk.END)
    entry.insert(0, output_path)


# Function to handle the submit button click
def submit(input_entry1, input_entry2, output_entry, submit_button):
    global file_path1, file_path2
    # Use the selected second file, or default to 人员手机号.xlsx in the same directory
    second_file = file_path2 if file_path2 else "人员手机号.xlsx"
    process_data(file_path1, second_file, output_path)
    submit_button.config(text="处理完成")
    # 显示"打开输出文件夹"按钮
    show_open_folder_button()


# Function to reset the application state
def reset_application(input_entry1, input_entry2, output_entry, submit_button):
    global file_path1, file_path2, output_path
    
    # Reset global variables
    file_path1 = ""
    file_path2 = ""
    output_path = ""
    
    # Clear entry fields
    input_entry1.delete(0, tk.END)
    input_entry2.delete(0, tk.END)
    output_entry.delete(0, tk.END)
    
    # Reset submit button text
    submit_button.config(text="开始处理")
    
    # Hide the open folder button if it exists
    hide_open_folder_button()
    
    # Clear the generated output filename
    generate_output_filename()


# Your data processing function
def process_data(file_path1, file_path2, output_path):
    try:
        # Read Excel files
        df1 = pd.read_excel(file_path1)
        df2 = pd.read_excel(file_path2)

        df1.rename(columns={'df1_成员账号': '成员账号'}, inplace=True)
        df2.rename(columns={'df2_成员账号': '成员账号'}, inplace=True)
        
        # Ensure the '成员账号' columns have the same data type (convert to string)
        df1['成员账号'] = df1['成员账号'].astype(str)
        df2['成员账号'] = df2['成员账号'].astype(str)

        # Merge DataFrames
        df_result = pd.merge(df1, df2, left_on='成员账号', right_on='成员账号', how='left')

        # Define the desired order of columns
        new_column_order = ['账期', '成员账号', '姓名', '付费总额(元)']

        # Reorder the columns in df_result
        df_result = df_result[new_column_order]
        
        # Remove the row with member account "1100000000000017"
        df_result = df_result[df_result['成员账号'] != '1100000000000017']
        
        # Remove rows where member account length is greater than or equal to 12
        df_result = df_result[df_result['成员账号'].str.len() < 12]

        # Create a Pandas Excel writer using xlsxwriter as the engine.
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        df_result.to_excel(writer, sheet_name='Sheet1', index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Set column width and centering format together
        center_format = workbook.add_format({'align': 'center'})
        for idx, col in enumerate(df_result):

            worksheet.set_column(idx, idx, 20, center_format)

        # Calculate the sum of '付费总额(元)' and write it to the last row of the column
        sum_format = workbook.add_format(
            {'bold': True, 'font_color': 'red', 'align': 'center', 'num_format': '#,##0.00'})
        sum_value = df_result['付费总额(元)'].sum()
        last_row = len(df_result.index) + 1
        worksheet.write(last_row, 3, sum_value, sum_format)

        label_format = workbook.add_format({'bold': True, 'align': 'center'})
        worksheet.write(last_row, 2, '合计', label_format)
        worksheet.write(last_row + 1, 2, '优惠金额', label_format)
        #折扣 1800元封顶
        discount = sum_value * 0.3
        if discount <= 1800:
            worksheet.write(last_row + 1, 3, discount, sum_format)
        elif discount > 1800:
            worksheet.write(last_row + 1, 3, 1800, sum_format)
        worksheet.write(last_row + 2, 2, '实际费用', label_format)
        worksheet.write(last_row + 2, 3, (sum_value - discount), sum_format)

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()

    except FileNotFoundError:
        print("One of the input files was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Function to open the output folder
def open_output_folder():
    global output_path
    if output_path:
        output_dir = os.path.dirname(output_path)
        if os.path.exists(output_dir):
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", output_dir])


# Function to show the "打开输出文件夹" button
def show_open_folder_button():
    global open_folder_button
    if 'open_folder_button' in globals():
        open_folder_button.pack(side=tk.LEFT, padx=5)
    else:
        open_folder_button = tk.Button(buttons_frame, text="打开输出文件夹",
                                       command=open_output_folder,
                                       font=("Arial", 12), bg="#2196F3", fg="white", 
                                       activebackground="#1976D2", relief=tk.FLAT,
                                       cursor="hand2")
        open_folder_button.pack(side=tk.LEFT, padx=5)


# Function to hide the "打开输出文件夹" button
def hide_open_folder_button():
    global open_folder_button
    if 'open_folder_button' in globals():
        open_folder_button.pack_forget()


# GUI setup
def setup_gui():
    global root, input_entry1_ref, input_entry2_ref, output_entry_ref, buttons_frame
    root = tk.Tk()
    root.title("Excel处理工具(移动话费)")
    root.geometry("350x550")
    root.configure(bg="#F0F0F0")
    root.resizable(True, True)

    # Input file selection1
    tk.Label(root, text="选择第一个输入文件:", font=("Arial", 12), bg="#F0F0F0").pack(pady=20)
    input_entry1 = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    input_entry1.pack(ipady=4, pady=10, padx=10)
    input_entry1_ref = input_entry1  # Keep a reference for later use
    tk.Button(root, text="浏览", command=lambda: select_input_file(input_entry1), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Input file selection2
    tk.Label(root, text="选择第二个输入文件:人员手机号.xlsx", font=("Arial", 12), bg="#F0F0F0").pack(pady=(20, 5))
    input_entry2 = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    input_entry2.pack(ipady=4, pady=10, padx=10)
    input_entry2_ref = input_entry2  # Keep a reference for later use
    tk.Button(root, text="浏览", command=lambda: select_input_file2(input_entry2), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Output directory selection
    tk.Label(root, text="选择输出目录并输入文件名:", font=("Arial", 12), bg="#F0F0F0").pack(pady=20)
    output_entry = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    output_entry.pack(ipady=4, pady=10, padx=10)
    output_entry_ref = output_entry  # Keep a reference for later use
    tk.Button(root, text="浏览", command=lambda: select_output_directory(output_entry), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Buttons frame
    buttons_frame = tk.Frame(root, bg="#F0F0F0")
    buttons_frame.pack(pady=20, padx=10)

    # Submit button
    submit_button = tk.Button(buttons_frame, text="开始处理",
                              command=lambda: submit(input_entry1, input_entry2, output_entry, submit_button),
                              font=("Arial", 12), bg="#4CAF50", fg="white", activebackground="#45a049", relief=tk.FLAT,
                              cursor="hand2")
    submit_button.pack(side=tk.LEFT, padx=5)

    # Reset button
    reset_button = tk.Button(buttons_frame, text="重置",
                             command=lambda: reset_application(input_entry1, input_entry2, output_entry, submit_button),
                             font=("Arial", 12), bg="#f44336", fg="white", activebackground="#d32f2f", relief=tk.FLAT,
                             cursor="hand2")
    reset_button.pack(side=tk.LEFT, padx=5)

    root.mainloop()


if __name__ == "__main__":
    setup_gui()