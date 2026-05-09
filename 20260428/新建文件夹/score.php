<?php
// score.php - 成绩管理（录入、查询、统计）
require_once 'common.php';
check_login();
$conn = db_connect();

$action = isset($_GET['action']) ? $_GET['action'] : 'input';
$class = isset($_GET['class']) ? trim($_GET['class']) : '';
$exam = isset($_GET['exam']) ? $_GET['exam'] : '期中'; // 期中/期末
$sort = isset($_GET['sort']) ? $_GET['sort'] : '学号'; // 排序字段
$order = isset($_GET['order']) ? $_GET['order'] : 'ASC';

// 获取班级列表（用于下拉）
function getClassList($conn) {
    $res = $conn->query("SELECT 所在班级 FROM 班级表 ORDER BY 所在班级");
    $list = [];
    while ($row = $res->fetch_assoc()) $list[] = $row['所在班级'];
    return $list;
}

// 获取某班级的科目列表（科目1-科目10）
function getSubjects($conn, $class) {
    $res = $conn->query("SELECT 科目1,科目2,科目3,科目4,科目5,科目6,科目7,科目8,科目9,科目10 FROM 班级表 WHERE 所在班级='$class'");
    if ($res->num_rows == 0) return array_fill(1, 10, '');
    $row = $res->fetch_assoc();
    $subjects = [];
    for ($i=1; $i<=10; $i++) {
        $subjects[$i] = $row["科目$i"];
    }
    return $subjects;
}

