<?php
// wage.php - 工资管理（支持五个工资表，增删改查，项目名称可配置）
require_once 'common.php';
check_login();
$conn = db_connect();

$action = isset($_GET['action']) ? $_GET['action'] : 'list';
$table_id = isset($_GET['table']) ? intval($_GET['table']) : 1;
if ($table_id < 1 || $table_id > 5) $table_id = 1;

// 获取工资表配置（标题和项目名称）
function getWageConfig($conn, $table_id) {
    $res = $conn->query("SELECT * FROM wage_config WHERE table_id = $table_id");
    if ($res->num_rows == 0) {
        // 默认配置（防止表为空）
        $default = [
            '标题' => "教员工资表(表$table_id)",
            '项目1名称' => '基本工资', '项目2名称' => '岗位津贴', '项目3名称' => '绩效工资',
            '项目4名称' => '工龄工资', '项目5名称' => '其他补贴', '项目6名称' => '养老保险', '项目7名称' => '实发合计'
        ];
        return $default;
    }
    return $res->fetch_assoc();
}

// 更新合计（根据项目1-7自动计算合计 = 项目1+...+项目5 - 项目6，然后存储到合计字段）
function updateTotal($conn, $id) {
    $res = $conn->query("SELECT 项目1,项目2,项目3,项目4,项目5,项目6 FROM wage_records WHERE id = $id");
    if ($row = $res->fetch_assoc()) {
        $total = $row['项目1'] + $row['项目2'] + $row['项目3'] + $row['项目4'] + $row['项目5'] - $row['项目6'];
        $conn->query("UPDATE wage_records SET 合计 = $total WHERE id = $id");
    }
}

