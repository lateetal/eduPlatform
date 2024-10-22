<template>
  <div class="student-home">
    <header class="header">
      <h1>教师主页</h1>
      <div class="user-info">
        <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
        <span>{{ username }} (教师)</span>
        <button class="btn btn-ghost">
          <User class="icon-user" />
          个人中心
        </button>
        <button class="btn btn-ghost">
          <LogOut class="icon-logout" />
          安全退出
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
          <ul class="notification-list">
            <li v-for="notification in notifications" :key="notification.id">
              <span class="notification-title">{{ notification.title }}</span>
              <span class="notification-date">{{ notification.date }}</span>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'
import { User, LogOut } from 'lucide-vue-next'

const API_URL = 'http://localhost:8000/homepage/teacher/'
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com'
const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'

// 创建 Axios 实例
const instance = axios.create();

// 添加请求拦截器
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); // 从本地存储获取令牌
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default {
  components:{User, LogOut},
  name: 'TeacherHome',
  data() {
    return {
      subjects: [],
      username: '',
      userType:'',
      loading: true,
      error: null,
      BUCKET_URL,
      notifications: [
      { id: 1, title: "智慧课程平台操作手册（学生版）", date: "2024-02-23" },
      { id: 2, title: "关于开展2024年春季学期教学检查的通知", date: "2024-02-20" },
      { id: 3, title: "2024年春季学期开学温馨提示", date: "2024-02-18" },
      ]
    }
  },
  mounted() {
    this.fetchSubjects()
    this.fetchUsername()
  },
  methods: {
    async fetchSubjects() {
      try {
        const token = localStorage.getItem('token')
        const response = await instance.get(API_URL, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        if (response.data.code === 200) {
          this.subjects = response.data.data || []
        } else {
          this.error = '获取科目失败'
        }
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    async fetchUsername() {
      try {
        const response = await instance.get(USERNAME_URL)
        if (response.status === 200) {
          const {username,userType} = response.data

          this.userType = userType
          this.username = username

          if(userType != 'teacher'){
            this.error = '用户权限不足'
          }
        } else {
          this.error = '获取用户名失败'
        }
      } catch (err) {
        this.error = err.message
      }
    },
    handleCourseClick(courseNo) {
      this.$router.push(`/teacher/course/${courseNo}/`)
    }
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