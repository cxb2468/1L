# birthday_converter.py
try:
    from zhDateTime import DateTime, zhDateTime
    ZHDATETIME_AVAILABLE = True
except (SyntaxError, ImportError) as e:
    print(f"警告: zhDateTime库加载失败: {e}")
    print("将尝试使用LunarCalendar库")
    ZHDATETIME_AVAILABLE = False

# 尝试导入LunarCalendar作为备选方案
if not ZHDATETIME_AVAILABLE:
    try:
        from lunarcalendar import Lunar, Solar
        LUNAR_CALENDAR_AVAILABLE = True
        print("成功加载lunarcalendar库")
    except ImportError:
        LUNAR_CALENDAR_AVAILABLE = False
        print("警告: lunarcalendar库也未安装，农历转换功能将不可用")
else:
    LUNAR_CALENDAR_AVAILABLE = False

from datetime import datetime, date
import pandas as pd
import xlwings as xw
import numpy as np
import re


def parse_lunar_date(lunar_str):
    """
    解析阴历生日字符串，支持多种格式：
    - 08-15
    - 8月15日
    - 八月十五
    - 08/15
    - 闰八月十五
    """
    if pd.isna(lunar_str) or lunar_str == '':
        return None, None, None

    lunar_str = str(lunar_str).strip()

    # 检查是否为闰月
    is_leap = False
    if '闰' in lunar_str:
        is_leap = True
        lunar_str = lunar_str.replace('闰', '')

    # 尝试数字格式解析
    if re.match(r'^\d{1,2}[-/]\d{1,2}$', lunar_str):
        parts = re.split(r'[-/]', lunar_str)
        month = int(parts[0])
        day = int(parts[1])
        return month, day, is_leap

    # 尝试中文格式解析
    # 注意：月份映射需要按长度排序，优先匹配多字符月份（如"十一"、"十二"）
    month_map = {
        '正月': 1, '一月': 1, '腊月': 12, '二月': 2, '三月': 3, '四月': 4, '五月': 5,
        '六月': 6, '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
    }
    day_map = {
        '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5, '初六': 6,
        '初七': 7, '初八': 8, '初九': 9, '初十': 10, '十一': 11, '十二': 12,
        '十三': 13, '十四': 14, '十五': 15, '十六': 16, '十七': 17, '十八': 18,
        '十九': 19, '二十': 20, '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24,
        '二十五': 25, '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30
    }

    # 尝试匹配月份 - 按月份名称长度降序排列，优先匹配长名称
    sorted_months = sorted(month_map.items(), key=lambda x: len(x[0]), reverse=True)
    for month_name, month_num in sorted_months:
        if month_name in lunar_str:
            remaining = lunar_str.replace(month_name, '')
            
            # 首先尝试直接匹配日期
            sorted_days = sorted(day_map.items(), key=lambda x: len(x[0]), reverse=True)
            for day_name, day_num in sorted_days:
                if remaining == day_name or remaining.strip() == day_name:
                    return month_num, day_num, is_leap
            
            # 如果没有直接匹配，尝试将"二十"转换为"廿"后再匹配
            remaining_normalized = remaining.replace('二十', '廿')
            for day_name, day_num in sorted_days:
                if remaining_normalized == day_name or remaining_normalized.strip() == day_name:
                    return month_num, day_num, is_leap
            
            # 如果还是没有匹配，尝试在remaining中查找完整的日期名称
            for day_name, day_num in sorted_days:
                if day_name in remaining and len(remaining.replace(day_name, '').strip()) == 0:
                    return month_num, day_num, is_leap

    # 尝试正则表达式提取数字
    numbers = re.findall(r'\d+', lunar_str)
    if len(numbers) >= 2:
        month = int(numbers[0])
        day = int(numbers[1])
        return month, day, is_leap

    return None, None, is_leap


def get_current_lunar_year():
    """获取当前农历年份"""
    if ZHDATETIME_AVAILABLE:
        current_solar_date = datetime.now()
        current_lunar_date = zhDateTime.from_datetime(current_solar_date)
        return current_lunar_date.year
    elif LUNAR_CALENDAR_AVAILABLE:
        # 使用lunarcalendar获取当前农历年
        today = datetime.now().date()
        # 这里我们简单地将阳历今天转换为农历来获取农历年份
        from lunarcalendar import Converter
        converter = Converter()
        # Lunar.from_date 可以从 date 对象创建农历日期
        lunar_today = Lunar.from_date(today)
        return lunar_today.year
    else:
        # 如果都没有，返回公历年份作为近似值
        return datetime.now().year


