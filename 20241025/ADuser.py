from ldap3 import Server, Connection, ALL, NTLM
from ldap3.utils.dn import parse_dn
import pandas as pd


def normalize_dn(dn):
    """Normalize the DN by parsing and reformatting it."""
    parsed_dn = parse_dn(dn)
    sorted_parsed_dn = sorted(parsed_dn, key=lambda x: x[0])  # Sort by attribute type
    normalized_dn = ','.join(['='.join([part[0], part[1]]) for part in sorted_parsed_dn])
    return normalized_dn


def compare_dns(dn1, dn2):
    """Compare two DNs after normalizing them."""
    normalized_dn1 = normalize_dn(dn1)
    normalized_dn2 = normalize_dn(dn2)
    return normalized_dn1.lower() == normalized_dn2.lower()


def checkWmsUserStatus(admin_c, row):
    # 账户启用标志
    enabled_user_flag = [512, 544, 66048, 262656]
    # 账户禁用标志
    disabled_user_flag = [514, 546, 66050, 66080, 66082]
    adDn = row["用户名"]
    hostname = row["登录 ID"]
    admin_c.search(search_base=search_base, search_filter='(sAMAccountName=%s)' % hostname,
                   attributes=['distinguishedName', 'description', 'userAccountControl', 'userWorkstations',
                               'lockoutTime'])

    if len(admin_c.entries) > 0:
        adUserInfor = admin_c.entries[0]
        entry_dn = adUserInfor["distinguishedName"].value

        # 比较两个dn是否一致
        if not compare_dns(entry_dn, adDn):
            return False

        if adUserInfor['lockoutTime'].value is not None and str(
                adUserInfor['lockoutTime'].value) != '1601-01-01 00:00:00+00:00':
            return False

        # 判断是否禁用 1.状态在禁用状态  2.或者 状态不在 启用状态
        if (adUserInfor['userAccountControl'] in disabled_user_flag) or not (
                adUserInfor['userAccountControl'] in enabled_user_flag):
            return False

        if adUserInfor['description'].value is not None and "禁" in adUserInfor["description"].value:
            return False

        # 允许登录所有计算机用户
        if adUserInfor['userWorkstations'] is not None:
            return True

        # 设置允许登录域控yk01 与 yk02 的用户
        if adUserInfor['userWorkstations'].value is not None and (
                "yk01" in adUserInfor["userWorkstations"].value or "yk02" in adUserInfor["userWorkstations"].value):
            return True

        # 未找到
        return False
    # 未找到
    return False


if __name__ == '__main__':
    file_path = '*.xlsx'
    server = Server('172.28.*.*', get_info=ALL)
    search_base = "DC=*,DC=com"
    admin_c = Connection(server, user='*', password='*', auto_bind=True, authentication=NTLM)
    # pdf 读取xlsx 文件 seet 标签为 USER_DATA  跳过第一行
    df = pd.read_excel(file_path, sheet_name='USER_DATA', skiprows=1)

    results = []

    for index, row in df.iterrows():
        # 检查满足条件用户
        if checkWmsUserStatus(admin_c, row):
            results.append(row)

    # 写入pd
    result_df = pd.DataFrame(results)
    with pd.ExcelWriter("outfile.xlsx") as writer:
        result_df.to_excel(writer, index=False, sheet_name='Valid Users')

    admin_c.unbind()