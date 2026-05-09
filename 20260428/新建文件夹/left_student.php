<?php
// left_student.php - 离校人员名单（整合转退+毕业）
require_once 'common.php';
check_login();
$conn = db_connect();

// 辅助函数：获取班级列表（用于下拉框）
function getClassOptions($conn, $selected = '') {
    $res = $conn->query("SELECT 所在班级 FROM 班级表 ORDER BY 所在班级");
    $html = '';
    while ($row = $res->fetch_assoc()) {
        $sel = ($selected == $row['所在班级']) ? 'selected' : '';
        $html .= "<option value=\"" . htmlspecialchars($row['所在班级']) . "\" $sel>" . htmlspecialchars($row['所在班级']) . "</option>";
    }
    return $html;
}

$type = isset($_GET['type']) ? $_GET['type'] : 'all'; // all:全部, transfer:转退, graduate:毕业
$keyword = isset($_GET['keyword']) ? trim($_GET['keyword']) : '';
$where = "1=1";
if ($keyword) $where .= " AND (学号 LIKE '%$keyword%' OR 姓名 LIKE '%$keyword%')";
if ($type == 'transfer') $where .= " AND 离校原因 NOT LIKE '%毕业%'";
elseif ($type == 'graduate') $where .= " AND 离校原因 LIKE '%毕业%'";

$sql = "SELECT 学号, 姓名, 性别, 所在班级, 离校时间, 离校原因 FROM 离校人员名单 WHERE $where ORDER BY 离校时间 DESC";
$res = $conn->query($sql);
if (!$res) die("查询失败：" . $conn->error);
?>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>离校人员名单</title></head>
<body>
<h2>离校人员名单</h2>
<p>
    <a href="?type=all" <?php if($type=='all') echo 'style="font-weight:bold;"'; ?>>全部</a> |
    <a href="?type=transfer" <?php if($type=='transfer') echo 'style="font-weight:bold;"'; ?>>转退学生</a> |
    <a href="?type=graduate" <?php if($type=='graduate') echo 'style="font-weight:bold;"'; ?>>毕业学生</a>
</p>
<form method="get" style="margin-bottom:10px;">
    <input type="hidden" name="type" value="<?php echo $type; ?>">
    姓名/学号: <input type="text" name="keyword" value="<?php echo htmlspecialchars($keyword); ?>">
    <input type="submit" value="搜索">
    <a href="left_student.php?action=add" style="margin-left:20px;">+ 添加离校人员</a>
</form>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
    <tr bgcolor="#ccc">
        <th>学号</th><th>姓名</th><th>性别</th><th>原班级</th><th>离校时间</th><th>离校原因</th><th>操作</th>
    </tr>
<?php while ($row = $res->fetch_assoc()): ?>
    <tr>
        <td><?php echo $row['学号']; ?></td>
        <td><?php echo htmlspecialchars($row['姓名']); ?></td>
        <td><?php echo $row['性别']; ?></td>
        <td><?php echo htmlspecialchars($row['所在班级']); ?></td>
        <td><?php echo $row['离校时间']; ?></td>
        <td><?php echo htmlspecialchars($row['离校原因']); ?></td>
        <td>
            <a href="student.php?action=view&id=<?php echo $row['学号']; ?>&from=left" target="_blank">查看详情</a>
            <?php if ($row['离校原因'] != '毕业'): ?>
                | <a href="left_student.php?action=restore&id=<?php echo $row['学号']; ?>" onclick="return confirm('恢复该生学籍？将回到原班级')">恢复学籍</a>
            <?php endif; ?>
            | <a href="left_student.php?action=delete&id=<?php echo $row['学号']; ?>" onclick="return confirm('永久删除记录，不可恢复！')">删除</a>
        </td>
    </tr>
<?php endwhile; ?>
</table>
<p><a href="student.php?action=list">返回在校学生列表</a></p>

