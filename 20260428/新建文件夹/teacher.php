<?php
// teacher.php - 教员管理（列表、添加、编辑、删除、退休/调离、查看、照片上传）
require_once 'common.php';
check_login();
$conn = db_connect();

// 自动检查并补充教员表缺失字段
function ensureTeacherTableColumns($conn) {
    $cols = [];
    $res = $conn->query("DESCRIBE 教员表");
    if ($res) {
        while ($row = $res->fetch_assoc()) $cols[] = $row['Field'];
    }
    $need = [
        '编号' => 'INT PRIMARY KEY', '姓名' => 'VARCHAR(50)', '性别' => 'VARCHAR(2)',
        '民族' => 'VARCHAR(20)', '出生日期' => 'DATE', '学历' => 'VARCHAR(20)',
        '政治面貌' => 'VARCHAR(20)', '参加工作时间' => 'DATE', '调入本校时间' => 'DATE',
        '职称' => 'VARCHAR(30)', '职务或岗位' => 'VARCHAR(50)', '身份证号' => 'VARCHAR(18)',
        '手机号码' => 'VARCHAR(20)', '家庭住址' => 'VARCHAR(200)', '住宅电话' => 'VARCHAR(20)',
        '籍贯' => 'VARCHAR(100)', '户籍所在地' => 'VARCHAR(100)', '照片' => 'LONGBLOB',
        '个人简历' => 'TEXT', '其他资料' => 'TEXT'
    ];
    foreach ($need as $field => $type) {
        if (!in_array($field, $cols)) {
            $conn->query("ALTER TABLE 教员表 ADD COLUMN $field $type");
        }
    }
}
ensureTeacherTableColumns($conn);

$action = isset($_GET['action']) ? $_GET['action'] : 'list';
$status = isset($_GET['status']) ? $_GET['status'] : 'active'; // active, retired, transferred

// 获取单个教员资料
function getTeacherById($conn, $id) {
    $id = intval($id);
    $res = $conn->query("SELECT * FROM 教员表 WHERE 编号 = $id");
    return $res->fetch_assoc();
}

