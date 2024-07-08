import pandas as pd
import xlsxwriter

# Define file paths
file_path1 = r'D:\SynologyDrive\Work\移动电信业务\移动\python\大塚化学202405.xlsx'
file_path2 = r'D:\SynologyDrive\Work\移动电信业务\移动\python\人员手机号.xlsx'
output_path = r'D:\SynologyDrive\Work\移动电信业务\移动\python\电话费2024年5月.xlsx'

try:
    # Read Excel files
    df1 = pd.read_excel(file_path1)
    df2 = pd.read_excel(file_path2)

    df1.rename(columns={'df1_成员账号': '成员账号'}, inplace=True)
    df2.rename(columns={'df2_成员账号': '成员账号'}, inplace=True)

    print(df1.columns)
    print(df2.columns)

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
    sum_format = workbook.add_format({'bold': True, 'font_color': 'red', 'align': 'center', 'num_format': '#,##0.00'})
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
