<template>
    <div class="smart-course-platform">
      <header class="header">
        <h1>用户主页</h1>
        <div class="user-info">
          <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
          <span>{{ username }} ({{ userType === 'student' ? '学生' : '教师' }})</span>
          <button class="btn btn-ghost" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </button>
        </div>
      </header>
      <div class="person-content">
        <el-aside width="250px" class="sidebar">
          <el-menu
            :default-active="selectedTab"
            class="sidebar-menu"
            @select="handleSelect"
          >
            <el-menu-item index="1" @click="selectedTab = 'info'">
              <template #title>
                <span>个人信息</span>
              </template>
            </el-menu-item>
  
            <el-menu-item index="2" @click="selectedTab = 'favorite'">
              <template #title>
                <span>收藏夹</span>
              </template>
            </el-menu-item>
          </el-menu>
        </el-aside>
          
        <main class="main-content">
          <div v-if="selectedTab === 'info'" class="person-info">
            <h2>个人信息</h2>
            <p v-if="userType === 'student'">学号：{{ id }}</p>
            <p v-else>工号：{{ id }}</p>
            <p>姓名：{{ name }}</p>
            <p>邮箱：{{ mail }}</p>
            <p v-if="userType === 'teacher'">办公室：{{ office }}</p>
            <p v-if="userType === 'teacher'">电话：{{ phone }}</p>
            <p v-if="userType === 'teacher'">简介：{{ intro }}</p>
          </div>
  
          <div v-if="selectedTab === 'favorite'" class="person-favorite">
            <h2>收藏夹</h2>
            <div v-if="favorites.length === 0">该用户没有收藏的帖子。</div>
            <div v-else>
              <div v-for="favorite in favorites" :key="favorite.id" class="favorite-item" @click="goToDetail(favorite.dno, favorite.dis_detail.cno)">
                <h3>{{ favorite.dis_detail.dtitle }}</h3>
                <p>{{ favorite.dis_detail.dinfo }}</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { ArrowLeft } from '@element-plus/icons-vue';
  import axios from 'axios';
  
  const INFO_URL = 'http://localhost:8000/home/getinfo';
  const FAVOR_URL = 'http://localhost:8000/homepage/favorite';
  
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
    components: { ArrowLeft },
    setup() {
      const router = useRouter();
      const route = useRoute();
      const favorites = ref([]);
      const id = ref('');
      const name = ref('');
      const mail = ref('');
      const office = ref('');
      const phone = ref('');
      const intro = ref('');
      const username = ref('');
      const userType = ref('');
      const selectedTab = ref('info');
  
      const fetchInfo = async () => {
        try {
          // In a real application, you would pass the user ID as a parameter
          const response = await instance.get(`${INFO_URL}/${route.params.userId}`);
          if (response.status === 200) {
            const data = response.data.data;
            username.value = data.username;
            userType.value = data.userType;
            if (data.userType === 'teacher') {
              id.value = data.tno;
              name.value = data.tname;
              mail.value = data.tmail;
              office.value = data.toffice;
              phone.value = data.tphone;
              intro.value = data.tintro;
            } else {
              id.value = data.sno;
              name.value = data.sname;
              mail.value = data.smail;
            }
          } else {
            console.error('Failed to fetch data:', response.status);
          }
        } catch (error) {
          console.error('Error fetching info:', error);
        }
      };
  
      const fetchFavorites = async () => {
        try {
          // In a real application, you would pass the user ID as a parameter
          const response = await instance.get(`${FAVOR_URL}/${route.params.userId}`);
          const result = await response.data;
          if (result.code === 200) {
            favorites.value = result.data;
          }
        } catch (error) {
          console.error('获取收藏夹数据失败:', error);
        }
      };
  
      const handleSelect = (key) => {
        selectedTab.value = key;
      };
  
      const goBack = () => {
        router.go(-1);
      };
  
      onMounted(async () => {
        await fetchInfo();
        await fetchFavorites();
      });
  
      return {
        favorites,
        id,
        name,
        mail,
        office,
        phone,
        intro,
        username,
        userType,
        selectedTab,
        goBack,
        handleSelect,
      };
    },
    methods: {
      goToDetail(dno, courseNo) {
        this.$router.push({ name: 'Review', params: { dno, courseNo } });
      }
    }
  };
  </script>
  
  <style scoped>
  .smart-course-platform {
    font-family: Arial, sans-serif;
    color: #333;
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
  
  .person-content {
    display: flex;
    min-height: calc(100vh - 80px);
  }
  
  .sidebar {
    width: 200px;
    background-color: #f0f0f0;
    padding: 0px;
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
  
  .favorite-item {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .favorite-item:hover {
    background-color: #f5f5f5;
  }
  
  .favorite-item h3 {
    margin: 0 0 5px 0;
    color: #2563eb;
  }
  
  .favorite-item p {
    margin: 0;
    color: #666;
  }
  </style>