// ======================= 列表 =======================
if ($action == 'list') {
    $keyword = isset($_GET['keyword']) ? trim($_GET['keyword']) : '';
    $where = "1=1";
    if ($keyword) $where .= " AND (姓名 LIKE '%$keyword%' OR 编号 LIKE '%$keyword%')";
    
    if ($status == 'active') {
        $table = '教员表';
        $title = '在职教员';
    } elseif ($status == 'retired') {
        $table = '离校教员表';
        $where .= " AND 离校原因 LIKE '%退休%'";
        $title = '退休教员';
    } elseif ($status == 'transferred') {
        $table = '离校教员表';
        $where .= " AND 离校原因 NOT LIKE '%退休%'";
        $title = '调离教员';
    } else {
        $table = '教员表';
        $title = '在职教员';
    }
    
    $sql = "SELECT 编号, 姓名, 性别, 职称, 手机号码 FROM $table WHERE $where ORDER BY 姓名";
    $res = $conn->query($sql);
    if (!$res) die("查询失败：" . $conn->error);
?>
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>教员管理</title></head>
<body>
<h2>教员管理 - <?php echo $title; ?></h2>
<p>
    <a href="?status=active" <?php if($status=='active') echo 'style="font-weight:bold;"'; ?>>在职教员</a> |
    <a href="?status=retired" <?php if($status=='retired') echo 'style="font-weight:bold;"'; ?>>退休教员</a> |
    <a href="?status=transferred" <?php if($status=='transferred') echo 'style="font-weight:bold;"'; ?>>调离教员</a>
</p>
<form method="get" style="margin-bottom:10px;">
    <input type="hidden" name="status" value="<?php echo $status; ?>">
    姓名/编号: <input type="text" name="keyword" value="<?php echo htmlspecialchars($keyword); ?>">
    <input type="submit" value="搜索">
    <?php if ($status == 'active'): ?>
        <a href="teacher.php?action=add" style="margin-left:20px;">+ 添加教员</a>
    <?php endif; ?>
</form>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
    <tr bgcolor="#ccc">
        <th>编号</th><th>姓名</th><th>性别</th><th>职称</th><th>手机</th><th>操作</th>
    </tr>
<?php while ($row = $res->fetch_assoc()): ?>
    <tr>
        <td><?php echo $row['编号']; ?></td>
        <td><?php echo htmlspecialchars($row['姓名']); ?></td>
        <td><?php echo $row['性别']; ?></td>
        <td><?php echo htmlspecialchars($row['职称']); ?></td>
        <td><?php echo htmlspecialchars($row['手机号码']); ?></td>
        <td>
            <a href="teacher.php?action=view&id=<?php echo $row['编号']; ?>&status=<?php echo $status; ?>">查看</a>
            <?php if ($status == 'active'): ?>
                | <a href="teacher.php?action=edit&id=<?php echo $row['编号']; ?>">编辑</a>
                | <a href="teacher.php?action=retire&id=<?php echo $row['编号']; ?>" onclick="return confirm('确认退休？')">退休</a>
                | <a href="teacher.php?action=transfer&id=<?php echo $row['编号']; ?>" onclick="return confirm('确认调离？')">调离</a>
                | <a href="teacher.php?action=delete&id=<?php echo $row['编号']; ?>" onclick="return confirm('永久删除，不可恢复！')">删除</a>
            <?php else: ?>
                | <a href="teacher.php?action=restore&id=<?php echo $row['编号']; ?>&status=<?php echo $status; ?>" onclick="return confirm('恢复该教员到在职状态？')">恢复</a>
                | <a href="teacher.php?action=delete_leave&id=<?php echo $row['编号']; ?>&status=<?php echo $status; ?>" onclick="return confirm('永久删除离校记录，不可恢复！')">删除</a>
            <?php endif; ?>
        </td>
    </tr>
<?php endwhile; ?>
</table>
<p><a href="student.php?action=list">返回学生管理</a></p>
</body></html>
<?php
}
// ======================= 添加教员 =======================
elseif ($action == 'add') {
    if ($_POST) {
        $bh = intval($_POST['编号']);
        $xm = $conn->real_escape_string($_POST['姓名']);
        $xb = $_POST['性别'];
        $mz = $conn->real_escape_string($_POST['民族']);
        $csrq = $_POST['出生日期'];
        $xl = $conn->real_escape_string($_POST['学历']);
        $zzmm = $conn->real_escape_string($_POST['政治面貌']);
        $cjsj = $_POST['参加工作时间'];
        $drxxsj = $_POST['调入本校时间'];
        $zc = $conn->real_escape_string($_POST['职称']);
        $zwgw = $conn->real_escape_string($_POST['职务或岗位']);
        $sfzh = $conn->real_escape_string($_POST['身份证号']);
        $sjhm = $conn->real_escape_string($_POST['手机号码']);
        $jtzz = $conn->real_escape_string($_POST['家庭住址']);
        $zzdh = $conn->real_escape_string($_POST['住宅电话']);
        $jg = $conn->real_escape_string($_POST['籍贯']);
        $hjszd = $conn->real_escape_string($_POST['户籍所在地']);
        $photo = null;
        if (isset($_FILES['photo']) && $_FILES['photo']['error'] == 0) {
            $photo = file_get_contents($_FILES['photo']['tmp_name']);
            $photo = $conn->real_escape_string($photo);
        }
        $jl = $conn->real_escape_string($_POST['个人简历']);
        $qt = $conn->real_escape_string($_POST['其他资料']);
        
        $sql = "INSERT INTO 教员表 (编号,姓名,性别,民族,出生日期,学历,政治面貌,参加工作时间,调入本校时间,
                职称,职务或岗位,身份证号,手机号码,家庭住址,住宅电话,籍贯,户籍所在地,照片,个人简历,其他资料)
                VALUES ($bh,'$xm','$xb','$mz','$csrq','$xl','$zzmm','$cjsj','$drxxsj','$zc','$zwgw','$sfzh','$sjhm',
                '$jtzz','$zzdh','$jg','$hjszd','$photo','$jl','$qt')";
        if ($conn->query($sql)) {
            show_msg("添加成功", "teacher.php?action=list");
        } else {
            show_msg("添加失败：" . $conn->error, "teacher.php?action=add");
        }
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>添加教员</title></head>
    <body>
    <h2>添加教员</h2>
    <form method="post" enctype="multipart/form-data">
    <table border="0" cellpadding="5">
        <tr><td>编号：</td><td><input type="text" name="编号" required></td></tr>
        <tr><td>姓名：</td><td><input type="text" name="姓名" required></td></tr>
        <tr><td>性别：</td><td><select name="性别"><option>男</option><option>女</option></select></td></tr>
        <tr><td>民族：</td><td><input type="text" name="民族" value="汉族"></td></tr>
        <tr><td>出生日期：</td><td><input type="date" name="出生日期"></td></tr>
        <tr><td>学历：</td><td><input type="text" name="学历"></td></tr>
        <tr><td>政治面貌：</td><td><input type="text" name="政治面貌"></td></tr>
        <tr><td>参加工作时间：</td><td><input type="date" name="参加工作时间"></td></tr>
        <tr><td>调入本校时间：</td><td><input type="date" name="调入本校时间"></td></tr>
        <tr><td>职称：</td><td><input type="text" name="职称"></td></tr>
        <tr><td>职务或岗位：</td><td><input type="text" name="职务或岗位"></td></tr>
        <tr><td>身份证号：</td><td><input type="text" name="身份证号"></td></tr>
        <tr><td>手机号码：</td><td><input type="text" name="手机号码"></td></tr>
        <tr><td>家庭住址：</td><td><input type="text" name="家庭住址" size="40"></td></tr>
        <tr><td>住宅电话：</td><td><input type="text" name="住宅电话"></td></tr>
        <tr><td>籍贯：</td><td><input type="text" name="籍贯"></td></tr>
        <tr><td>户籍所在地：</td><td><input type="text" name="户籍所在地"></td></tr>
        <tr><td>照片：</td><td><input type="file" name="photo"></td></tr>
        <tr><td>个人简历：</td><td><textarea name="个人简历" rows="4" cols="50"></textarea></td></tr>
        <tr><td>其他资料：</td><td><textarea name="其他资料" rows="4" cols="50"></textarea></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存"> <a href="teacher.php?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 编辑教员 =======================
elseif ($action == 'edit') {
    $id = intval($_GET['id']);
    if ($_POST) {
        $bh = intval($_POST['编号']);
        $xm = $conn->real_escape_string($_POST['姓名']);
        $xb = $_POST['性别'];
        $mz = $conn->real_escape_string($_POST['民族']);
        $csrq = $_POST['出生日期'];
        $xl = $conn->real_escape_string($_POST['学历']);
        $zzmm = $conn->real_escape_string($_POST['政治面貌']);
        $cjsj = $_POST['参加工作时间'];
        $drxxsj = $_POST['调入本校时间'];
        $zc = $conn->real_escape_string($_POST['职称']);
        $zwgw = $conn->real_escape_string($_POST['职务或岗位']);
        $sfzh = $conn->real_escape_string($_POST['身份证号']);
        $sjhm = $conn->real_escape_string($_POST['手机号码']);
        $jtzz = $conn->real_escape_string($_POST['家庭住址']);
        $zzdh = $conn->real_escape_string($_POST['住宅电话']);
        $jg = $conn->real_escape_string($_POST['籍贯']);
        $hjszd = $conn->real_escape_string($_POST['户籍所在地']);
        $photoPart = "";
        if (isset($_FILES['photo']) && $_FILES['photo']['error'] == 0) {
            $photo = file_get_contents($_FILES['photo']['tmp_name']);
            $photo = $conn->real_escape_string($photo);
            $photoPart = ",照片='$photo'";
        }
        $jl = $conn->real_escape_string($_POST['个人简历']);
        $qt = $conn->real_escape_string($_POST['其他资料']);
        
        $sql = "UPDATE 教员表 SET 编号=$bh,姓名='$xm',性别='$xb',民族='$mz',出生日期='$csrq',
                学历='$xl',政治面貌='$zzmm',参加工作时间='$cjsj',调入本校时间='$drxxsj',
                职称='$zc',职务或岗位='$zwgw',身份证号='$sfzh',手机号码='$sjhm',家庭住址='$jtzz',
                住宅电话='$zzdh',籍贯='$jg',户籍所在地='$hjszd',个人简历='$jl',其他资料='$qt'
                $photoPart WHERE 编号=$id";
        if ($conn->query($sql)) {
            show_msg("修改成功", "teacher.php?action=list");
        } else {
            show_msg("修改失败：" . $conn->error, "teacher.php?action=edit&id=$id");
        }
    }
    $row = getTeacherById($conn, $id);
    if (!$row) show_msg("教员不存在", "teacher.php?action=list");
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>编辑教员</title></head>
    <body>
    <h2>编辑教员 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post" enctype="multipart/form-data">
    <table border="0" cellpadding="5">
        <tr><td>编号：</td><td><input type="text" name="编号" value="<?php echo $row['编号']; ?>" required></td></tr>
        <tr><td>姓名：</td><td><input type="text" name="姓名" value="<?php echo htmlspecialchars($row['姓名']); ?>" required></td></tr>
        <tr><td>性别：</td><td><select name="性别"><option <?php echo $row['性别']=='男'?'selected':'';?>>男</option><option <?php echo $row['性别']=='女'?'selected':'';?>>女</option></select></td></tr>
        <tr><td>民族：</td><td><input type="text" name="民族" value="<?php echo htmlspecialchars($row['民族']); ?>"></td></tr>
        <tr><td>出生日期：</td><td><input type="date" name="出生日期" value="<?php echo $row['出生日期']; ?>"></td></tr>
        <tr><td>学历：</td><td><input type="text" name="学历" value="<?php echo htmlspecialchars($row['学历']); ?>"></td></tr>
        <tr><td>政治面貌：</td><td><input type="text" name="政治面貌" value="<?php echo htmlspecialchars($row['政治面貌']); ?>"></td></tr>
        <tr><td>参加工作时间：</td><td><input type="date" name="参加工作时间" value="<?php echo $row['参加工作时间']; ?>"></td></tr>
        <tr><td>调入本校时间：</td><td><input type="date" name="调入本校时间" value="<?php echo $row['调入本校时间']; ?>"></td></tr>
        <tr><td>职称：</td><td><input type="text" name="职称" value="<?php echo htmlspecialchars($row['职称']); ?>"></td></tr>
        <tr><td>职务或岗位：</td><td><input type="text" name="职务或岗位" value="<?php echo htmlspecialchars($row['职务或岗位']); ?>"></td></tr>
        <tr><td>身份证号：</td><td><input type="text" name="身份证号" value="<?php echo htmlspecialchars($row['身份证号']); ?>"></td></tr>
        <tr><td>手机号码：</td><td><input type="text" name="手机号码" value="<?php echo htmlspecialchars($row['手机号码']); ?>"></td></tr>
        <tr><td>家庭住址：</td><td><input type="text" name="家庭住址" size="40" value="<?php echo htmlspecialchars($row['家庭住址']); ?>"></td></tr>
        <tr><td>住宅电话：</td><td><input type="text" name="住宅电话" value="<?php echo htmlspecialchars($row['住宅电话']); ?>"></td></tr>
        <tr><td>籍贯：</td><td><input type="text" name="籍贯" value="<?php echo htmlspecialchars($row['籍贯']); ?>"></td></tr>
        <tr><td>户籍所在地：</td><td><input type="text" name="户籍所在地" value="<?php echo htmlspecialchars($row['户籍所在地']); ?>"></td></tr>
        <tr><td>照片：</td><td><input type="file" name="photo"> <?php if(!empty($row['照片'])) echo "当前已上传照片"; ?></td></tr>
        <tr><td>个人简历：</td><td><textarea name="个人简历" rows="4" cols="50"><?php echo htmlspecialchars($row['个人简历']); ?></textarea></td></tr>
        <tr><td>其他资料：</td><td><textarea name="其他资料" rows="4" cols="50"><?php echo htmlspecialchars($row['其他资料']); ?></textarea></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存修改"> <a href="teacher.php?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 查看详情 =======================
elseif ($action == 'view') {
    $id = intval($_GET['id']);
    $status = isset($_GET['status']) ? $_GET['status'] : 'active';
    if ($status == 'active') {
        $row = getTeacherById($conn, $id);
    } else {
        $table = '离校教员表';
        $res = $conn->query("SELECT * FROM $table WHERE 编号 = $id");
        $row = $res->fetch_assoc();
    }
    if (!$row) show_msg("教员不存在", "teacher.php?action=list");
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>教员详细信息</title>
    <style>
        body { font-family: 微软雅黑,宋体; margin:20px; }
        .main-table { width:100%; border-collapse:collapse; }
        .main-table td, .main-table th { border:1px solid #ccc; padding:8px; vertical-align:top; }
        .info-table { width:100%; border-collapse:collapse; }
        .info-table td, .info-table th { border:1px solid #ddd; padding:6px; }
        .info-table th { background:#f5f5f5; width:120px; text-align:right; }
        .section-title { background:#2c6e9e; color:white; padding:6px; margin:0 0 10px 0; font-weight:bold; }
        .photo-cell { vertical-align:middle; text-align:center; background:#fafafa; }
        .photo-img { max-width:180px; max-height:220px; border:1px solid #ccc; }
    </style>
    </head>
    <body>
    <h2>教员详细信息 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <table class="main-table" cellpadding="0" cellspacing="0">
        <tr>
            <td style="width:70%; padding:0;">
                <div class="section-title">基本信息</div>
                <table class="info-table">
                    <tr><th>编号</th><td><?php echo $row['编号']; ?></td><th>姓名</th><td><?php echo htmlspecialchars($row['姓名']); ?></td></tr>
                    <tr><th>性别</th><td><?php echo $row['性别']; ?></td><th>民族</th><td><?php echo htmlspecialchars($row['民族']); ?></td></tr>
                    <tr><th>出生日期</th><td><?php echo $row['出生日期']; ?></td><th>学历</th><td><?php echo htmlspecialchars($row['学历']); ?></td></tr>
                    <tr><th>政治面貌</th><td><?php echo htmlspecialchars($row['政治面貌']); ?></td><th>参加工作时间</th><td><?php echo $row['参加工作时间']; ?></td></tr>
                    <tr><th>调入本校时间</th><td><?php echo $row['调入本校时间']; ?></td><th>职称</th><td><?php echo htmlspecialchars($row['职称']); ?></td></tr>
                    <tr><th>职务或岗位</th><td><?php echo htmlspecialchars($row['职务或岗位']); ?></td><th>身份证号</th><td><?php echo htmlspecialchars($row['身份证号']); ?></td></tr>
                    <tr><th>手机号码</th><td><?php echo htmlspecialchars($row['手机号码']); ?></td><th>住宅电话</th><td><?php echo htmlspecialchars($row['住宅电话']); ?></td></tr>
                    <tr><th>家庭住址</th><td colspan="3"><?php echo htmlspecialchars($row['家庭住址']); ?></td></tr>
                    <tr><th>籍贯</th><td><?php echo htmlspecialchars($row['籍贯']); ?></td><th>户籍所在地</th><td><?php echo htmlspecialchars($row['户籍所在地']); ?></td></tr>
                </table>
                <div class="section-title">个人简历</div>
                <div style="border:1px solid #ddd; padding:8px;"><?php echo nl2br(htmlspecialchars($row['个人简历'])); ?></div>
                <div class="section-title">其他资料</div>
                <div style="border:1px solid #ddd; padding:8px;"><?php echo nl2br(htmlspecialchars($row['其他资料'])); ?></div>
            </td>
            <td class="photo-cell" style="width:30%;">
                <div class="section-title">照片</div>
                <div style="padding:15px;">
                <?php if(!empty($row['照片'])): ?>
                    <img src="data:image/jpeg;base64,<?php echo base64_encode($row['照片']); ?>" class="photo-img">
                <?php else: ?>
                    暂无照片
                <?php endif; ?>
                </div>
            </td>
        </tr>
    </table>
    <p><a href="teacher.php?action=list&status=<?php echo $status; ?>">返回列表</a></p>
    </body></html>
    <?php
}
// ======================= 退休（移至离校教员表） =======================
elseif ($action == 'retire') {
    $id = intval($_GET['id']);
    $row = getTeacherById($conn, $id);
    if (!$row) show_msg("教员不存在", "teacher.php?action=list");
    if ($_POST) {
        $date = $_POST['离校时间'];
        $reason = '退休';
        // 创建离校教员表（如果不存在）
        $conn->query("CREATE TABLE IF NOT EXISTS 离校教员表 LIKE 教员表");
        $conn->query("ALTER TABLE 离校教员表 ADD COLUMN 离校时间 DATE, ADD COLUMN 离校原因 VARCHAR(100)");
        // 插入到离校表
        $sql = "INSERT INTO 离校教员表 SELECT *, '$date','$reason' FROM 教员表 WHERE 编号 = $id";
        if ($conn->query($sql)) {
            $conn->query("DELETE FROM 教员表 WHERE 编号 = $id");
            show_msg("教员已退休", "teacher.php?action=list&status=retired");
        } else {
            show_msg("操作失败：" . $conn->error, "teacher.php?action=list");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>教员退休</title></head>
    <body>
    <h2>教员退休 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post">
    退休日期: <input type="date" name="离校时间" value="<?php echo date('Y-m-d'); ?>" required><br><br>
    <input type="submit" value="确认退休"> <a href="teacher.php?action=list">取消</a>
    </form>
    </body></html>
    <?php
}
// ======================= 调离 =======================
elseif ($action == 'transfer') {
    $id = intval($_GET['id']);
    $row = getTeacherById($conn, $id);
    if (!$row) show_msg("教员不存在", "teacher.php?action=list");
    if ($_POST) {
        $date = $_POST['离校时间'];
        $reason = $conn->real_escape_string($_POST['离校原因']);
        $conn->query("CREATE TABLE IF NOT EXISTS 离校教员表 LIKE 教员表");
        $conn->query("ALTER TABLE 离校教员表 ADD COLUMN 离校时间 DATE, ADD COLUMN 离校原因 VARCHAR(100)");
        $sql = "INSERT INTO 离校教员表 SELECT *, '$date','$reason' FROM 教员表 WHERE 编号 = $id";
        if ($conn->query($sql)) {
            $conn->query("DELETE FROM 教员表 WHERE 编号 = $id");
            show_msg("教员已调离", "teacher.php?action=list&status=transferred");
        } else {
            show_msg("操作失败：" . $conn->error, "teacher.php?action=list");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>教员调离</title></head>
    <body>
    <h2>教员调离 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post">
    调离日期: <input type="date" name="离校时间" value="<?php echo date('Y-m-d'); ?>" required><br><br>
    调离原因: <input type="text" name="离校原因" list="reason_list" style="width:200px;">
        <datalist id="reason_list"><option>正常调动</option><option>辞职</option><option>其他</option></datalist>
    <br><br>
    <input type="submit" value="确认调离"> <a href="teacher.php?action=list">取消</a>
    </form>
    </body></html>
    <?php
}
// ======================= 恢复（从离校表恢复到教员表） =======================
elseif ($action == 'restore') {
    $id = intval($_GET['id']);
    $status = $_GET['status'];
    $table = ($status == 'retired') ? '离校教员表' : '离校教员表';
    // 从离校表复制回教员表（排除离校字段）
    $conn->query("INSERT INTO 教员表 SELECT 编号,姓名,性别,民族,出生日期,学历,政治面貌,参加工作时间,调入本校时间,
                  职称,职务或岗位,身份证号,手机号码,家庭住址,住宅电话,籍贯,户籍所在地,照片,个人简历,其他资料
                  FROM $table WHERE 编号 = $id");
    $conn->query("DELETE FROM $table WHERE 编号 = $id");
    show_msg("恢复成功", "teacher.php?action=list&status=active");
}
// ======================= 删除在职教员 =======================
elseif ($action == 'delete') {
    $id = intval($_GET['id']);
    $conn->query("DELETE FROM 教员表 WHERE 编号 = $id");
    show_msg("已删除", "teacher.php?action=list");
}
// ======================= 删除离校教员记录 =======================
elseif ($action == 'delete_leave') {
    $id = intval($_GET['id']);
    $status = $_GET['status'];
    $table = ($status == 'retired') ? '离校教员表' : '离校教员表';
    $conn->query("DELETE FROM $table WHERE 编号 = $id");
    show_msg("已删除", "teacher.php?action=list&status=$status");
}
?>