<!-- 添加离校人员表单 -->
<?php if (isset($_GET['action']) && $_GET['action'] == 'add'): ?>
    <h3>添加离校人员</h3>
    <form method="post" action="left_student.php">
        <input type="hidden" name="action" value="add_submit">
        <table border="0">
            <tr><td>学号：</td><td><input type="text" name="学号" required></td></tr>
            <tr><td>姓名：</td><td><input type="text" name="姓名" required></td></tr>
            <tr><td>性别：</td><td><select name="性别"><option>男</option><option>女</option></select></td></tr>
            <tr><td>所在班级：</td><td><select name="所在班级"><?php echo getClassOptions($conn); ?></select></td></tr>
            <tr><td>离校时间：</td><td><input type="date" name="离校时间" value="<?php echo date('Y-m-d'); ?>" required></td></tr>
            <tr><td>离校原因：</td><td>
                <input type="text" name="离校原因" list="reason_list" style="width:200px;">
                <datalist id="reason_list">
                    <option>转学</option><option>退学</option><option>休学</option><option>毕业</option><option>开除</option><option>其他</option>
                </datalist>
                （可手动输入或选择）
            </td></tr>
            <tr><td colspan="2"><input type="submit" value="添加"> <a href="left_student.php">取消</a></td></tr>
        </table>
    </form>
<?php endif; ?>
</body>
</html>
<?php
// 处理添加提交
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['action']) && $_POST['action'] == 'add_submit') {
    $xh = intval($_POST['学号']);
    $xm = $conn->real_escape_string($_POST['姓名']);
    $xb = $_POST['性别'];
    $bj = $conn->real_escape_string($_POST['所在班级']);
    $lxsj = $_POST['离校时间'];
    $lxyy = $conn->real_escape_string($_POST['离校原因']);
    $sql = "INSERT INTO 离校人员名单 (学号,姓名,性别,所在班级,离校时间,离校原因) VALUES ($xh,'$xm','$xb','$bj','$lxsj','$lxyy')";
    if ($conn->query($sql)) {
        show_msg("添加成功", "left_student.php");
    } else {
        show_msg("添加失败：" . $conn->error, "left_student.php?action=add");
    }
}

// 恢复学籍
if (isset($_GET['action']) && $_GET['action'] == 'restore') {
    $id = intval($_GET['id']);
    $check = $conn->query("SELECT 学号 FROM 学籍表 WHERE 学号 = $id");
    if ($check->num_rows > 0) {
        show_msg("该学号已在学籍表中，无法恢复（学号冲突）", "left_student.php");
    }
    $conn->query("INSERT INTO 学籍表 (学号,姓名,性别,民族,出生日期,入学日期,所在班级,班内职务,家庭住址,联系电话,户籍,籍贯,
                   家长A,家长A姓名,家长A单位,家长A电话,家长B,家长B姓名,家长B单位,家长B电话,照片,本学期评语,综合评语,
                   期中1,期中2,期中3,期中4,期中5,期中6,期中7,期中8,期中9,期中10,
                   期末1,期末2,期末3,期末4,期末5,期末6,期末7,期末8,期末9,期末10)
                  SELECT 学号,姓名,性别,民族,出生日期,入学日期,所在班级,班内职务,家庭住址,联系电话,户籍,籍贯,
                   家长A,家长A姓名,家长A单位,家长A电话,家长B,家长B姓名,家长B单位,家长B电话,照片,本学期评语,综合评语,
                   期中1,期中2,期中3,期中4,期中5,期中6,期中7,期中8,期中9,期中10,
                   期末1,期末2,期末3,期末4,期末5,期末6,期末7,期末8,期末9,期末10
                  FROM 离校人员名单 WHERE 学号 = $id");
    $conn->query("DELETE FROM 离校人员名单 WHERE 学号 = $id");
    show_msg("恢复学籍成功", "left_student.php");
}

// 删除记录
if (isset($_GET['action']) && $_GET['action'] == 'delete') {
    $id = intval($_GET['id']);
    $conn->query("DELETE FROM 离校人员名单 WHERE 学号 = $id");
    show_msg("已删除", "left_student.php");
}
?>