def convert_to_current_year_solar(solar_date):
    """将阳历生日转换为本年阳历生日"""
    if pd.isna(solar_date) or not isinstance(solar_date, (date, datetime)):
        return None

    current_year = datetime.now().year
    try:
        # 处理2月29日等特殊日期
        if solar_date.month == 2 and solar_date.day == 29:
            # 检查当前年是否为闰年
            if (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0):
                return date(current_year, 2, 29)
            else:
                return date(current_year, 2, 28)

        return date(current_year, solar_date.month, solar_date.day)
    except ValueError:
        return None


def convert_lunar_to_specific_year_solar(lunar_str, target_year):
    """将阴历生日转换为指定年份的阳历生日"""
    month, day, is_leap = parse_lunar_date(lunar_str)
    if month is None or day is None:
        return None

    # 尝试使用zhDateTime
    if ZHDATETIME_AVAILABLE:
        try:
            # 创建农历日期
            lunar_date = zhDateTime(target_year, month, day, is_leap=is_leap)
            # 转换为阳历
            solar_date = lunar_date.to_datetime()
            return solar_date.date()
        except Exception as e:
            print(f"zhDateTime农历转换错误: {lunar_str} -> {e}")
    
    # 如果zhDateTime失败，尝试使用lunarcalendar
    if LUNAR_CALENDAR_AVAILABLE:
        try:
            # lunarcalendar中创建农历日期
            lunar = Lunar(target_year, month, day, isleap=is_leap)
            # 转换为阳历 date 对象
            solar_date = lunar.to_date()
            return solar_date
        except Exception as e:
            print(f"lunarcalendar农历转换错误: {lunar_str} -> {e}")
    
    if not ZHDATETIME_AVAILABLE and not LUNAR_CALENDAR_AVAILABLE:
        print(f"警告: 没有可用的农历库，无法转换农历日期: {lunar_str}")
    
    return None


def convert_lunar_to_target_year_solar(lunar_str, target_year):
    """
    将阴历生日转换为目标年份内的阳历生日
    
    核心逻辑：
    - 尝试用 target_year-1, target_year, target_year+1 三个农历年去转换
    - 优先选择转换后落在 target_year 公历年份的那个结果
    - 如果没有精确匹配，返回最接近的日期（优先下一年年初）
    """
    month, day, is_leap = parse_lunar_date(lunar_str)
    if month is None or day is None:
        return None

    # 尝试使用zhDateTime或lunarcalendar
    exact_match = None  # 精确匹配（在目标年份内）
    fallback_date = None  # 备选日期（最接近的）
    
    # 尝试三个农历年份：目标年份-1、目标年份、目标年份+1
    for lunar_year in [target_year - 1, target_year, target_year + 1]:
        result = None
        
        # 尝试使用zhDateTime
        if ZHDATETIME_AVAILABLE:
            try:
                lunar_date = zhDateTime(lunar_year, month, day, is_leap=is_leap)
                solar_date = lunar_date.to_datetime()
                result = solar_date.date()
            except Exception:
                pass
        
        # 如果zhDateTime失败，尝试使用lunarcalendar
        if result is None and LUNAR_CALENDAR_AVAILABLE:
            try:
                lunar = Lunar(lunar_year, month, day, isleap=is_leap)
                result = lunar.to_date()
            except Exception:
                pass
        
        if result is not None:
            # 检查转换结果是否在目标公历年份内
            if result.year == target_year:
                exact_match = result
                break  # 找到精确匹配，直接返回
            
            # 记录备选：优先下一年的年初（1月或2月）
            if result.year == target_year + 1 and result.month <= 2:
                if fallback_date is None or fallback_date.year != target_year + 1:
                    fallback_date = result
            # 其次上一年的年末（11月或12月）
            elif result.year == target_year - 1 and result.month >= 11:
                if fallback_date is None:
                    fallback_date = result
    
    if not ZHDATETIME_AVAILABLE and not LUNAR_CALENDAR_AVAILABLE:
        print(f"警告: 没有可用的农历库，无法转换农历日期: {lunar_str}")
    
    # 优先返回精确匹配，其次返回备选
    return exact_match if exact_match else fallback_date


