<template>
    <div class="course-page">
      <header class="course-header">
        <div class="header-left">
          <h1 class="course-title">{{ courseData?.data?.cname || 'cname' }}</h1>
          <span class="course-info">
            主讲教师: {{ courseData?.data?.teacher?.tname || 'tname' }} |
            课程编号: {{ courseData?.data?.course_no || 'course_no' }} |
            课序号: {{ courseData?.data?.course_class || 'course_class' }}
          </span>
        </div>
      </header>
      <div class="course-content">
        <el-aside width="250px" class="sidebar">
          <el-menu
            :default-active="selectedTab"
            class="sidebar-menu"
            @select="handleSelect"
          >
            <el-sub-menu index="1">
              <template #title>
                <el-icon><Location /></el-icon>
                <span>课程信息</span>
              </template>
              <el-menu-item index="1-1" @click="selectedTab = 'introduction'">
                课程介绍</el-menu-item>
              <el-menu-item index="1-2" @click="selectedTab = 'outline'">
                教学大纲</el-menu-item>
              <el-menu-item index="1-3" @click="selectedTab = 'calendar'">
                教学日历</el-menu-item>
              <el-menu-item index="1-4" @click="selectedTab = 'professor'">
                教师信息</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="2">
              <template #title>
                <el-icon><Folder /></el-icon>
                <span>课程资源</span>
              </template>
              <el-menu-item index="2-1" @click="selectedTab = 'ppts'">
                课件</el-menu-item>
              <el-menu-item index="2-2" @click="selectedTab = 'papers'">
                历年试题库</el-menu-item>
              <el-menu-item index="2-3" @click="selectedTab = 'exercises'">
                习题库</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="3">
              <template #title>
                <el-icon><DataBoard /></el-icon>
                <span>课程考核</span>
              </template>
              <el-menu-item index="3-1" @click="selectedTab = 'homework'">作业</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="4">
              <template #title>
                <el-icon><ChatDotRound /></el-icon>
                <span>答疑讨论</span>
              </template>
              <el-menu-item index="4-1">讨论区</el-menu-item>
              <el-menu-item index="4-2" @click="selectedTab = 'AIhelper'">AI问答</el-menu-item>
            </el-sub-menu>

            <el-sub-menu index="5">
              <template #title>
                <el-icon><Bell /></el-icon>
                <span>课程通知</span>
              </template>
              <el-menu-item index="5-1" @click="selectedTab = 'notice'">通知</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>
          
        <main class="main-content">
          <div v-if="selectedTab === 'introduction'" class="course-intro">
            <h2>课程介绍</h2>
            <p>{{ courseData?.data?.cintro || 'cintro' }}</p>
          </div>
          <div v-if="selectedTab === 'outline'" class="course-outline">
            <h2>教学大纲</h2>
            <p>{{ courseData?.data?.coutline || 'coutline' }}</p>
          </div>
          <div v-if="selectedTab === 'calendar'" class="course-calendar">
            <h2>教学日历</h2>
            <p>{{ courseData?.data?.calendar || 'calendar' }}</p>
          </div>
          <div v-if="selectedTab === 'professor'" class="course-professor">
            <h2>教师信息</h2>
            <p>{{ courseData?.data?.teacher?.tname || 'tname'}}</p>
          </div>

          <div v-if="selectedTab === 'ppts'" class="course-ppts">
            <h2>课件</h2>
          </div>
          <div v-if="selectedTab === 'papers'" class="course-papers">
            <h2>历年试题库</h2>
          </div>
          <div v-if="selectedTab === 'exercises'" class="course-exercises">
            <h2>习题库</h2>
          </div>

          <div v-if="selectedTab === 'homework'" class="course-homework">
            <h2>作业</h2>
          </div>

          <div v-if="selectedTab === 'AIhelper'" class="course-AIhelper">
            <h2>AI助手</h2>
          </div>

          <div v-if="selectedTab === 'notice'" class="course-notice">
            <h2>通知</h2>
          </div>
        </main>
      </div>
    </div>
  </template>

  <script>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { useRoute } from 'vue-router';
  import { Location, Folder, ChatDotRound, DataBoard, Bell } from '@element-plus/icons-vue';
  
  const API_URL = 'http://localhost:8000/homepage/student/';
  
  export default {
    components:{
      Location,
      Folder,
      ChatDotRound,
      DataBoard,
      Bell,
    },

    setup() {
      const route = useRoute();
      const courseNo = route.params.courseNo;
      const courseData = ref(null);
      const selectedTab = ref('introduction');
  
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

      const handleSelect = (key) => {
        selectedTab.value = key;
      };
  
      onMounted(() => {
        fetchCourseData();
      });
  
      return {
        courseData,
        selectedTab,
        handleSelect,
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
  
  </style>