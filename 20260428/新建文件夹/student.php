<?php
// student.php - 学生管理（列表、添加、编辑、删除、转学、毕业、查看、照片上传）
require_once 'common.php';
check_login();
$conn = db_connect();

// 自动检查并补充学籍表缺失字段（无 IF NOT EXISTS）
function ensureStudentTableColumns($conn) {
    $cols = [];
    $res = $conn->query("DESCRIBE 学籍表");
    if ($res) {
        while ($row = $res->fetch_assoc()) $cols[] = $row['Field'];
    }
    $need = [
        '民族' => 'VARCHAR(20)', '出生日期' => 'DATE', '入学日期' => 'DATE',
        '联系电话' => 'VARCHAR(20)', '家庭住址' => 'VARCHAR(200)', '户籍' => 'VARCHAR(100)', '籍贯' => 'VARCHAR(100)',
        '家长A' => 'VARCHAR(20)', '家长A姓名' => 'VARCHAR(50)', '家长A单位' => 'VARCHAR(100)', '家长A电话' => 'VARCHAR(20)',
        '家长B' => 'VARCHAR(20)', '家长B姓名' => 'VARCHAR(50)', '家长B单位' => 'VARCHAR(100)', '家长B电话' => 'VARCHAR(20)',
        '班内职务' => 'VARCHAR(50)', '照片' => 'LONGBLOB', '本学期评语' => 'TEXT', '综合评语' => 'TEXT',
        '身份证号' => 'VARCHAR(18)',
        '期中1' => 'INT', '期中2' => 'INT', '期中3' => 'INT', '期中4' => 'INT', '期中5' => 'INT',
        '期中6' => 'INT', '期中7' => 'INT', '期中8' => 'INT', '期中9' => 'INT', '期中10' => 'INT',
        '期末1' => 'INT', '期末2' => 'INT', '期末3' => 'INT', '期末4' => 'INT', '期末5' => 'INT',
        '期末6' => 'INT', '期末7' => 'INT', '期末8' => 'INT', '期末9' => 'INT', '期末10' => 'INT'
    ];
    foreach ($need as $field => $type) {
        if (!in_array($field, $cols)) {
            $conn->query("ALTER TABLE 学籍表 ADD COLUMN $field $type");
        }
    }
}
ensureStudentTableColumns($conn);

$action = isset($_GET['action']) ? $_GET['action'] : 'list';

function getClassOptions($conn, $selected = '') {
    $res = $conn->query("SELECT 所在班级 FROM 班级表 ORDER BY 所在班级");
    $html = '';
    while ($row = $res->fetch_assoc()) {
        $sel = ($selected == $row['所在班级']) ? 'selected' : '';
        $html .= "<option value=\"" . htmlspecialchars($row['所在班级']) . "\" $sel>" . htmlspecialchars($row['所在班级']) . "</option>";
    }
    return $html;
}

function getStudentById($conn, $id) {
    $id = intval($id);
    $res = $conn->query("SELECT * FROM 学籍表 WHERE 学号 = $id");
    return $res->fetch_assoc();
}

