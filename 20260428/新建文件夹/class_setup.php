<?php require_once 'common.php'; check_login(); if(!has_perm(3)) die("无权限");
$conn = db_connect();
if($_POST) {
    $class = $_POST['class'];
    $sql = "UPDATE 班级表 SET 科目1='{$_POST['sub1']}',科目2='{$_POST['sub2']}',...,班主任='{$_POST['teacher']}' WHERE 所在班级='$class'";
    $conn->query($sql);
    show_msg("保存成功");
}
$classes = get_class_list($conn);
$curr = $_GET['class']??$classes[0]??'';
$res = $conn->query("SELECT * FROM 班级表 WHERE 所在班级='$curr'");
$row = $res->fetch_assoc();
?>
<form method="post">
班级：<select name="class" onchange="this.form.submit()">
<?php foreach($classes as $c) echo "<option ".($curr==$c?"selected":"").">$c</option>"; ?>
</select><br>
班主任：<input name="teacher" value="<?=$row['班主任']?>"><br>
科目1-10：<br>
<?php for($i=1;$i<=10;$i++) echo "科目$i：<input name='sub$i' value='{$row["科目$i"]}'><br>"; ?>
<input type="submit" value="保存">
</form>