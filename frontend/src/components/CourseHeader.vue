<template>
    <header class="course-header">
      <div class="header-left">
        <h1 class="course-title">{{ courseData?.data?.cname || 'Course Name' }}</h1>
        <span class="course-info">
          主讲教师: {{ courseData?.data?.teacher?.tname || 'Teacher Name' }} |
          课程编号: {{ courseData?.data?.course_no || 'Course No' }} |
          课序号: {{ courseData?.data?.course_class || 'Class No' }}
        </span>
      </div>
    </header>
</template>
  
<script>
export default {
    props: ['courseData'],
};
</script>
  
<style scoped>
.course-header {
    background-color: #4a69bd;
    color: white;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
  
.header-left {
    display: flex;
    flex-direction: column;
}
  
.course-title {
    font-size: 28px;
    margin: 0;
    font-weight: 600;
}
  
.course-info {
    font-size: 14px;
    margin-top: 10px;
    opacity: 0.9;
}
</style>