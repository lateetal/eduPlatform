<template>
    <div class="smart-course-platform">
      <header class="header">
        <h1>个人主页</h1>
        <div class="user-info">
          <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
          <span v-if="userType=='student'">{{ username }} (学生)</span>
          <span v-else>{{ username }} (教师)</span>
          <button class="btn btn-ghost" @click="goHome">
              <el-icon><School /></el-icon>
              课程主页
          </button>
          <button class="btn btn-ghost" @click="logout" >
            <el-icon  ><TopRight /></el-icon>
            安全退出
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

            <el-menu-item index="2" @click="selectedTab = 'psw'">
              <template #title>
                <span>修改密码</span>
              </template>
            </el-menu-item>

            <el-menu-item index="3" @click="selectedTab = 'favorite'">
              <template #title>
                <span>收藏夹</span>
              </template>
            </el-menu-item>

            <el-menu-item index="4" @click="selectedTab = 'follow'">
              <template #title>
                <span>关注列表</span>
              </template>
            </el-menu-item>

            <el-menu-item index="5" @click="selectedTab = 'fans'">
              <template #title>
                <span>粉丝列表</span>
              </template>
            </el-menu-item>

            <el-menu-item index="6" @click="selectedTab = 'message'">
              <template #title>
                <span>互动消息</span>
              </template>
            </el-menu-item>
          </el-menu>
        </el-aside>
          
        <main class="main-content">
          <div v-if="selectedTab === 'info'" class="person-info">
            <h2>个人信息</h2>
            <p v-if="userType=='student'">学号：</p>
            <p v-else>工号：</p>
            <p>姓名：</p>
            <p>邮箱：</p>
          </div>
          
          <div v-if="selectedTab === 'psw'" class="person-psw">
            <h2>修改密码</h2>
            <p>新密码：</p>
            <p>确认密码：</p>
          </div>

          <div v-if="selectedTab === 'favorite'" class="person-favorite">
            <h2>收藏夹</h2>
            <p>帖1</p>
          </div>

          <div v-if="selectedTab === 'follow'" class="person-follow">
            <h2>关注列表</h2>
            <p>22301018</p>
          </div>

          <div v-if="selectedTab === 'fans'" class="person-fans">
            <h2>粉丝列表</h2>
            <p>22301082</p>
          </div>

          <div v-if="selectedTab === 'message'" class="person-message">
            <h2>互动消息</h2>
            <p>qzx @你</p>
          </div>
        </main>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { School, TopRight } from '@element-plus/icons-vue';
  import axios from 'axios'

  const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'

  const instance = axios.create();
  instance.interceptors.request.use(config => {
    const token = localStorage.getItem('token'); // 从本地存储获取令牌
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
    }, error => {
    return Promise.reject(error);
});
  
  
  export default{
      components:{School,TopRight},
      setup(){
        const router = useRouter();
        const selectedTab = ref('info');
        const username = ref('');
        const userType = ref('');
        const error = ref('');

        const fetchUsername = async () => {
            try {
                const response = await instance.get(USERNAME_URL);
                if (response.status === 200) {
                    const { username: fetchedUsername, userType: fetchedUserType } = response.data;

                    username.value = fetchedUsername; // 更新 username
                    userType.value = fetchedUserType; // 更新 userType
                } else {
                    error.value = '获取用户名失败'; // 设置获取失败错误
                }
            } catch (err) {
                error.value = err.message; // 捕获并设置错误信息
            }
        };


        const handleSelect = (key) => {
            selectedTab.value = key;
        };

        const goHome = () => {
            router.push('/student')
        }

        const logout = () => {
            localStorage.removeItem('token');
            router.push('/login')
        };

        onMounted(() => {
            fetchUsername();
        });

        return{
            logout,
            goHome,
            selectedTab,
            handleSelect,
            username,
            userType,
            error,
        }
      },
  
      
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
  
  </style>