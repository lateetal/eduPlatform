<template>
  <div class="student-home">
    <header class="header">
      <h1>教师主页</h1>
      <div class="user-info">
        <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
        <span>{{ username }} (教师)</span>
        <button class="btn btn-ghost" @click="goHome">
          <el-icon><User /></el-icon>
          个人中心
        </button>
        <button class="btn btn-ghost" @click="logout" >
          <el-icon><TopRight /></el-icon>
          退出
        </button>
      </div>
    </header>

    <main class="main-content">
      <div class="course-list">
        <h2>欢迎, {{ username }}!</h2>
        <div v-if="loading">加载中...</div>
        <div v-else-if="error" class="error">发生错误: {{ error }}</div>
        <div v-else>
          <div v-if="subjects.length > 0" class="course-grid">
            <div v-for="(subject, index) in subjects" :key="index" class="course-card">
              <img
                class="course-img"
                :src="`${BUCKET_URL}${subject.picAddr}`"
                :alt="subject.cname"
              />
              <div class="course-info">
                <h3 :title="subject.cname">{{ subject.cname }}</h3>
                <p :title="subject.course_no">
                  <span class="label">课程号：</span>{{ subject.course_no }}
                </p>
                <p :title="subject.course_class">
                  <span class="label">班级：</span>{{ subject.course_class }}
                </p>
                <button @click="handleCourseClick(subject.cno)" class="btn btn-primary">
                  查看课程详情
                </button>
              </div>
            </div>
          </div>
          <p v-else>没有任教科目</p>
        </div>
      </div>
      <div class="sidebar">
        <div class="notification-card">
          <h2>
            <i class="icon-bell"></i>
            通知公告
          </h2>
          <ul v-if="notifications.length > 0" class="notification-list">
            <li v-for="notification in notifications" :key="notification.id">
              <span class="notification-title">{{ notification.mtitle }}</span>
              <span class="notification-info">{{ notification.minfo }}</span>
              <span class="notification-date">{{ formatDate(notification.mtime) }}</span>
            </li>
          </ul>
          <p v-else-if="notice_error">{{ notice_error }}</p>
          <p v-else>暂无数据</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'
import { User, TopRight } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus'

const API_URL = 'http://localhost:8000/homepage/teacher/'
const NOTIFICATIONS_URL = 'http://localhost:8000/homepage/course/message' // New endpoint for notifications
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com'
const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'

const instance = axios.create();
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default {
  components: { User, TopRight },
  name: 'TeacherHome',
  data() {
    return {
      subjects: [],
      username: '',
      userType: '',
      loading: true,
      error: null,
      notice_error: null,
      notifications: [],
      BUCKET_URL,
    }
  },
  mounted() {
    this.fetchSubjects();
    this.fetchUsername();
    this.fetchCourseMessage(); 
  },
  methods: {
    async fetchSubjects() {
      try {
        const response = await instance.get(API_URL);
        if (response.data.code === 200) {
          this.subjects = response.data.data || [];
        } else {
          this.error = '获取科目失败';
        }
      } catch (err) {
        ElMessage.error('请先登录');
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    async fetchUsername() {
      try {
        const response = await instance.get(USERNAME_URL);
        if (response.status === 200) {
          const { username, userType } = response.data;
          this.userType = userType;
          this.username = username;

          if (userType !== 'teacher') {
            this.error = '用户权限不足';
          }
        } else {
          this.error = '获取用户名失败';
        }
      } catch (err) {
        this.error = err.message;
      }
    },
    async fetchCourseMessage() {
      try {
        const response = await instance.get(NOTIFICATIONS_URL);
        if (response.data.code === 200) {
          this.notifications = response.data.data || [];
          console.log(this.notifications);
        } else {
          this.notice_error = '获取通知失败';
        }
      } catch (err) {
        this.notice_error = err.message;
      }
    },

    handleCourseClick(courseNo) {
      this.$router.push(`/course/${courseNo}/`);
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    },
    goHome() {
      this.$router.push('/home');
    },

    formatDate(dateString) {//处理时间
            const date = new Date(dateString);
            return date.toISOString().split('T')[0]; // 只返回日期部分
    },

  }
}
</script>

<style scoped>
.student-home {
  min-height: 100vh;
  background-color: #f3f4f6;
}

.header {
  background-color: #2563eb;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.btn-ghost {
  background-color: transparent;
  color: white;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.main-content {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

@media (min-width: 1024px) {
  .main-content {
    flex-direction: row;
  }

  .course-list {
    width: 66.666667%;
    padding-right: 1rem;
  }

  .sidebar {
    width: 33.333333%;
  }
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.course-card {
  background-color: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.course-img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.course-info {
  padding: 1rem;
}

.label {
  font-weight: 600;
}

.notification-card, .calendar-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.notification-list {
  list-style-type: none;
  padding: 0;
}

.notification-list li {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.notification-title {
  color: #2563eb;
  cursor: pointer;
}

.notification-title:hover {
  text-decoration: underline;
}

.notification-date {
  color: #6b7280;
  font-size: 0.875rem;
}

.error {
  color: #dc2626;
}
</style>