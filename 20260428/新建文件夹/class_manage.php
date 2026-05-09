<?php
// class_manage.php - 班级管理（增删改查）
require_once 'common.php';
check_login();
if (!has_perm(3)) die("无权限访问");
$conn = db_connect();

$action = isset($_GET['action']) ? $_GET['action'] : 'list';

// 辅助：获取班级列表（用于下拉）
function getClassList($conn) {
    $res = $conn->query("SELECT 所在班级 FROM 班级表 ORDER BY 所在班级");
    $list = [];
    while ($row = $res->fetch_assoc()) $list[] = $row['所在班级'];
    return $list;
}

// ======================= 列表 =======================
if ($action == 'list') {
    $res = $conn->query("SELECT 所在班级, 班主任, 班级分类 FROM 班级表 ORDER BY 所在班级");
?>
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>班级管理</title></head>
<body>
<h2>班级管理</h2>
<p><a href="class_manage.php?action=add">+ 添加班级</a></p>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
    <tr bgcolor="#ccc"><th>班级名称</th><th>班主任</th><th>班级分类</th><th>操作</th></tr>
<?php while ($row = $res->fetch_assoc()): ?>
    <tr>
        <td><?php echo htmlspecialchars($row['所在班级']); ?></td>
        <td><?php echo htmlspecialchars($row['班主任']); ?></td>
        <td><?php echo $row['班级分类']; ?></td>
        <td>
            <a href="class_manage.php?action=edit&class=<?php echo urlencode($row['所在班级']); ?>">编辑</a>
            <a href="class_manage.php?action=delete&class=<?php echo urlencode($row['所在班级']); ?>" onclick="return confirm('删除班级将同时删除该班级下的所有学生！确定删除？')">删除</a>
         </td>
    </tr>
<?php endwhile; ?>
</table>
<p><a href="class_setup.php">设置班级课程科目</a></p>
</body></html>
<?php
}
// ======================= 添加班级 =======================
elseif ($action == 'add') {
    if ($_POST) {
        $classType = $_POST['班级类型'];
        if ($classType == '通用') {
            $grade = $_POST['年级'];
            $classNum = $_POST['班级序号'];
            $className = $grade . $classNum;
        } else {
            $className = trim($_POST['自设班级名']);
        }
        $teacher = $conn->real_escape_string($_POST['班主任']);
        $category = $classType == '通用' ? '通用' : '自设';
        
        // 检查是否已存在
        $check = $conn->query("SELECT 所在班级 FROM 班级表 WHERE 所在班级 = '$className'");
        if ($check->num_rows > 0) {
            show_msg("班级 [$className] 已存在！", "class_manage.php?action=add");
        }
        $sql = "INSERT INTO 班级表 (所在班级, 班主任, 班级分类) VALUES ('$className', '$teacher', '$category')";
        if ($conn->query($sql)) {
            show_msg("添加成功", "class_manage.php?action=list");
        } else {
            show_msg("添加失败：" . $conn->error, "class_manage.php?action=add");
        }
    }
    // 显示表单
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>添加班级</title>
    <script>
    function toggleClassType() {
        var type = document.querySelector('input[name="班级类型"]:checked').value;
        document.getElementById('通用设置').style.display = (type == '通用') ? 'block' : 'none';
        document.getElementById('自设设置').style.display = (type == '自设') ? 'block' : 'none';
    }
    </script>
    </head>
    <body onload="toggleClassType()">
    <h2>添加班级</h2>
    <form method="post">
    <input type="radio" name="班级类型" value="通用" checked onclick="toggleClassType()"> 通用班级
    <input type="radio" name="班级类型" value="自设" onclick="toggleClassType()"> 自设班级
    <br><br>
    <div id="通用设置">
        年级: <select name="年级">
            <option>一年级</option><option>二年级</option><option>三年级</option>
            <option>四年级</option><option>五年级</option><option>六年级</option>
            <option>初中一年级</option><option>初中二年级</option><option>初中三年级</option>
            <option>高中一年级</option><option>高中二年级</option><option>高中三年级</option>
            <option>幼儿园小班</option><option>幼儿园中班</option><option>幼儿园大班</option>
        </select>
        班级序号: <select name="班级序号">
            <option>1班</option><option>2班</option><option>3班</option><option>4班</option><option>5班</option><option>6班</option><option>7班</option><option>8班</option>
        </select>
    </div>
    <div id="自设设置" style="display:none;">
        班级名称: <input type="text" name="自设班级名" size="30">
    </div>
    <br>
    班主任: <input type="text" name="班主任" required><br><br>
    <input type="submit" value="保存班级">
    <a href="class_manage.php?action=list">返回列表</a>
    </form>
    </body></html>
    <?php
}
// ======================= 编辑班级（班主任+科目） =======================
elseif ($action == 'edit') {
    $className = $_GET['class'];
    if ($_POST) {
        $teacher = $conn->real_escape_string($_POST['班主任']);
        // 科目1-10
        $subjects = [];
        for ($i = 1; $i <= 10; $i++) {
            $subjects[] = "科目$i = '" . $conn->real_escape_string($_POST["科目$i"]) . "'";
        }
        $sql = "UPDATE 班级表 SET 班主任 = '$teacher', " . implode(',', $subjects) . " WHERE 所在班级 = '$className'";
        if ($conn->query($sql)) {
            show_msg("修改成功", "class_manage.php?action=list");
        } else {
            show_msg("修改失败：" . $conn->error, "class_manage.php?action=edit&class=" . urlencode($className));
        }
    }
    $res = $conn->query("SELECT * FROM 班级表 WHERE 所在班级 = '$className'");
    if ($res->num_rows == 0) show_msg("班级不存在", "class_manage.php?action=list");
    $row = $res->fetch_assoc();
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>编辑班级</title></head>
    <body>
    <h2>编辑班级：<?php echo htmlspecialchars($className); ?></h2>
    <form method="post">
    班主任: <input type="text" name="班主任" value="<?php echo htmlspecialchars($row['班主任']); ?>" required><br><br>
    <strong>课程科目设置（最多10科）</strong><br>
    <?php for ($i = 1; $i <= 10; $i++): ?>
        科目<?php echo $i; ?>: <input type="text" name="科目<?php echo $i; ?>" value="<?php echo htmlspecialchars($row["科目$i"]); ?>" size="12">
        <?php if ($i % 3 == 0) echo "<br>"; ?>
    <?php endfor; ?>
    <br><br>
    <input type="submit" value="保存修改">
    <a href="class_manage.php?action=list">返回列表</a>
    </form>
    </body></html>
    <?php
}
// ======================= 删除班级（同时删除该班级所有学生） =======================
elseif ($action == 'delete') {
    $className = $conn->real_escape_string($_GET['class']);
    // 删除学籍表中该班级的学生
    $conn->query("DELETE FROM 学籍表 WHERE 所在班级 = '$className'");
    // 删除班级
    $conn->query("DELETE FROM 班级表 WHERE 所在班级 = '$className'");
    show_msg("班级及所属学生已删除", "class_manage.php?action=list");
}
?>