// ======================= 列表 =======================
if ($action == 'list') {
    $class = isset($_GET['class']) ? trim($_GET['class']) : '';
    $keyword = isset($_GET['keyword']) ? trim($_GET['keyword']) : '';
    $where = "1=1";
    if ($class) $where .= " AND 所在班级 = '$class'";
    if ($keyword) $where .= " AND (姓名 LIKE '%$keyword%' OR 学号 LIKE '%$keyword%')";
    $sql = "SELECT 学号, 姓名, 性别, 所在班级, 联系电话 FROM 学籍表 WHERE $where ORDER BY 所在班级, 姓名";
    $res = $conn->query($sql);
    if (!$res) die("查询失败：" . $conn->error);
?>
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>学生列表</title></head>
<body>
<h2>学生管理 - 列表</h2>
<form method="get" style="margin-bottom:10px;">
    <input type="hidden" name="action" value="list">
    班级: <select name="class"><option value="">全部</option><?php echo getClassOptions($conn, $class); ?></select>
    姓名/学号: <input type="text" name="keyword" value="<?php echo htmlspecialchars($keyword); ?>">
    <input type="submit" value="筛选">
    <a href="student.php?action=add" style="margin-left:20px;">+ 添加学生</a>
</form>
<table border="1" cellpadding="5" cellspacing="0" width="100%">
    <tr bgcolor="#ccc"><th>学号</th><th>姓名</th><th>性别</th><th>班级</th><th>电话</th><th>操作</th> </tr>
<?php while ($row = $res->fetch_assoc()): ?>
    <tr>
        <td><?php echo $row['学号']; ?></td>
        <td><?php echo htmlspecialchars($row['姓名']); ?></td>
        <td><?php echo $row['性别']; ?></td>
        <td><?php echo htmlspecialchars($row['所在班级']); ?></td>
        <td><?php echo htmlspecialchars($row['联系电话']); ?></td>
        <td>
            <a href="student.php?action=view&id=<?php echo $row['学号']; ?>">查看</a>
            <a href="student.php?action=edit&id=<?php echo $row['学号']; ?>">编辑</a>
            <a href="student.php?action=transfer&id=<?php echo $row['学号']; ?>" onclick="return confirm('确认转学/退学？')">转学/退学</a>
            <a href="student.php?action=delete&id=<?php echo $row['学号']; ?>" onclick="return confirm('永久删除，不可恢复！')">删除</a>
        </td>
    </tr>
<?php endwhile; ?>
</table>
</body></html>
<?php
}
// ======================= 添加学生 =======================
elseif ($action == 'add') {
    if ($_POST) {
        $xh = intval($_POST['学号']);
        $xm = $conn->real_escape_string($_POST['姓名']);
        $xb = $_POST['性别'];
        $mz = $conn->real_escape_string($_POST['民族']);
        $csrq = $_POST['出生日期'];
        $rxrq = $_POST['入学日期'];
        $bj = $conn->real_escape_string($_POST['所在班级']);
        $zw = $conn->real_escape_string($_POST['班内职务']);
        $address = $conn->real_escape_string($_POST['家庭住址']);
        $phone = $conn->real_escape_string($_POST['联系电话']);
        $hukou = $conn->real_escape_string($_POST['户籍']);
        $jiguan = $conn->real_escape_string($_POST['籍贯']);
        $sfzh = $conn->real_escape_string($_POST['身份证号']);
        $jza = $conn->real_escape_string($_POST['家长A']);
        $jzaxm = $conn->real_escape_string($_POST['家长A姓名']);
        $jzadw = $conn->real_escape_string($_POST['家长A单位']);
        $jzatel = $conn->real_escape_string($_POST['家长A电话']);
        $jzb = $conn->real_escape_string($_POST['家长B']);
        $jzbxm = $conn->real_escape_string($_POST['家长B姓名']);
        $jzbdw = $conn->real_escape_string($_POST['家长B单位']);
        $jzbtel = $conn->real_escape_string($_POST['家长B电话']);
        
        // 照片处理
        $photo = null;
        if (isset($_FILES['photo']) && $_FILES['photo']['error'] == 0) {
            $photo = file_get_contents($_FILES['photo']['tmp_name']);
            $photo = $conn->real_escape_string($photo);
        }
        
        $sql = "INSERT INTO 学籍表 (学号,姓名,性别,民族,出生日期,入学日期,所在班级,班内职务,家庭住址,联系电话,户籍,籍贯,身份证号,
                家长A,家长A姓名,家长A单位,家长A电话,家长B,家长B姓名,家长B单位,家长B电话,照片)
                VALUES ($xh,'$xm','$xb','$mz','$csrq','$rxrq','$bj','$zw','$address','$phone','$hukou','$jiguan','$sfzh',
                '$jza','$jzaxm','$jzadw','$jzatel','$jzb','$jzbxm','$jzbdw','$jzbtel','$photo')";
        if ($conn->query($sql)) {
            show_msg("添加成功", "student.php?action=list");
        } else {
            show_msg("添加失败：" . $conn->error, "student.php?action=add");
        }
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>添加学生</title></head>
    <body>
    <h2>添加学生</h2>
    <form method="post" enctype="multipart/form-data">
    <table border="0" cellpadding="5">
        <tr><td>学号：</td><td><input type="text" name="学号" required></td></tr>
        <tr><td>姓名：</td><td><input type="text" name="姓名" required></td></tr>
        <tr><td>性别：</td><td><select name="性别"><option>男</option><option>女</option></select></td></tr>
        <tr><td>民族：</td><td><input type="text" name="民族" value="汉族"></td></tr>
        <tr><td>出生日期：</td><td><input type="date" name="出生日期"></td></tr>
        <tr><td>入学日期：</td><td><input type="date" name="入学日期"></td></tr>
        <tr><td>所在班级：</td><td><select name="所在班级"><?php echo getClassOptions($conn); ?></select></td></tr>
        <tr><td>班内职务：</td><td><input type="text" name="班内职务"></td></tr>
        <tr><td>家庭住址：</td><td><input type="text" name="家庭住址" size="40"></td></tr>
        <tr><td>联系电话：</td><td><input type="text" name="联系电话"></td></tr>
        <tr><td>户籍：</td><td><input type="text" name="户籍"></td></tr>
        <tr><td>籍贯：</td><td><input type="text" name="籍贯"></td></tr>
        <tr><td>身份证号：</td><td><input type="text" name="身份证号" size="20"></td></tr>
        <tr><td colspan="2"><strong>家长信息</strong></td></tr>
        <tr><td>家长A称谓：</td><td><input type="text" name="家长A" value="父亲"></td></tr>
        <tr><td>家长A姓名：</td><td><input type="text" name="家长A姓名"></td></tr>
        <tr><td>家长A单位：</td><td><input type="text" name="家长A单位"></td></tr>
        <tr><td>家长A电话：</td><td><input type="text" name="家长A电话"></td></tr>
        <tr><td>家长B称谓：</td><td><input type="text" name="家长B" value="母亲"></td></tr>
        <tr><td>家长B姓名：</td><td><input type="text" name="家长B姓名"></td></tr>
        <tr><td>家长B单位：</td><td><input type="text" name="家长B单位"></td></tr>
        <tr><td>家长B电话：</td><td><input type="text" name="家长B电话"></td></tr>
        <tr><td>照片：</td><td><input type="file" name="photo"></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存"> <a href="student.php?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 编辑学生 =======================
elseif ($action == 'edit') {
    $id = intval($_GET['id']);
    if ($_POST) {
        $xh = intval($_POST['学号']);
        $xm = $conn->real_escape_string($_POST['姓名']);
        $xb = $_POST['性别'];
        $mz = $conn->real_escape_string($_POST['民族']);
        $csrq = $_POST['出生日期'];
        $rxrq = $_POST['入学日期'];
        $bj = $conn->real_escape_string($_POST['所在班级']);
        $zw = $conn->real_escape_string($_POST['班内职务']);
        $address = $conn->real_escape_string($_POST['家庭住址']);
        $phone = $conn->real_escape_string($_POST['联系电话']);
        $hukou = $conn->real_escape_string($_POST['户籍']);
        $jiguan = $conn->real_escape_string($_POST['籍贯']);
        $sfzh = $conn->real_escape_string($_POST['身份证号']);
        $jza = $conn->real_escape_string($_POST['家长A']);
        $jzaxm = $conn->real_escape_string($_POST['家长A姓名']);
        $jzadw = $conn->real_escape_string($_POST['家长A单位']);
        $jzatel = $conn->real_escape_string($_POST['家长A电话']);
        $jzb = $conn->real_escape_string($_POST['家长B']);
        $jzbxm = $conn->real_escape_string($_POST['家长B姓名']);
        $jzbdw = $conn->real_escape_string($_POST['家长B单位']);
        $jzbtel = $conn->real_escape_string($_POST['家长B电话']);
        
        $photoPart = "";
        if (isset($_FILES['photo']) && $_FILES['photo']['error'] == 0) {
            $photo = file_get_contents($_FILES['photo']['tmp_name']);
            $photo = $conn->real_escape_string($photo);
            $photoPart = ",照片='$photo'";
        }
        
        $sql = "UPDATE 学籍表 SET 学号=$xh,姓名='$xm',性别='$xb',民族='$mz',出生日期='$csrq',入学日期='$rxrq',
                所在班级='$bj',班内职务='$zw',家庭住址='$address',联系电话='$phone',户籍='$hukou',籍贯='$jiguan',
                身份证号='$sfzh',
                家长A='$jza',家长A姓名='$jzaxm',家长A单位='$jzadw',家长A电话='$jzatel',
                家长B='$jzb',家长B姓名='$jzbxm',家长B单位='$jzbdw',家长B电话='$jzbtel'
                $photoPart WHERE 学号=$id";
        if ($conn->query($sql)) {
            show_msg("修改成功", "student.php?action=list");
        } else {
            show_msg("修改失败：" . $conn->error, "student.php?action=edit&id=$id");
        }
    }
    $row = getStudentById($conn, $id);
    if (!$row) show_msg("学生不存在", "student.php?action=list");
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>编辑学生</title></head>
    <body>
    <h2>编辑学生 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post" enctype="multipart/form-data">
    <table border="0" cellpadding="5">
        <tr><td>学号：</td><td><input type="text" name="学号" value="<?php echo $row['学号']; ?>" required></td></tr>
        <tr><td>姓名：</td><td><input type="text" name="姓名" value="<?php echo htmlspecialchars($row['姓名']); ?>" required></td></tr>
        <tr><td>性别：</td><td><select name="性别"><option <?php echo $row['性别']=='男'?'selected':'';?>>男</option><option <?php echo $row['性别']=='女'?'selected':'';?>>女</option></select></td></tr>
        <tr><td>民族：</td><td><input type="text" name="民族" value="<?php echo htmlspecialchars($row['民族']); ?>"></td></tr>
        <tr><td>出生日期：</td><td><input type="date" name="出生日期" value="<?php echo $row['出生日期']; ?>"></td></tr>
        <tr><td>入学日期：</td><td><input type="date" name="入学日期" value="<?php echo $row['入学日期']; ?>"></td></tr>
        <tr><td>所在班级：</td><td><select name="所在班级"><?php echo getClassOptions($conn, $row['所在班级']); ?></select></td></tr>
        <tr><td>班内职务：</td><td><input type="text" name="班内职务" value="<?php echo htmlspecialchars($row['班内职务']); ?>"></td></tr>
        <tr><td>家庭住址：</td><td><input type="text" name="家庭住址" size="40" value="<?php echo htmlspecialchars($row['家庭住址']); ?>"></td></tr>
        <tr><td>联系电话：</td><td><input type="text" name="联系电话" value="<?php echo htmlspecialchars($row['联系电话']); ?>"></td></tr>
        <tr><td>户籍：</td><td><input type="text" name="户籍" value="<?php echo htmlspecialchars($row['户籍']); ?>"></td></tr>
        <tr><td>籍贯：</td><td><input type="text" name="籍贯" value="<?php echo htmlspecialchars($row['籍贯']); ?>"></td></tr>
        <tr><td>身份证号：</td><td><input type="text" name="身份证号" size="20" value="<?php echo htmlspecialchars($row['身份证号']); ?>"></td></tr>
        <tr><td colspan="2"><strong>家长信息</strong></td></tr>
        <tr><td>家长A称谓：</td><td><input type="text" name="家长A" value="<?php echo htmlspecialchars($row['家长A']); ?>"></td></tr>
        <tr><td>家长A姓名：</td><td><input type="text" name="家长A姓名" value="<?php echo htmlspecialchars($row['家长A姓名']); ?>"></td></tr>
        <tr><td>家长A单位：</td><td><input type="text" name="家长A单位" value="<?php echo htmlspecialchars($row['家长A单位']); ?>"></td></tr>
        <tr><td>家长A电话：</td><td><input type="text" name="家长A电话" value="<?php echo htmlspecialchars($row['家长A电话']); ?>"></td></tr>
        <tr><td>家长B称谓：</td><td><input type="text" name="家长B" value="<?php echo htmlspecialchars($row['家长B']); ?>"></td></tr>
        <tr><td>家长B姓名：</td><td><input type="text" name="家长B姓名" value="<?php echo htmlspecialchars($row['家长B姓名']); ?>"></td></tr>
        <tr><td>家长B单位：</td><td><input type="text" name="家长B单位" value="<?php echo htmlspecialchars($row['家长B单位']); ?>"></td></tr>
        <tr><td>家长B电话：</td><td><input type="text" name="家长B电话" value="<?php echo htmlspecialchars($row['家长B电话']); ?>"></td></tr>
        <tr><td>照片：</td><td><input type="file" name="photo"> <?php if(!empty($row['照片'])) echo "当前已上传照片"; ?></td></tr>
        <tr><td colspan="2"><input type="submit" value="保存修改"> <a href="student.php?action=list">返回列表</a></td></tr>
    </table>
    </form>
    </body></html>
    <?php
}
// ======================= 查看详情（基础信息 | 照片，下方评语+成绩单） =======================
elseif ($action == 'view') {
    $id = intval($_GET['id']);
    $row = getStudentById($conn, $id);
    if (!$row) show_msg("学生不存在", "student.php?action=list");
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>学生详细信息</title>
    <style>
        body { font-family: 微软雅黑,宋体; margin:20px; }
        .main-table { width:100%; border-collapse:collapse; }
        .main-table td, .main-table th { border:1px solid #ccc; padding:8px; vertical-align:top; }
        .info-table { width:100%; border-collapse:collapse; }
        .info-table td, .info-table th { border:1px solid #ddd; padding:6px; }
        .info-table th { background:#f5f5f5; width:100px; text-align:right; }
        .section-title { background:#2c6e9e; color:white; padding:6px; margin:0 0 10px 0; font-weight:bold; }
        .photo-cell { vertical-align:middle; text-align:center; background:#fafafa; }
        .photo-img { max-width:180px; max-height:220px; border:1px solid #ccc; }
        .no-photo { color:#999; }
    </style>
    </head>
    <body>
    <h2>学生详细信息 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <table class="main-table" cellpadding="0" cellspacing="0">
        <tr>
            <td style="width:70%; padding:0;">
                <div class="section-title" style="margin:0;">基础信息</div>
                <table class="info-table" style="border-top:0;">
                    <tr><th>学号</th><td><?php echo $row['学号']; ?></td><th>姓名</th><td><?php echo htmlspecialchars($row['姓名']); ?></td></tr>
                    <tr><th>性别</th><td><?php echo $row['性别']; ?></td><th>民族</th><td><?php echo htmlspecialchars($row['民族']); ?></td></tr>
                    <tr><th>出生日期</th><td><?php echo $row['出生日期']; ?></td><th>入学日期</th><td><?php echo $row['入学日期']; ?></td></tr>
                    <tr><th>所在班级</th><td><?php echo htmlspecialchars($row['所在班级']); ?></td><th>班内职务</th><td><?php echo htmlspecialchars($row['班内职务']); ?></td></tr>
                    <tr><th>户籍</th><td><?php echo htmlspecialchars($row['户籍']); ?></td><th>籍贯</th><td><?php echo htmlspecialchars($row['籍贯']); ?></td></tr>
                    <tr><th>联系电话</th><td><?php echo htmlspecialchars($row['联系电话']); ?></td><th>家庭住址</th><td><?php echo htmlspecialchars($row['家庭住址']); ?></td></tr>
                    <tr><th>身份证号</th><td colspan="3"><?php echo htmlspecialchars($row['身份证号']); ?></td></tr>
                    <tr><th>家长A</th><td colspan="3"><?php echo htmlspecialchars($row['家长A']); ?>：<?php echo htmlspecialchars($row['家长A姓名']); ?> （<?php echo htmlspecialchars($row['家长A单位']); ?> / <?php echo htmlspecialchars($row['家长A电话']); ?>）</td></tr>
                    <tr><th>家长B</th><td colspan="3"><?php echo htmlspecialchars($row['家长B']); ?>：<?php echo htmlspecialchars($row['家长B姓名']); ?> （<?php echo htmlspecialchars($row['家长B单位']); ?> / <?php echo htmlspecialchars($row['家长B电话']); ?>）</td></tr>
                </table>
            </td>
            <td class="photo-cell" style="width:30%;">
                <div class="section-title" style="margin:0;">照片</div>
                <div style="padding:15px;">
                <?php if(!empty($row['照片'])): ?>
                    <img src="data:image/jpeg;base64,<?php echo base64_encode($row['照片']); ?>" class="photo-img" alt="学生照片">
                <?php else: ?>
                    <span class="no-photo">暂无照片</span>
                <?php endif; ?>
                </div>
            </td>
        </tr>
        <tr><td colspan="2">
            <div class="section-title">评语</div>
            <table class="info-table">
                <tr><th>本学期评语</th><td><?php echo nl2br(htmlspecialchars($row['本学期评语'])); ?></td></tr>
                <tr><th>综合评语</th><td><?php echo nl2br(htmlspecialchars($row['综合评语'])); ?></td></tr>
            </table>
        </td></tr>
        <tr><td colspan="2">
            <div class="section-title">成绩单</div>
            <table class="info-table">
                <tr><th>科目</th><?php for($i=1;$i<=10;$i++) echo "<th>科目$i</th>"; ?></tr>
                <tr><th>期中</th><?php for($i=1;$i<=10;$i++) echo "<td>".intval($row["期中$i"])."</td>"; ?></tr>
                <tr><th>期末</th><?php for($i=1;$i<=10;$i++) echo "<td>".intval($row["期末$i"])."</td>"; ?></tr>
            </table>
        </td></tr>
    </table>
    <p><a href="student.php?action=list">返回列表</a> | <a href="student.php?action=edit&id=<?php echo $id; ?>">编辑</a></p>
    </body></html>
    <?php
}
// ======================= 删除 =======================
elseif ($action == 'delete') {
    $id = intval($_GET['id']);
    $conn->query("DELETE FROM 学籍表 WHERE 学号 = $id");
    show_msg("已删除", "student.php?action=list");
}
// ======================= 转学/退学 =======================
elseif ($action == 'transfer') {
    $id = intval($_GET['id']);
    $row = getStudentById($conn, $id);
    if (!$row) show_msg("学生不存在", "student.php?action=list");
    if ($_POST) {
        $reason = $conn->real_escape_string($_POST['离校原因']);
        $date = $_POST['离校日期'];
        $conn->query("CREATE TABLE IF NOT EXISTS 离校人员名单 LIKE 学籍表");
        $conn->query("ALTER TABLE 离校人员名单 ADD COLUMN 离校时间 DATE, ADD COLUMN 离校原因 VARCHAR(100)");
        $sql = "INSERT INTO 离校人员名单 (学号,姓名,性别,民族,出生日期,入学日期,所在班级,班内职务,家庭住址,联系电话,户籍,籍贯,身份证号,
                家长A,家长A姓名,家长A单位,家长A电话,家长B,家长B姓名,家长B单位,家长B电话,照片,本学期评语,综合评语,
                期中1,期中2,期中3,期中4,期中5,期中6,期中7,期中8,期中9,期中10,
                期末1,期末2,期末3,期末4,期末5,期末6,期末7,期末8,期末9,期末10,
                离校时间,离校原因)
                SELECT 学号,姓名,性别,民族,出生日期,入学日期,所在班级,班内职务,家庭住址,联系电话,户籍,籍贯,身份证号,
                家长A,家长A姓名,家长A单位,家长A电话,家长B,家长B姓名,家长B单位,家长B电话,照片,本学期评语,综合评语,
                期中1,期中2,期中3,期中4,期中5,期中6,期中7,期中8,期中9,期中10,
                期末1,期末2,期末3,期末4,期末5,期末6,期末7,期末8,期末9,期末10,
                '$date','$reason' FROM 学籍表 WHERE 学号 = $id";
        if ($conn->query($sql)) {
            $conn->query("DELETE FROM 学籍表 WHERE 学号 = $id");
            show_msg("该生已转学/退学", "student.php?action=list");
        } else {
            show_msg("转学/退学操作失败：" . $conn->error, "student.php?action=transfer&id=$id");
        }
        exit;
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>学生转学/退学</title></head>
    <body>
    <h2>学生转学/退学 - <?php echo htmlspecialchars($row['姓名']); ?></h2>
    <form method="post">
    离校日期: <input type="date" name="离校日期" value="<?php echo date('Y-m-d'); ?>" required><br><br>
    离校原因: 
        <input list="reasons" name="离校原因" style="width:200px;" placeholder="可选择或手动输入">
        <datalist id="reasons">
            <option>转学</option><option>退学</option><option>休学</option><option>其他</option>
        </datalist>
    <br><br>
    <input type="submit" value="确认离校"> <a href="student.php?action=list">取消</a>
    </form>
    </body></html>
    <?php
}
// ======================= 毕业升级 =======================
elseif ($action == 'graduate') {
    if ($_POST) {
        $graduateDate = $_POST['毕业日期'];
        $classes = $conn->query("SELECT 所在班级 FROM 班级表 WHERE 所在班级 LIKE '%6年级%' OR 所在班级 LIKE '%初中3年级%' OR 所在班级 LIKE '%高中3年级%'");
        while ($c = $classes->fetch_assoc()) {
            $className = $c['所在班级'];
            $conn->query("INSERT INTO 离校人员名单 SELECT *, '$graduateDate','毕业' FROM 学籍表 WHERE 所在班级 = '$className'");
            $conn->query("DELETE FROM 学籍表 WHERE 所在班级 = '$className'");
            $conn->query("DELETE FROM 班级表 WHERE 所在班级 = '$className'");
        }
        show_msg("毕业升级操作完成", "student.php?action=list");
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>毕业升级</title></head>
    <body>
    <h2>批量毕业升级</h2>
    <p>将自动识别六年级、初三、高三班级，执行毕业操作。</p>
    <form method="post">
    毕业日期: <input type="date" name="毕业日期" value="<?php echo date('Y-m-d'); ?>" required><br><br>
    <input type="submit" value="执行毕业升级" onclick="return confirm('毕业操作不可逆，确认执行？')">
    <a href="student.php?action=list">返回列表</a>
    </form>
    </body></html>
    <?php
}
?>