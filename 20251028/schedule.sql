DROP TABLE IF EXISTS class;
CREATE TABLE class(
    `id` INT AUTO_INCREMENT COMMENT '' ,
    `classname` VARCHAR(255)   COMMENT '' ,
    `number` INT   COMMENT '' ,
    PRIMARY KEY (id)
)  COMMENT = 'class';

DROP TABLE IF EXISTS course;
CREATE TABLE course(
    `id` INT AUTO_INCREMENT COMMENT '' ,
    `coursename` VARCHAR(255)   COMMENT '' ,
    PRIMARY KEY (id)
)  COMMENT = 'course';

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule(
    `id` INT AUTO_INCREMENT COMMENT '' ,
    `class_id` INT   COMMENT '' ,
    `teacher_id` INT   COMMENT '' ,
    `course_id` INT   COMMENT '' ,
    `weeks` INT   COMMENT '' ,
    `lessons` INT   COMMENT '' ,
    `remark` VARCHAR(255)   COMMENT '' ,
    PRIMARY KEY (id)
)  COMMENT = 'schedule';

DROP TABLE IF EXISTS student;
CREATE TABLE student(
    `id` INT AUTO_INCREMENT COMMENT '' ,
    `name` VARCHAR(255)   COMMENT '' ,
    `sex` VARCHAR(255)   COMMENT '' ,
    `class_id` INT   COMMENT '' ,
    PRIMARY KEY (id)
)  COMMENT = 'student';

DROP TABLE IF EXISTS teacher;
CREATE TABLE teacher(
    `id` INT AUTO_INCREMENT COMMENT '' ,
    `name` VARCHAR(255)   COMMENT '' ,
    `sex` VARCHAR(255)   COMMENT '' ,
    `age` VARCHAR(255)   COMMENT '' ,
    PRIMARY KEY (id)
)  COMMENT = 'teacher';