// ======================= 列表 =======================
if ($action == 'list') {
    $config = getWageConfig($conn, $table_id);
    $records = $conn->query("SELECT * FROM wage_records WHERE table_id = $table_id ORDER BY id");
    // 计算所有记录的项目小计和总合计
    $sum = array_fill(1, 7, 0);
    $totalSum = 0;
    $rows = [];
    while ($row = $records->fetch_assoc()) {
        $rows[] = $row;
        for ($i=1; $i<=7; $i++) {
            $sum[$i] += $row["项目$i"];
        }
        $totalSum += $row['合计'];
    }
?>
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>工资管理</title></head>
<body>
<h2><?php echo htmlspecialchars($config['标题']); ?></h2>
<p>
    <?php for ($i=1; $i<=5; $i++): ?>
        <a href="?action=list&table=<?php echo $i; ?>" <?php if($i==$table_id) echo 'style="font-weight:bold;"'; ?>>工资表<?php echo $i; ?></a> |
    <?php endfor; ?>
    <a href="?action=add&table=<?php echo $table_id; ?>">+ 添加记录</a>
    <a href="?action=title&table=<?php echo $table_id; ?>">标题/项目设置</a>
</p>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
    <tr bgcolor="#ccc">
        <th>姓名</th>
        <th><?php echo htmlspecialchars($config['项目1名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目2名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目3名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目4名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目5名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目6名称']); ?></th>
        <th><?php echo htmlspecialchars($config['项目7名称']); ?></th>
        <th>操作</th>
    </tr>
    <?php foreach ($rows as $row): ?>
    <tr>
        <td><?php echo htmlspecialchars($row['姓名']); ?></td>
        <td><?php echo number_format($row['项目1'], 2); ?></td>
        <td><?php echo number_format($row['项目2'], 2); ?></td>
        <td><?php echo number_format($row['项目3'], 2); ?></td>
        <td><?php echo number_format($row['项目4'], 2); ?></td>
        <td><?php echo number_format($row['项目5'], 2); ?></td>
        <td><?php echo number_format($row['项目6'], 2); ?></td>
        <td><?php echo number_format($row['合计'], 2); ?></td>
        <td>
            <a href="?action=edit&id=<?php echo $row['id']; ?>&table=<?php echo $table_id; ?>">编辑</a>
            <a href="?action=delete&id=<?php echo $row['id']; ?>&table=<?php echo $table_id; ?>" onclick="return confirm('确认删除？')">删除</a>
        </td>
    </tr>
    <?php endforeach; ?>
    <?php if (count($rows) > 0): ?>
    <tr bgcolor="#e0e0e0">
        <th>合计</th>
        <th><?php echo number_format($sum[1], 2); ?></th>
        <th><?php echo number_format($sum[2], 2); ?></th>
        <th><?php echo number_format($sum[3], 2); ?></th>
        <th><?php echo number_format($sum[4], 2); ?></th>
        <th><?php echo number_format($sum[5], 2); ?></th>
        <th><?php echo number_format($sum[6], 2); ?></th>
        <th><?php echo number_format($totalSum, 2); ?></th>
        <th></th>
    </tr>
    <?php endif; ?>
</table>
<p><a href="student.php?action=list">返回主菜单</a></p>
</body></html>
<?php
}
// ======================= 添加记录 =======================
elseif ($action == 'add') {
    $config = getWageConfig($conn, $table_id);
    if ($_POST) {
        $name = $conn->real_escape_string($_POST['姓名']);
        $p1 = floatval($_POST['项目1']);
        $p2 = floatval($_POST['项目2']);
        $p3 = floatval($_POST['项目3']);
        $p4 = floatval($_POST['项目4']);
        $p5 = floatval($_POST['项目5']);
        $p6 = floatval($_POST['项目6']);
        $total = $p1 + $p2 + $p3 + $p4 + $p5 - $p6;
        $sql = "INSERT INTO wage_records (table_id, 姓名, 项目1, 项目2, 项目3, 项目4, 项目5, 项目6, 合计)
                VALUES ($table_id, '$name', $p1, $p2, $p3, $p4, $p5, $p6, $total)";
        if ($conn->query($sql)) {
            show_msg("添加成功", "wage.php?action=list&table=$table_id");
        } else {
            show_msg("添加失败：" . $conn->error, "wage.php?action=add&table=$table_id");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>添加工资记录</title></head>
    <body>
    <h2>添加工资记录 - <?php echo htmlspecialchars($config['标题']); ?></h2>
    <form method="post">
    <table border="0">
        <tr><td>姓名：</td><td><input type="text" name="姓名" required></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目1名称']); ?>：</td><td><input type="text" name="项目1" value="0"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目2名称']); ?>：</td><td><input type="text" name="项目2" value="0"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目3名称']); ?>：</td><td><input type="text" name="项目3" value="0"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目4名称']); ?>：</td><td><input type="text" name="项目4" value="0"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目5名称']); ?>：</td><td><input type="text" name="项目5" value="0"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目6名称']); ?>：</td><td><input type="text" name="项目6" value="0"></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存"> <a href="wage.php?action=list&table=<?php echo $table_id; ?>">取消</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 编辑记录 =======================
elseif ($action == 'edit') {
    $id = intval($_GET['id']);
    $config = getWageConfig($conn, $table_id);
    $res = $conn->query("SELECT * FROM wage_records WHERE id = $id");
    if ($res->num_rows == 0) show_msg("记录不存在", "wage.php?action=list&table=$table_id");
    $row = $res->fetch_assoc();
    if ($_POST) {
        $name = $conn->real_escape_string($_POST['姓名']);
        $p1 = floatval($_POST['项目1']);
        $p2 = floatval($_POST['项目2']);
        $p3 = floatval($_POST['项目3']);
        $p4 = floatval($_POST['项目4']);
        $p5 = floatval($_POST['项目5']);
        $p6 = floatval($_POST['项目6']);
        $total = $p1 + $p2 + $p3 + $p4 + $p5 - $p6;
        $sql = "UPDATE wage_records SET 姓名='$name', 项目1=$p1, 项目2=$p2, 项目3=$p3, 项目4=$p4, 项目5=$p5, 项目6=$p6, 合计=$total WHERE id=$id";
        if ($conn->query($sql)) {
            show_msg("修改成功", "wage.php?action=list&table=$table_id");
        } else {
            show_msg("修改失败：" . $conn->error, "wage.php?action=edit&id=$id&table=$table_id");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>编辑工资记录</title></head>
    <body>
    <h2>编辑工资记录 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post">
    <table border="0">
        <tr><td>姓名：</td><td><input type="text" name="姓名" value="<?php echo htmlspecialchars($row['姓名']); ?>" required></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目1名称']); ?>：</td><td><input type="text" name="项目1" value="<?php echo $row['项目1']; ?>"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目2名称']); ?>：</td><td><input type="text" name="项目2" value="<?php echo $row['项目2']; ?>"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目3名称']); ?>：</td><td><input type="text" name="项目3" value="<?php echo $row['项目3']; ?>"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目4名称']); ?>：</td><td><input type="text" name="项目4" value="<?php echo $row['项目4']; ?>"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目5名称']); ?>：</td><td><input type="text" name="项目5" value="<?php echo $row['项目5']; ?>"></td></tr>
        <tr><td><?php echo htmlspecialchars($config['项目6名称']); ?>：</td><td><input type="text" name="项目6" value="<?php echo $row['项目6']; ?>"></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存"> <a href="wage.php?action=list&table=<?php echo $table_id; ?>">取消</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 删除记录 =======================