def calculate_this_year_birthday(row):
    """
    计算本年生日的逻辑：
    1. 优先使用阳历生日（如果有）
    2. 如果没有阳历生日，使用阴历生日
    3. 如果都有，优先使用阳历生日（可以根据需求调整）
    4. 如果都没有，返回None
    """
    solar_birthday = row.get('阳历生日')
    lunar_birthday_str = row.get('阴历生日')
    current_year = datetime.now().year

    # 情况1：有阳历生日
    if pd.notna(solar_birthday) and solar_birthday not in ['', 'NaT', None]:
        return convert_to_current_year_solar(solar_birthday)

    # 情况2：有阴历生日 - 使用新的转换函数，指定当前年份
    if pd.notna(lunar_birthday_str) and lunar_birthday_str not in ['', 'NaT', None]:
        return convert_lunar_to_target_year_solar(lunar_birthday_str, current_year)

    # 情况3：都没有
    return None


def process_excel_file_multi_year(input_file, output_file=None, years=[2026, 2027, 2028]):
    """
    处理Excel文件，添加多个年份的阳历生日列
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(input_file)

        print(f"读取到 {len(df)} 条记录")
        print(f"列名: {df.columns.tolist()}")

        # 确保必要的列存在
        required_columns = ['阳历生日', '阴历生日']
        for col in required_columns:
            if col not in df.columns:
                print(f"警告: 缺少必要列 '{col}'，将创建空列")
                df[col] = None

        # 转换阳历生日列为日期类型
        if '阳历生日' in df.columns:
            df['阳历生日'] = pd.to_datetime(df['阳历生日'], errors='coerce')

        # 为每个目标年份添加阳历生日列
        for year in years:
            col_name = f'{year}年阳历生日'
            print(f"正在计算{year}年阳历生日...")
            
            def calculate_year_birthday(row, target_year=year):
                solar_birthday = row.get('阳历生日')
                lunar_birthday_str = row.get('阴历生日')
                
                # 情况1：有阳历生日
                if pd.notna(solar_birthday) and solar_birthday not in ['', 'NaT', None]:
                    try:
                        if isinstance(solar_birthday, (date, datetime)):
                            # 处理2月29日等特殊日期
                            if solar_birthday.month == 2 and solar_birthday.day == 29:
                                if (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0):
                                    return date(target_year, 2, 29)
                                else:
                                    return date(target_year, 2, 28)
                            return date(target_year, solar_birthday.month, solar_birthday.day)
                    except:
                        pass
                
                # 情况2：有阴历生日
                if pd.notna(lunar_birthday_str) and lunar_birthday_str not in ['', 'NaT', None]:
                    return convert_lunar_to_specific_year_solar(lunar_birthday_str, target_year)
                
                # 情况3：都没有
                return None
            
            df[col_name] = df.apply(calculate_year_birthday, axis=1)
            
            # 格式化该年的生日为字符串
            display_col = f'{col_name}显示'
            df[display_col] = df[col_name].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '未设置'
            )

        # 添加备注列说明来源
        def get_source(row):
            solar = row.get('阳历生日')
            lunar = row.get('阴历生日')

            if pd.notna(solar) and solar not in ['', 'NaT', None]:
                return '阳历'
            elif pd.notna(lunar) and lunar not in ['', 'NaT', None]:
                return '阴历'
            else:
                return '无'

        df['生日来源'] = df.apply(get_source, axis=1)

        # 保存结果
        if output_file is None:
            output_file = input_file.replace('.xlsx', '_多年份生日.xlsx')

        df.to_excel(output_file, index=False)
        print(f"处理完成！结果已保存到: {output_file}")

        # 统计信息
        total = len(df)
        from_solar = len(df[df['生日来源'] == '阳历'])
        from_lunar = len(df[df['生日来源'] == '阴历'])

        print(f"\n统计信息:")
        print(f"- 总记录数: {total}")
        print(f"  - 来自阳历生日: {from_solar}")
        print(f"  - 来自阴历生日: {from_lunar}")
        print(f"- 无生日信息的记录: {total - from_solar - from_lunar}")
        
        for year in years:
            col_name = f'{year}年阳历生日'
            has_birthday = len(df[df[col_name].notna()])
            print(f"- {year}年有生日的记录: {has_birthday}")

        return df

    except Exception as e:
        print(f"处理过程中出错: {e}")
        raise


def set_column_width(worksheet, df, column_name, width):
    """
    设置指定列的宽度
    
    Args:
        worksheet: openpyxl工作表对象
        df: DataFrame数据
        column_name: 要设置宽度的列名
        width: 列宽值
    """
    if column_name in df.columns:
        col_idx = df.columns.get_loc(column_name) + 1  # Excel列索引从1开始
        # 将列索引转换为Excel列字母（支持任意列数）
        col_letter = ''
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            col_letter = chr(65 + remainder) + col_letter
        worksheet.column_dimensions[col_letter].width = width


def split_excel_by_month(input_file, target_year, output_file=None):
    """
    将Excel文件按月份拆分成12个工作表（Sheet），保存在同一个Excel文件中
    
    Args:
        input_file: 输入的Excel文件路径
        target_year: 目标年份
        output_file: 输出文件路径，默认为自动生成
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(input_file)
        print(f"读取到 {len(df)} 条记录")
        
        # 获取生日显示列的名称
        birthday_col = f'{target_year}年公历生日_显示'
        if birthday_col not in df.columns:
            print(f"错误: 找不到列 '{birthday_col}'")
            return
        
        # 提取月份信息
        def extract_month(date_str):
            """从日期字符串中提取月份"""
            if pd.isna(date_str) or date_str == '未设置':
                return None
            try:
                # 尝试解析日期格式 YYYY-MM-DD
                if isinstance(date_str, str):
                    parts = date_str.split('-')
                    if len(parts) >= 2:
                        return int(parts[1])
                elif isinstance(date_str, (date, datetime)):
                    return date_str.month
            except:
                pass
            return None
        
        df['月份'] = df[birthday_col].apply(extract_month)
        
        # 生成输出文件名称
        if output_file is None:
            base_name = input_file.replace('.xlsx', '').replace('.xls', '')
            output_file = f"{base_name}_{target_year}年公历生日.xlsx"
        
        print(f"\n开始按月份拆分到不同工作表...")
        print("=" * 80)
        
        # 使用 ExcelWriter 将所有月份写入同一个Excel文件
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 先写入完整数据到第一个Sheet
            if '月份' in df.columns:
                df_without_temp = df.drop(columns=['月份'])
            else:
                df_without_temp = df
            df_without_temp.to_excel(writer, sheet_name='全年汇总', index=False)
            print(f"✓ 全年汇总: {len(df):3d} 人")
            
            # 按月份分组，写入12个月份的Sheet
            month_stats = []
            for month in range(1, 13):
                # 筛选该月份的记录
                month_df = df[df['月份'] == month].copy()
                
                # 删除临时的'月份'列
                if '月份' in month_df.columns:
                    month_df = month_df.drop(columns=['月份'])
                
                # Sheet名称格式：01月、02月...12月
                sheet_name = f"{month:02d}月"
                
                # 保存该月份的数据
                if len(month_df) > 0:
                    month_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    month_stats.append({
                        '月份': month,
                        '人数': len(month_df)
                    })
                    print(f"✓ {sheet_name}: {len(month_df):3d} 人")
                else:
                    # 即使没有数据也创建空Sheet
                    empty_df = pd.DataFrame()
                    empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  {sheet_name}:   0 人")
        
        print("=" * 80)
        print(f"\n拆分完成！文件已保存: {output_file}")
        print(f"共生成 {13} 个工作表（1个全年汇总 + 12个月份）")
        
        # 统计信息
        total_with_birthday = sum(stat['人数'] for stat in month_stats)
        print(f"\n统计信息:")
        print(f"- 有生日信息的总人数: {total_with_birthday}")
        print(f"- 无生日信息的人数: {len(df) - total_with_birthday}")
        print(f"- 原始文件总人数: {len(df)}")
        
        # 显示季度统计
        print(f"\n季度分布:")
        q1 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [1,2,3])
        q2 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [4,5,6])
        q3 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [7,8,9])
        q4 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [10,11,12])
        print(f"  Q1 (1-3月): {q1} 人")
        print(f"  Q2 (4-6月): {q2} 人")
        print(f"  Q3 (7-9月): {q3} 人")
        print(f"  Q4 (10-12月): {q4} 人")
        
        return output_file
        
    except Exception as e:
        print(f"拆分过程中出错: {e}")
        import traceback
        traceback.print_exc()
        raise