// ======================= 成绩录入 =======================
if ($action == 'input') {
    // 处理保存
    if ($_POST && isset($_POST['save'])) {
        $class = $_POST['class'];
        $exam = $_POST['exam'];
        foreach ($_POST['score'] as $sid => $scores) {
            $sid = intval($sid);
            $updates = [];
            for ($i=1; $i<=10; $i++) {
                $val = isset($scores[$i]) ? intval($scores[$i]) : 0;
                $updates[] = "$exam$i = $val";
            }
            $sql = "UPDATE 学籍表 SET " . implode(',', $updates) . " WHERE 学号 = $sid";
            $conn->query($sql);
        }
        show_msg("成绩保存成功", "score.php?action=input&class=" . urlencode($class) . "&exam=$exam");
    }

    // 如果没有传入班级，取第一个班级
    $classList = getClassList($conn);
    if (empty($classList)) {
        die("请先在班级管理中添加班级。");
    }
    if ($class == '') $class = $classList[0];

    // 获取该班级学生列表
    $students = $conn->query("SELECT 学号,姓名 FROM 学籍表 WHERE 所在班级='$class' ORDER BY 学号");
    $subjects = getSubjects($conn, $class);
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>成绩录入</title></head>
    <body>
    <h2>成绩录入</h2>
    <form method="get" style="margin-bottom:10px;">
        <input type="hidden" name="action" value="input">
        班级: <select name="class" onchange="this.form.submit()">
            <?php foreach ($classList as $c): ?>
                <option value="<?php echo htmlspecialchars($c); ?>" <?php if($c==$class) echo 'selected'; ?>><?php echo htmlspecialchars($c); ?></option>
            <?php endforeach; ?>
        </select>
        考试: <select name="exam" onchange="this.form.submit()">
            <option value="期中" <?php if($exam=='期中') echo 'selected'; ?>>期中</option>
            <option value="期末" <?php if($exam=='期末') echo 'selected'; ?>>期末</option>
        </select>
    </form>

    <form method="post">
        <input type="hidden" name="class" value="<?php echo htmlspecialchars($class); ?>">
        <input type="hidden" name="exam" value="<?php echo $exam; ?>">
        <table border="1" cellpadding="5" cellspacing="0">
            <tr bgcolor="#ccc">
                <th>学号</th><th>姓名</th>
                <?php for ($i=1; $i<=10; $i++): ?>
                    <th><?php echo htmlspecialchars($subjects[$i] ?: "科目$i"); ?></th>
                <?php endfor; ?>
            </tr>
            <?php while ($stu = $students->fetch_assoc()):
                $sid = $stu['学号'];
                // 读取现有成绩
                $score_res = $conn->query("SELECT $exam" . implode(",$exam", range(1,10)) . " FROM 学籍表 WHERE 学号=$sid");
                $scores = $score_res->fetch_assoc();
            ?>
                <tr>
                    <td><?php echo $sid; ?></td>
                    <td><?php echo htmlspecialchars($stu['姓名']); ?></td>
                    <?php for ($i=1; $i<=10; $i++): ?>
                        <td><input type="text" name="score[<?php echo $sid; ?>][<?php echo $i; ?>]" value="<?php echo intval($scores["$exam$i"]); ?>" size="5"></td>
                    <?php endfor; ?>
                </tr>
            <?php endwhile; ?>
        </table>
        <br>
        <input type="submit" name="save" value="保存成绩">
        <a href="score.php?action=stats">成绩统计</a>
        <a href="score.php?action=list">成绩列表</a>
    </form>
    </body></html>
    <?php
}
// ======================= 成绩列表（可排序） =======================
elseif ($action == 'list') {
    $classList = getClassList($conn);
    if (empty($classList)) die("请先添加班级。");
    if ($class == '') $class = $classList[0];
    $subjects = getSubjects($conn, $class);
    // 排序字段安全处理
    $allowedSort = ['学号', '姓名'];
    for ($i=1;$i<=10;$i++) {
        $allowedSort[] = "$exam$i";
        $allowedSort[] = "$exam$i得分";
    }
    $sort = in_array($sort, $allowedSort) ? $sort : '学号';
    $order = strtoupper($order) == 'DESC' ? 'DESC' : 'ASC';
    // 构建查询
    $fields = "学号,姓名";
    for ($i=1;$i<=10;$i++) {
        $fields .= ", $exam$i";
    }
    $sql = "SELECT $fields FROM 学籍表 WHERE 所在班级='$class' ORDER BY $sort $order";
    $res = $conn->query($sql);
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>成绩列表</title></head>
    <body>
    <h2>成绩列表 - <?php echo htmlspecialchars($class); ?> (<?php echo $exam; ?>)</h2>
    <form method="get">
        <input type="hidden" name="action" value="list">
        班级: <select name="class" onchange="this.form.submit()">
            <?php foreach ($classList as $c): ?>
                <option value="<?php echo htmlspecialchars($c); ?>" <?php if($c==$class) echo 'selected'; ?>><?php echo htmlspecialchars($c); ?></option>
            <?php endforeach; ?>
        </select>
        考试: <select name="exam" onchange="this.form.submit()">
            <option value="期中" <?php if($exam=='期中') echo 'selected'; ?>>期中</option>
            <option value="期末" <?php if($exam=='期末') echo 'selected'; ?>>期末</option>
        </select>
    </form>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr bgcolor="#ccc">
            <th><a href="?action=list&class=<?php echo urlencode($class); ?>&exam=<?php echo $exam; ?>&sort=学号&order=<?php echo ($sort=='学号' && $order=='ASC')?'DESC':'ASC'; ?>">学号</a></th>
            <th><a href="?action=list&class=<?php echo urlencode($class); ?>&exam=<?php echo $exam; ?>&sort=姓名&order=<?php echo ($sort=='姓名' && $order=='ASC')?'DESC':'ASC'; ?>">姓名</a></th>
            <?php for ($i=1; $i<=10; $i++): ?>
                <th><?php echo htmlspecialchars($subjects[$i] ?: "科目$i"); ?>
                    <a href="?action=list&class=<?php echo urlencode($class); ?>&exam=<?php echo $exam; ?>&sort=<?php echo $exam.$i; ?>&order=<?php echo ($sort==$exam.$i && $order=='ASC')?'DESC':'ASC'; ?>">↑↓</a>
                </th>
            <?php endfor; ?>
        </tr>
        <?php while ($row = $res->fetch_assoc()): ?>
            <tr>
                <td><?php echo $row['学号']; ?></td>
                <td><?php echo htmlspecialchars($row['姓名']); ?></td>
                <?php for ($i=1; $i<=10; $i++): ?>
                    <td><?php echo intval($row["$exam$i"]); ?></td>
                <?php endfor; ?>
            </tr>
        <?php endwhile; ?>
    </table>
    <p><a href="score.php?action=input">返回成绩录入</a> | <a href="score.php?action=stats">成绩统计</a></p>
    </body></html>
    <?php
}
// ======================= 成绩统计 =======================
elseif ($action == 'stats') {
    $classList = getClassList($conn);
    if (empty($classList)) die("请先添加班级。");
    $exam = isset($_GET['exam']) ? $_GET['exam'] : '期中';
    // 统计所有班级各科平均分
    $stats = [];
    foreach ($classList as $c) {
        $subjects = getSubjects($conn, $c);
        $avg = [];
        $totalScore = 0;
        $studentCount = 0;
        // 获取该班级学生各科成绩
        $res = $conn->query("SELECT 学号 FROM 学籍表 WHERE 所在班级='$c'");
        $studentCount = $res->num_rows;
        for ($i=1; $i<=10; $i++) {
            $avgRes = $conn->query("SELECT AVG($exam$i) as avg_score FROM 学籍表 WHERE 所在班级='$c' AND $exam$i > 0");
            $row = $avgRes->fetch_assoc();
            $avg[$i] = round($row['avg_score'], 1);
            $totalScore += $avg[$i];
        }
        $stats[$c] = ['avg' => $avg, 'total' => $totalScore, 'count' => $studentCount];
    }
    ?>
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>成绩统计</title></head>
    <body>
    <h2>成绩统计（各班级平均分）</h2>
    <form method="get">
        <input type="hidden" name="action" value="stats">
        考试: <select name="exam" onchange="this.form.submit()">
            <option value="期中" <?php if($exam=='期中') echo 'selected'; ?>>期中</option>
            <option value="期末" <?php if($exam=='期末') echo 'selected'; ?>>期末</option>
        </select>
    </form>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr bgcolor="#ccc">
            <th>班级</th>
            <?php
            // 获取第一个班级的科目名称作为表头
            $firstClass = $classList[0];
            $subjects = getSubjects($conn, $firstClass);
            for ($i=1; $i<=10; $i++):
            ?>
                <th><?php echo htmlspecialchars($subjects[$i] ?: "科目$i"); ?></th>
            <?php endfor; ?>
            <th>总分</th>
        </tr>
        <?php foreach ($stats as $className => $data): ?>
            <tr>
                <td><?php echo htmlspecialchars($className); ?></td>
                <?php for ($i=1; $i<=10; $i++): ?>
                    <td><?php echo $data['avg'][$i]; ?></td>
                <?php endfor; ?>
                <td><?php echo round($data['total'], 1); ?></td>
            </tr>
        <?php endforeach; ?>
    </table>
    <p><a href="score.php?action=input">成绩录入</a> | <a href="score.php?action=list">成绩列表</a></p>
    </body></html>
    <?php
}
?>