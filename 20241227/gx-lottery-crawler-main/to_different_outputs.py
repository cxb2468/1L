from typing import List
import csv
import xlwt
import pandas as pd
from styleframe import StyleFrame, Styler, utils
from article import Article


def articles_txt_content(articles: List[Article]):
    return '\n'.join([str(article) for article in articles]) + '\n'


def articles2txt(articles: List[Article]):
    content = articles_txt_content(articles)
    with open('lottery_gx_out.txt', 'w', encoding='utf-8') as f:
        f.write(content)


def articles_to_2d_array(articles: List[Article]):
    return [[article.date, article.link, article.title] for article in articles]


def articles2csv(articles: List[Article]):
    with open('lottery_gx_out.csv', 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(('date', 'link', 'title'))
        csv_rows = articles_to_2d_array(articles)
        csv_writer.writerows(csv_rows)


def articles2csv_pandas(articles: List[Article]):
    df = pd.DataFrame(articles)
    df.to_csv('lottery_gx_out.p.csv', index=False)


def get_duplicate_and_unique(articles: List[Article]):
    st = set()
    duplicate: List[Article] = []
    unq: List[Article] = []
    for article in articles:
        title = article.title
        if title in st:
            duplicate.append(article)
            continue
        st.add(title)
        unq.append(article)
    return duplicate, unq


XLS_SHEET_NAMES = ('all data', 'unique', 'duplicate')


def articles2xls(articles: List[Article]):
    def sheet_common_op(sheet):
        sheet.col(0).width = 256 * 15
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 40
        for i, v in enumerate(('date', 'link', 'title')):
            sheet.write(0, i, v)

    workbook = xlwt.Workbook(encoding='utf-8')
    sheet1 = workbook.add_sheet(XLS_SHEET_NAMES[0])
    sheet_common_op(sheet1)
    excel_rows = articles_to_2d_array(articles)
    for i, row in enumerate(excel_rows):
        for j, cell in enumerate(row):
            sheet1.write(i + 1, j, cell)

    duplicate, unq = get_duplicate_and_unique(articles)
    dup_rows = articles_to_2d_array(duplicate)
    unq_rows = articles_to_2d_array(unq)

    sheet2 = workbook.add_sheet(XLS_SHEET_NAMES[1])
    sheet_common_op(sheet2)
    for i, row in enumerate(unq_rows):
        for j, cell in enumerate(row):
            sheet2.write(i + 1, j, cell)

    sheet3 = workbook.add_sheet(XLS_SHEET_NAMES[2])
    sheet_common_op(sheet3)
    for i, row in enumerate(dup_rows):
        for j, cell in enumerate(row):
            sheet3.write(i + 1, j, cell)

    workbook.save('lottery_gx_out.xls')


def articles2xlsx(articles: List[Article]):
    df_all = pd.DataFrame(articles)
    duplicate, unq = get_duplicate_and_unique(articles)
    df_unq = pd.DataFrame(unq)
    df_duplicate = pd.DataFrame(duplicate)
    df_arr = (df_all, df_unq, df_duplicate)
    with pd.ExcelWriter('lottery_gx_out.xlsx') as writer:
        for df, sheet_name in zip(df_arr, XLS_SHEET_NAMES):
            sf = StyleFrame(df)
            header_style = Styler(
                font_color='#2980b9',
                bold=True,
                font_size=14,
                horizontal_alignment=utils.horizontal_alignments.center,
                vertical_alignment=utils.vertical_alignments.center,
            )
            content_style = Styler(
                font_size=12,
                horizontal_alignment=utils.horizontal_alignments.left,
            )
            sf.apply_headers_style(header_style)
            sf.apply_column_style(sf.columns, content_style)

            # it's a pity that we have to set font_size and horizontal_alignment again
            row_bg_style = Styler(
                bg_color='#bdc3c7',
                font_size=12,
                horizontal_alignment=utils.horizontal_alignments.left,
            )
            indexes = list(range(1, len(sf), 2))
            sf.apply_style_by_indexes(indexes, styler_obj=row_bg_style)

            sf.set_column_width_dict(
                {
                    'date': 15,
                    'link': 20,
                    'title': 40,
                }
            )
            sf.to_excel(writer, sheet_name=sheet_name, index=False)