elseif ($action == 'delete') {
    $id = intval($_GET['id']);
    $conn->query("DELETE FROM wage_records WHERE id = $id");
    show_msg("已删除", "wage.php?action=list&table=$table_id");
}
// ======================= 标题/项目设置 =======================
elseif ($action == 'title') {
    $config = getWageConfig($conn, $table_id);
    if ($_POST) {
        $title = $conn->real_escape_string($_POST['标题']);
        $p1 = $conn->real_escape_string($_POST['项目1名称']);
        $p2 = $conn->real_escape_string($_POST['项目2名称']);
        $p3 = $conn->real_escape_string($_POST['项目3名称']);
        $p4 = $conn->real_escape_string($_POST['项目4名称']);
        $p5 = $conn->real_escape_string($_POST['项目5名称']);
        $p6 = $conn->real_escape_string($_POST['项目6名称']);
        $p7 = $conn->real_escape_string($_POST['项目7名称']);
        $sql = "UPDATE wage_config SET 标题='$title', 项目1名称='$p1', 项目2名称='$p2', 项目3名称='$p3', 项目4名称='$p4',
                项目5名称='$p5', 项目6名称='$p6', 项目7名称='$p7' WHERE table_id=$table_id";
        if ($conn->query($sql)) {
            show_msg("设置保存成功", "wage.php?action=list&table=$table_id");
        } else {
            show_msg("保存失败：" . $conn->error, "wage.php?action=title&table=$table_id");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>工资表设置</title></head>
    <body>
    <h2>设置工资表 (表<?php echo $table_id; ?>)</h2>
    <form method="post">
    <table border="0">
        <tr><td>表格标题：</td><td><input type="text" name="标题" size="40" value="<?php echo htmlspecialchars($config['标题']); ?>"></td></tr>
        <tr><td><?php echo $config['项目1名称']; ?>（项目1）：</td><td><input type="text" name="项目1名称" value="<?php echo htmlspecialchars($config['项目1名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目2名称']; ?>（项目2）：</td><td><input type="text" name="项目2名称" value="<?php echo htmlspecialchars($config['项目2名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目3名称']; ?>（项目3）：</td><td><input type="text" name="项目3名称" value="<?php echo htmlspecialchars($config['项目3名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目4名称']; ?>（项目4）：</td><td><input type="text" name="项目4名称" value="<?php echo htmlspecialchars($config['项目4名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目5名称']; ?>（项目5）：</td><td><input type="text" name="项目5名称" value="<?php echo htmlspecialchars($config['项目5名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目6名称']; ?>（项目6）：</td><td><input type="text" name="项目6名称" value="<?php echo htmlspecialchars($config['项目6名称']); ?>"></td></tr>
        <tr><td><?php echo $config['项目7名称']; ?>（合计）：</td><td><input type="text" name="项目7名称" value="<?php echo htmlspecialchars($config['项目7名称']); ?>"></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存设置"> <a href="wage.php?action=list&table=<?php echo $table_id; ?>">返回</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
?>