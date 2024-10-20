<template>
    <div class="course-page">
      <header class="course-header">
        <div class="header-left">
          <h1 class="course-title">{{ courseData?.data?.cname || '机器学习' }}</h1>
          <span class="course-info">
            主讲教师: {{ courseData?.data?.teacher?.tname || '张教授' }} |
            课程编号: {{ courseData?.data?.course_no || 'M310006B' }} |
            课序号: {{ courseData?.data?.course_class || '02' }}
          </span>
        </div>
        <div class="header-right">
          <span>学期: {{ semester }}</span>
          <span>当前教学周: 第{{ currentWeek }}周</span>
        </div>
      </header>
      <div class="course-content">
        <aside class="sidebar">
          <h2>课程信息</h2>
          <ul>
            <li @click="selectedTab = 'introduction'" :class="{ active: selectedTab === 'introduction' }">课程介绍</li>
            <li @click="selectedTab = 'syllabus'" :class="{ active: selectedTab === 'syllabus' }">教学大纲</li>
            <li @click="selectedTab = 'calendar'" :class="{ active: selectedTab === 'calendar' }">教学日历</li>
            <li @click="selectedTab = 'notification'" :class="{ active: selectedTab === 'notification' }">课程通知</li>
            <li @click="selectedTab = 'teacher'" :class="{ active: selectedTab === 'teacher' }">教师信息</li>
            <li @click="selectedTab = 'mygroup'" :class="{ active: selectedTab === 'mygroup' }">我的分组</li>
          </ul>
          <h2>课程资源</h2>
          <ul>
            <li>课程资源</li>
            <li>课程视频</li>
          </ul>
          <h2>课程考核</h2>
          <ul>
            <li>作业</li>
            <li>课程报告</li>
            <li>实验</li>
            <li>平时测验</li>
            <li>结课考核</li>
          </ul>
          <h2>答疑讨论</h2>
          <h2>学习档案</h2>
        </aside>
        <main class="main-content">
          <div v-if="selectedTab === 'introduction'" class="course-intro">
            <h2>课程简介</h2>
            <p>{{ courseData?.data?.cintro || '《机器学习》是软件工程专业的一门专业核心必修课。理论与实践相结合，旨在培养学生运用所学的机器学习理论、方法及算法，分析和解决软件工程问题，本课程为软件工程专业本科生在后续方向必选课程中提供强力支撑。在人才培养方面占有重要的地位。本课程系统地介绍机器学习的经典方法与应用现状，线性模型、决策树、感知机、支持向量机、贝叶斯分类器、集成学习、聚类、降维、半监督学习等。此外，本课程注重理论教学与实践的结合，注重学生实践能力的培养，通过设立实践环节来巩固学生对于机器学习算法的正确应用，使学生体会机器学习广泛的应用场景。' }}</p>
          </div>
          <!-- Add other content sections for different tabs here -->
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { useRoute } from 'vue-router';
  
  const API_URL = 'http://localhost:8000/homepage/student/';
  
  export default {
    setup() {
      const route = useRoute();
      const courseNo = route.params.courseNo;
      const courseData = ref(null);
      const selectedTab = ref('introduction');
      const semester = ref('2024-2025第一学期');
      const currentWeek = ref(6);
  
      const fetchCourseData = async () => {
        try {
          const token = localStorage.getItem('token');
          const response = await axios.get(`${API_URL}course/${courseNo}/`, {
            headers: { Authorization: `Bearer ${token}` },
            maxRedirects: 0,
          });
          if (response.status === 200) {
            courseData.value = response.data;
          }
        } catch (error) {
          console.error('Error fetching course data:', error);
        }
      };
  
      onMounted(() => {
        fetchCourseData();
      });
  
      return {
        courseData,
        selectedTab,
        semester,
        currentWeek
      };
    }
  };
  </script>
  
  <style scoped>
  .course-page {
    font-family: Arial, sans-serif;
    color: #333;
  }
  
  .course-header {
    background-color: #4a69bd;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .header-left {
    display: flex;
    flex-direction: column;
  }
  
  .course-title {
    font-size: 24px;
    margin: 0;
  }
  
  .course-info {
    font-size: 14px;
    margin-top: 5px;
  }
  
  .header-right {
    text-align: right;
    font-size: 14px;
  }
  
  .header-right span {
    display: block;
  }
  
  .course-content {
    display: flex;
    min-height: calc(100vh - 80px);
  }
  
  .sidebar {
    width: 200px;
    background-color: #f0f0f0;
    padding: 20px;
  }
  
  .sidebar h2 {
    font-size: 16px;
    margin-top: 20px;
    margin-bottom: 10px;
  }
  
  .sidebar ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }
  
  .sidebar li {
    padding: 5px 0;
    cursor: pointer;
  }
  
  .sidebar li:hover, .sidebar li.active {
    color: #4a69bd;
  }
  
  .main-content {
    flex-grow: 1;
    padding: 20px;
  }
  
  .course-intro h2 {
    font-size: 18px;
    margin-bottom: 10px;
  }
  
  .course-intro p {
    line-height: 1.6;
  }
  </style>