import pandas as pd
import xlsxwriter
import tkinter as tk
from tkinter import filedialog

# Define file paths initially as empty strings
file_path1 = ""
file_path2 = ""
output_path = ""


# Function to select the first input file
def select_input_file(entry):
    global file_path1
    file_path1 = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path1)


# Function to select the second input file
def select_second_input_file(entry):
    global file_path2
    file_path2 = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path2)


# Function to select the output directory
def select_output_directory(entry):
    global output_path
    output_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    entry.delete(0, tk.END)
    entry.insert(0, output_path)


# Function to handle the submit button click
def submit(input_entry1, input_entry2, output_entry, submit_button):
    process_data(file_path1, file_path2, output_path)
    submit_button.config(text="处理完成")


# Your data processing function
def process_data(file_path1, file_path2, output_path):
    try:
        # Read Excel files
        df1 = pd.read_excel(file_path1)
        df2 = pd.read_excel(file_path2)

        df1.rename(columns={'df1_成员账号': '成员账号'}, inplace=True)
        df2.rename(columns={'df2_成员账号': '成员账号'}, inplace=True)

        # ... rest of your data processing code ...
        # Merge DataFrames
        df_result = pd.merge(df1, df2, left_on='成员账号', right_on='成员账号', how='left')

        # Define the desired order of columns
        new_column_order = ['账期', '成员账号', '姓名', '付费总额(元)']

        # Reorder the columns in df_result
        df_result = df_result[new_column_order]

        # Create a Pandas Excel writer using xlsxwriter as the engine.
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        df_result.to_excel(writer, sheet_name='Sheet1', index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Set column width
        for idx, col in enumerate(df_result):
            worksheet.set_column(idx, idx, 20)

        # Set cell format for centering text
        center_format = workbook.add_format({'align': 'center'})
        worksheet.set_column(0, len(df_result.columns) - 1, None, center_format)

        # Calculate the sum of '付费总额(元)' and write it to the last row of the column
        sum_format = workbook.add_format(
            {'bold': True, 'font_color': 'red', 'align': 'center', 'num_format': '#,##0.00'})
        sum_value = df_result['付费总额(元)'].sum()
        last_row = len(df_result.index) + 1
        worksheet.write(last_row, 3, sum_value, sum_format)

        label_format = workbook.add_format({'bold': True, 'align': 'center'})
        worksheet.write(last_row, 2, '合计', label_format)
        worksheet.write(last_row + 1, 2, '优惠金额', label_format)
        discount = sum_value * 0.3
        worksheet.write(last_row + 1, 3, discount, sum_format)
        worksheet.write(last_row + 2, 2, '实际费用', label_format)
        worksheet.write(last_row + 2, 3, (sum_value - discount), sum_format)

        # Close the Pandas Excel writer and output the Excel file.
        writer.close()

    except FileNotFoundError:
        print("One of the input files was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# GUI setup
def setup_gui():
    global root
    root = tk.Tk()
    root.title("Excel处理工具(移动话费)")
    root.geometry("350x550")
    root.configure(bg="#F0F0F0")
    root.resizable(True, True)

    # Input file selection
    tk.Label(root, text="选择第一个输入文件:", font=("Arial", 12), bg="#F0F0F0").pack(pady=20)
    input_entry1 = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    input_entry1.pack(ipady=4, pady=10, padx=10)
    tk.Button(root, text="浏览", command=lambda: select_input_file(input_entry1), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Second input file selection
    tk.Label(root, text="选择第二个输入文件:", font=("Arial", 12), bg="#F0F0F0").pack(pady=20)
    input_entry2 = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    input_entry2.pack(ipady=4, pady=10, padx=10)
    tk.Button(root, text="浏览", command=lambda: select_second_input_file(input_entry2), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Output directory selection
    tk.Label(root, text="选择输出目录:", font=("Arial", 12), bg="#F0F0F0").pack(pady=20)
    output_entry = tk.Entry(root, font=("Arial", 12), relief=tk.FLAT, bg="white")
    output_entry.pack(ipady=4, pady=10, padx=10)
    tk.Button(root, text="浏览", command=lambda: select_output_directory(output_entry), font=("Arial", 12), bg="#4CAF50",
              fg="white", activebackground="#45a049", relief=tk.FLAT, cursor="hand2").pack(pady=5, padx=10)

    # Submit button
    submit_button = tk.Button(root, text="开始处理",
                              command=lambda: submit(input_entry1, input_entry2, output_entry, submit_button),
                              font=("Arial", 12), bg="#4CAF50", fg="white", activebackground="#45a049", relief=tk.FLAT,
                              cursor="hand2")
    submit_button.pack(pady=20, padx=10)

    root.mainloop()


if __name__ == "__main__":
    setup_gui()
