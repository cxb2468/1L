<?php
// admin_user.php - 管理员管理（仅限超级管理员使用）
require_once 'common.php';
check_login();
// 只有拥有系统管理权限（第4位为1）的用户才能访问
if (!has_perm(3)) {
    show_msg("抱歉！您没有当前的操作权限！", "main.php");
}
$conn = db_connect();

$action = isset($_GET['action']) ? $_GET['action'] : 'list';

// 获取管理员列表
function getAdminList($conn) {
    $res = $conn->query("SELECT 用户名, 密码, 权限 FROM 管理员表 ORDER BY 用户名");
    $list = [];
    while ($row = $res->fetch_assoc()) {
        $list[] = $row;
    }
    return $list;
}

// ======================= 列表 =======================
if ($action == 'list') {
    $admins = getAdminList($conn);
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>管理员管理</title></head>
    <body>
    <h2>管理员管理</h2>
    <p><a href="?action=add">+ 添加管理员</a></p>
    <table border="1" cellpadding="5" cellspacing="0" width="100%">
        <tr bgcolor="#ccc">
            <th>用户名</th>
            <th>权限</th>
            <th>操作</th>
        </tr>
        <?php foreach ($admins as $admin): ?>
        <tr>
            <td><?php echo htmlspecialchars($admin['用户名']); ?></td>
            <td>
                <?php
                $perm = $admin['权限'];
                $permNames = [];
                if (substr($perm,0,1)=='1') $permNames[] = '学生管理';
                if (substr($perm,1,1)=='1') $permNames[] = '教员管理';
                if (substr($perm,2,1)=='1') $permNames[] = '工资管理';
                if (substr($perm,3,1)=='1') $permNames[] = '系统管理';
                echo implode(', ', $permNames) ?: '无权限';
                ?>
            </td>
            <td>
                <a href="?action=edit&user=<?php echo urlencode($admin['用户名']); ?>">编辑</a>
                <?php if ($admin['用户名'] != $_SESSION['username']): ?>
                    | <a href="?action=delete&user=<?php echo urlencode($admin['用户名']); ?>" onclick="return confirm('确定删除管理员 <?php echo htmlspecialchars($admin['用户名']); ?> 吗？')">删除</a>
                <?php endif; ?>
            </td>
        </tr>
        <?php endforeach; ?>
    </table>
    <p><a href="main.php">返回主界面</a></p>
    </body></html>
    <?php
}
// ======================= 添加管理员 =======================
elseif ($action == 'add') {
    if ($_POST) {
        $username = trim($_POST['username']);
        $password = trim($_POST['password']);
        $confirm = trim($_POST['confirm']);
        if ($username == '' || $password == '') {
            show_msg("用户名和密码不能为空", "?action=add");
        }
        if ($password != $confirm) {
            show_msg("两次输入的密码不一致", "?action=add");
        }
        // 权限组装
        $perm = '';
        $perm .= isset($_POST['perm_student']) ? '1' : '0';
        $perm .= isset($_POST['perm_teacher']) ? '1' : '0';
        $perm .= isset($_POST['perm_wage']) ? '1' : '0';
        $perm .= isset($_POST['perm_system']) ? '1' : '0';
        if ($perm == '0000') {
            show_msg("至少需要分配一项操作权限", "?action=add");
        }
        // 检查用户名是否已存在
        $check = $conn->query("SELECT 用户名 FROM 管理员表 WHERE 用户名='$username'");
        if ($check->num_rows > 0) {
            show_msg("用户名已存在", "?action=add");
        }
        $sql = "INSERT INTO 管理员表 (用户名, 密码, 权限) VALUES ('$username', '$password', '$perm')";
        if ($conn->query($sql)) {
            show_msg("添加成功", "?action=list");
        } else {
            show_msg("添加失败：" . $conn->error, "?action=add");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>添加管理员</title></head>
    <body>
    <h2>添加管理员</h2>
    <form method="post">
    <table border="0">
        <tr><td>用户名：</td><td><input type="text" name="username" required></td></tr>
        <tr><td>密码：</td><td><input type="password" name="password" required></td></tr>
        <tr><td>确认密码：</td><td><input type="password" name="confirm" required></td></tr>
        <tr><td>权限：</td><td>
            <input type="checkbox" name="perm_student" value="1"> 学生管理<br>
            <input type="checkbox" name="perm_teacher" value="1"> 教员管理<br>
            <input type="checkbox" name="perm_wage" value="1"> 工资管理<br>
            <input type="checkbox" name="perm_system" value="1"> 系统管理
        </td></tr>
        <tr><td colspan="2"><input type="submit" value="添加"> <a href="?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 编辑管理员 =======================
elseif ($action == 'edit') {
    $username = $_GET['user'];
    // 查询原信息
    $res = $conn->query("SELECT * FROM 管理员表 WHERE 用户名='$username'");
    if ($res->num_rows == 0) show_msg("管理员不存在", "?action=list");
    $admin = $res->fetch_assoc();
    if ($_POST) {
        $newUsername = trim($_POST['username']);
        $password = trim($_POST['password']);
        $confirm = trim($_POST['confirm']);
        if ($newUsername == '') {
            show_msg("用户名不能为空", "?action=edit&user=" . urlencode($username));
        }
        // 如果修改了用户名且新用户名已存在（且不是当前用户）
        if ($newUsername != $username) {
            $check = $conn->query("SELECT 用户名 FROM 管理员表 WHERE 用户名='$newUsername'");
            if ($check->num_rows > 0) {
                show_msg("新用户名已存在", "?action=edit&user=" . urlencode($username));
            }
        }
        // 权限组装
        $perm = '';
        $perm .= isset($_POST['perm_student']) ? '1' : '0';
        $perm .= isset($_POST['perm_teacher']) ? '1' : '0';
        $perm .= isset($_POST['perm_wage']) ? '1' : '0';
        $perm .= isset($_POST['perm_system']) ? '1' : '0';
        if ($perm == '0000') {
            show_msg("至少需要分配一项操作权限", "?action=edit&user=" . urlencode($username));
        }
        // 防止将唯一的超级管理员降权或改用户名导致权限丢失（简单检查：如果当前用户是唯一的超级管理员且修改后权限不再是1111或用户名改变）
        $superCount = $conn->query("SELECT COUNT(*) as cnt FROM 管理员表 WHERE 权限='1111'")->fetch_assoc()['cnt'];
        if ($superCount == 1 && $admin['权限'] == '1111') {
            if ($perm != '1111') {
                show_msg("当前是唯一的超级管理员，不能降低权限", "?action=edit&user=" . urlencode($username));
            }
            if ($newUsername != $username) {
                show_msg("当前是唯一的超级管理员，不能修改用户名", "?action=edit&user=" . urlencode($username));
            }
        }
        // 构建更新语句（密码可选修改）
        if ($password != '') {
            if ($password != $confirm) {
                show_msg("两次输入的密码不一致", "?action=edit&user=" . urlencode($username));
            }
            $sql = "UPDATE 管理员表 SET 用户名='$newUsername', 密码='$password', 权限='$perm' WHERE 用户名='$username'";
        } else {
            $sql = "UPDATE 管理员表 SET 用户名='$newUsername', 权限='$perm' WHERE 用户名='$username'";
        }
        if ($conn->query($sql)) {
            // 如果修改的是当前登录用户，更新会话中的用户名和权限
            if ($username == $_SESSION['username']) {
                $_SESSION['username'] = $newUsername;
                $_SESSION['perm'] = $perm;
            }
            show_msg("修改成功", "?action=list");
        } else {
            show_msg("修改失败：" . $conn->error, "?action=edit&user=" . urlencode($username));
        }
        exit;
    }
    // 显示编辑表单
    $permBits = str_split($admin['权限'] . '0000');
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>编辑管理员</title></head>
    <body>
    <h2>编辑管理员 - <?php echo htmlspecialchars($admin['用户名']); ?></h2>
    <form method="post">
    <table border="0">
        <tr><td>用户名：</td><td><input type="text" name="username" value="<?php echo htmlspecialchars($admin['用户名']); ?>" required></td></tr>
        <tr><td>密码：</td><td><input type="password" name="password">（留空则不修改）</td></tr>
        <tr><td>确认密码：</td><td><input type="password" name="confirm"></td></tr>
        <tr><td>权限：</td><td>
            <input type="checkbox" name="perm_student" <?php if($permBits[0]=='1') echo 'checked'; ?>> 学生管理<br>
            <input type="checkbox" name="perm_teacher" <?php if($permBits[1]=='1') echo 'checked'; ?>> 教员管理<br>
            <input type="checkbox" name="perm_wage" <?php if($permBits[2]=='1') echo 'checked'; ?>> 工资管理<br>
            <input type="checkbox" name="perm_system" <?php if($permBits[3]=='1') echo 'checked'; ?>> 系统管理
        </td></tr>
        <tr><td colspan="2"><input type="submit" value="保存修改"> <a href="?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 删除管理员 =======================
elseif ($action == 'delete') {
    $username = $_GET['user'];
    if ($username == $_SESSION['username']) {
        show_msg("不能删除自己", "?action=list");
    }
    // 检查是否为唯一的超级管理员
    $superCount = $conn->query("SELECT COUNT(*) as cnt FROM 管理员表 WHERE 权限='1111'")->fetch_assoc()['cnt'];
    if ($superCount == 1) {
        $res = $conn->query("SELECT 权限 FROM 管理员表 WHERE 用户名='$username'");
        if ($res->num_rows && $res->fetch_assoc()['权限'] == '1111') {
            show_msg("不能删除唯一的超级管理员", "?action=list");
        }
    }
    $conn->query("DELETE FROM 管理员表 WHERE 用户名='$username'");
    show_msg("已删除", "?action=list");
}
?>