def process_excel_file_by_year(input_file, target_year, output_file=None, split_by_month=False):
    """
    处理Excel文件，根据指定年份导出该年度的公历生日
    
    Args:
        input_file: 输入Excel文件路径
        target_year: 目标年份（例如 2026）
        output_file: 输出Excel文件路径，默认为自动生成
        split_by_month: 是否按月份拆分成子表
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(input_file)

        print(f"读取到 {len(df)} 条记录")
        print(f"列名: {df.columns.tolist()}")
        print(f"\n正在计算 {target_year} 年度生日...")

        # 确保必要的列存在
        required_columns = ['阳历生日', '阴历生日']
        for col in required_columns:
            if col not in df.columns:
                print(f"警告: 缺少必要列 '{col}'，将创建空列")
                df[col] = None

        # 转换阳历生日列为日期类型
        if '阳历生日' in df.columns:
            df['阳历生日'] = pd.to_datetime(df['阳历生日'], errors='coerce')

        # 计算目标年份的公历生日列
        col_name = f'{target_year}年公历生日'
        
        def calculate_year_birthday(row):
            solar_birthday = row.get('阳历生日')
            lunar_birthday_str = row.get('阴历生日')
            
            # 情况1：有阳历生日 - 直接转换到目标年份
            if pd.notna(solar_birthday) and solar_birthday not in ['', 'NaT', None]:
                try:
                    if isinstance(solar_birthday, (date, datetime)):
                        # 处理2月29日等特殊日期
                        if solar_birthday.month == 2 and solar_birthday.day == 29:
                            if (target_year % 4 == 0 and target_year % 100 != 0) or (target_year % 400 == 0):
                                return date(target_year, 2, 29)
                            else:
                                return date(target_year, 2, 28)
                        return date(target_year, solar_birthday.month, solar_birthday.day)
                except:
                    pass
            
            # 情况2：有阴历生日 - 转换为公历（自动处理腊月跨年）
            if pd.notna(lunar_birthday_str) and lunar_birthday_str not in ['', 'NaT', None]:
                return convert_lunar_to_target_year_solar(lunar_birthday_str, target_year)
            
            # 情况3：都没有
            return None
        
        df[col_name] = df.apply(calculate_year_birthday, axis=1)
        
        # 格式化生日为字符串（便于Excel显示）
        display_col = f'{col_name}_显示'
        df[display_col] = df[col_name].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '未设置'
        )

        # 添加备注列说明来源
        def get_source(row):
            solar = row.get('阳历生日')
            lunar = row.get('阴历生日')

            if pd.notna(solar) and solar not in ['', 'NaT', None]:
                return '阳历'
            elif pd.notna(lunar) and lunar not in ['', 'NaT', None]:
                return '阴历'
            else:
                return '无'

        df['生日来源'] = df.apply(get_source, axis=1)

        # 保存结果（只包含必要的列）
        if output_file is None:
            output_file = input_file.replace('.xlsx', f'_{target_year}年公历生日.xlsx')

        if split_by_month:
            # 按月份拆分到同一个Excel文件的不同Sheet中
            # 先生成完整的DataFrame（包含月份列）
            df_with_month = df.copy()
            
            def extract_month_from_date(date_obj):
                """从日期对象中提取月份"""
                if pd.isna(date_obj):
                    return None
                try:
                    if isinstance(date_obj, (date, datetime)):
                        return date_obj.month
                except:
                    pass
                return None
            
            df_with_month['月份'] = df_with_month[col_name].apply(extract_month_from_date)
            
            # 生成输出文件名称
            if output_file is None:
                output_file = input_file.replace('.xlsx', f'_{target_year}年公历生日.xlsx')
            
            print(f"\n开始按月份拆分到不同工作表...")
            print("=" * 80)
            
            # 使用 ExcelWriter 将所有月份写入同一个Excel文件
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 先写入完整数据到第一个Sheet（删除内部计算用的datetime列和临时月份列）
                cols_to_save = [col for col in df_with_month.columns if col not in [col_name, '月份']]
                df_with_month[cols_to_save].to_excel(writer, sheet_name='全年汇总', index=False)
                
                # 设置列宽：阳历生日=20, 阴历生日=15, 2026年公历生日_显示=20
                worksheet = writer.sheets['全年汇总']
                set_column_width(worksheet, df_with_month[cols_to_save], '阳历生日', 20)
                set_column_width(worksheet, df_with_month[cols_to_save], '阴历生日', 15)
                birthday_display_col = f'{target_year}年公历生日_显示'
                set_column_width(worksheet, df_with_month[cols_to_save], birthday_display_col, 20)
                
                print(f"✓ 全年汇总: {len(df_with_month):3d} 人")
                
                # 按月份分组，写入12个月份的Sheet
                month_stats = []
                for month in range(1, 13):
                    # 筛选该月份的记录
                    month_df = df_with_month[df_with_month['月份'] == month].copy()
                    
                    # 删除临时的'月份'列和datetime列
                    cols_for_sheet = [col for col in month_df.columns if col not in [col_name, '月份']]
                    month_df_clean = month_df[cols_for_sheet]
                    
                    # Sheet名称格式：01月、02月...12月
                    sheet_name = f"{month:02d}月"
                    
                    # 保存该月份的数据
                    if len(month_df) > 0:
                        month_df_clean.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 设置列宽：阳历生日=20, 阴历生日=15, 2026年公历生日_显示=20
                        worksheet = writer.sheets[sheet_name]
                        set_column_width(worksheet, month_df_clean, '阳历生日', 20)
                        set_column_width(worksheet, month_df_clean, '阴历生日', 15)
                        set_column_width(worksheet, month_df_clean, birthday_display_col, 20)
                        
                        month_stats.append({
                            '月份': month,
                            '人数': len(month_df)
                        })
                        print(f"✓ {sheet_name}: {len(month_df):3d} 人")
                    else:
                        # 即使没有数据也创建空Sheet
                        empty_df = pd.DataFrame()
                        empty_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        print(f"  {sheet_name}:   0 人")
            
            print("=" * 80)
            print(f"\n拆分完成！文件已保存: {output_file}")
            print(f"共生成 {13} 个工作表（1个全年汇总 + 12个月份）")
            
            # 统计信息
            total_with_birthday = sum(stat['人数'] for stat in month_stats)
            print(f"\n统计信息:")
            print(f"- 有生日信息的总人数: {total_with_birthday}")
            print(f"- 无生日信息的人数: {len(df) - total_with_birthday}")
            print(f"- 原始文件总人数: {len(df)}")
            
            # 显示季度统计
            print(f"\n季度分布:")
            q1 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [1,2,3])
            q2 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [4,5,6])
            q3 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [7,8,9])
            q4 = sum(stat['人数'] for stat in month_stats if stat['月份'] in [10,11,12])
            print(f"  Q1 (1-3月): {q1} 人")
            print(f"  Q2 (4-6月): {q2} 人")
            print(f"  Q3 (7-9月): {q3} 人")
            print(f"  Q4 (10-12月): {q4} 人")
            
            return output_file
        else:
            # 只保存完整文件（单个工作表）
            if output_file is None:
                output_file = input_file.replace('.xlsx', f'_{target_year}年公历生日.xlsx')
            
            cols_to_save = [col for col in df.columns if col != col_name]
            df[cols_to_save].to_excel(output_file, index=False)
            
            # 设置列宽：阳历生日=20, 阴历生日=15, {target_year}年公历生日_显示=20
            from openpyxl import load_workbook
            wb = load_workbook(output_file)
            ws = wb.active
            set_column_width(ws, df[cols_to_save], '阳历生日', 20)
            set_column_width(ws, df[cols_to_save], '阴历生日', 15)
            display_col_name = f'{target_year}年公历生日_显示'
            set_column_width(ws, df[cols_to_save], display_col_name, 20)
            wb.save(output_file)
        
        print(f"\n处理完成！结果已保存到: {output_file}")

        # 统计信息
        total = len(df)
        has_birthday = len(df[df[col_name].notna()])
        from_solar = len(df[df['生日来源'] == '阳历'])
        from_lunar = len(df[df['生日来源'] == '阴历'])

        print(f"\n=== {target_year}年度生日统计 ===")
        print(f"总记录数: {total}")
        print(f"有生日信息的记录: {has_birthday}")
        print(f"  - 来自阳历生日: {from_solar}")
        print(f"  - 来自阴历生日: {from_lunar}")
        print(f"无生日信息的记录: {total - has_birthday}")

        return df

    except Exception as e:
        print(f"处理过程中出错: {e}")
        raise


def excel_integration():
    """
    Excel集成版本，可以直接在Excel中调用
    """
    try:
        # 连接到当前Excel工作簿
        wb = xw.Book.caller()
        sheet = wb.sheets[0]

        # 获取数据
        data_range = sheet.range('A1').expand('table')
        headers = data_range.rows[0].value

        # 检查必要列
        if '阳历生日' not in headers or '阴历生日' not in headers:
            raise ValueError("Excel表格缺少必要的'阳历生日'或'阴历生日'列")

        # 读取数据到DataFrame
        df = pd.DataFrame(data_range.value[1:], columns=headers)

        # 转换阳历生日
        if '阳历生日' in df.columns:
            # 尝试多种日期格式
            df['阳历生日'] = pd.to_datetime(df['阳历生日'], errors='coerce')

        # 计算本年生日
        print("正在计算本年生日...")
        df['本年生日'] = df.apply(calculate_this_year_birthday, axis=1)

        # 准备写入Excel
        result_col = len(headers) + 1
        sheet.range((1, result_col)).value = '本年生日'
        sheet.range((1, result_col + 1)).value = '生日来源'

        # 写入结果
        for i, row in df.iterrows():
            row_idx = i + 2  # 从第2行开始（跳过标题行）

            birthday = row['本年生日']
            source = '阳历' if pd.notna(row.get('阳历生日')) and row.get('阳历生日') not in ['', 'NaT', None] else \
                ('阴历' if pd.notna(row.get('阴历生日')) and row.get('阴历生日') not in ['', 'NaT', None] else '无')

            if pd.notna(birthday):
                sheet.range((row_idx, result_col)).value = birthday
                sheet.range((row_idx, result_col)).number_format = 'yyyy-mm-dd'
            else:
                sheet.range((row_idx, result_col)).value = '未设置'

            sheet.range((row_idx, result_col + 1)).value = source

        # 自动调整列宽
        sheet.range((1, result_col), (len(df) + 1, result_col + 1)).columns.autofit()

        print("Excel更新完成！")

    except Exception as e:
        print(f"Excel集成出错: {e}")
        raise


# 命令行使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='员工生日转换工具 - 按指定年份导出公历生日')
    parser.add_argument('input_file', help='输入Excel文件路径')
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                       help=f'目标年份（默认: {datetime.now().year}）')
    parser.add_argument('-o', '--output', help='输出Excel文件路径（可选，自动生成）')
    parser.add_argument('--excel-mode', action='store_true', help='Excel集成模式')
    parser.add_argument('--multi-year', action='store_true', help='多年份模式（2026-2028）')
    parser.add_argument('--years', nargs='+', type=int, default=[2026, 2027, 2028], 
                       help='多年份模式的年份列表，默认为 2026 2027 2028')
    parser.add_argument('--split-month', action='store_true', help='按月份拆分成12个子表')

    args = parser.parse_args()

    if args.excel_mode:
        excel_integration()
    elif args.multi_year:
        process_excel_file_multi_year(args.input_file, args.output, args.years)
    else:
        # 默认模式：按指定年份导出公历生日
        print(f"\n{'='*60}")
        print(f"员工生日转换工具 - {args.year}年度")
        print(f"{'='*60}\n")
        process_excel_file_by_year(args.input_file, args.year, args.output, args.split_month)