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
            退出
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

            <el-menu-item index="3" @click="selectedTab = 'folder'">
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
            <el-form :model="form" label-width="auto">
              <el-form-item v-if="userType==='teacher'" label="工号">
                <el-input v-model="form.id" disabled/>
              </el-form-item>
              <el-form-item v-if="userType==='student'" label="学号">
                <el-input v-model="form.id" disabled/>
              </el-form-item>
              <el-form-item label="姓名">
                <el-input v-model="form.name" disabled/>
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="form.mail"/>
              </el-form-item>
              <el-form-item v-if="userType === 'teacher'" label="办公室">
                <el-input v-model="form.office"/>
              </el-form-item>
              <el-form-item v-if="userType === 'teacher'" label="电话">
                <el-input v-model="form.phone"/>
              </el-form-item>
              <el-form-item v-if="userType === 'teacher'" label="简介">
                <el-input v-model="form.intro"/>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="onSubmit">提交修改</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div v-if="selectedTab === 'psw'" class="person-psw">
            <h2>修改密码</h2>
            <p>旧密码：<input type="password" v-model="oldPassword" /></p>
            <p>新密码：<input type="password" v-model="newPassword" /></p>
            <p>确认密码：<input type="password" v-model="confirmPassword" /></p>
            <button @click= "updatePassword" >提交</button>
            <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
            <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
          </div>

          <div v-if="selectedTab === 'folder'" class="person-folder">
            <h2>收藏夹</h2>
            <div class="folder-list">
              <ul>
                <li v-for="folder in folders" :key="folder.fno">
                  <div class="folder-item">
                    <h3>{{ folder.fname }}</h3>
                    <div class="folder-btn">
                      <el-switch
                        v-model="folder.fstatus"
                        active-text="公开"
                        disabled
                      />
                      <el-button type="primary">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                    </div>
                    
                  </div>
                  
                </li>
              </ul>
            </div>
          </div>

          <div v-if="selectedTab === 'follow'" class="person-follow">
            <h2>关注列表</h2>
            <div class="follow-list">
              <ul>
                <li v-for="follow in follows" :key="follow.username">
                  <h3 @click="goToUser(follow.username)">{{ follow.username }}</h3>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="selectedTab === 'fans'" class="person-fans">
            <h2>粉丝列表</h2>
            <div class="fan-list">
              <ul>
                <li v-for="fan in fans" :key="fan.username">
                  <h3 @click="goToUser(fan.username)">{{ fan.username }}</h3>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="selectedTab === 'message'" class="person-message">
             <h2>互动消息</h2>
            <div v-if="atmessages.length > 0">
              <el-list>
                <el-list-item
                  v-for="(message) in atmessages"
                  :key="message.id"
                  :class="{'unread': !message.status}"
                  @click="viewReview(message)"
                >
                  <div>
                    <span v-if="!message.status" class="message-unread">[未读]</span>
                    <span v-if="message.status" class="message-read">[已读]</span>
                    {{ message.rinfo }}
                  </div>
                </el-list-item>
              </el-list>
            </div>

          </div>

        </main>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { School, TopRight, Edit  } from '@element-plus/icons-vue';
  import axios from 'axios'
  import {ElMessage} from "element-plus";

  const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'
  const INFO_URL = 'http://localhost:8000/home/getinfo'
  const UPDATE_URL = 'http://localhost:8000/home/updatePassword'
  const ATMESSAGE_URL = 'http://localhost:8000/chatRoom/atmessage'

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


  export default {
  components: { School, TopRight, Edit },
  setup() {
    const form = ref({
      id: '',
      name: '',
      mail: '',
      office: '',
      phone: '',
      intro: '',
    });
    const router = useRouter();
    const oldPassword = ref('');
    const newPassword = ref('');
    const confirmPassword = ref('');
    const errorMessage = ref('');
    const successMessage = ref('');
    const error = ref('');
    const username = ref('');
    const userType = ref('');
    const selectedTab = ref('info');
    const atmessages = ref([]);

    const follows = ref([
      {
        username:'22301001',
      },
      {
        username:'22301018',
      },
    ]);

    const fans = ref([
      {
        username:'22301001',
      },
      {
        username:'22301082',
      },
    ]);

    const folders = ref([
      {
        fno:1,
        fname:'实训',
        fstatus:true,
      },
      {
        fno:2,
        fname:'笔记',
        fstatus:false,
      },
    ])

    const fetchUsername = async () => {
      try {
        const response = await instance.get(USERNAME_URL);
        if (response.status === 200) {
          const { username: fetchedUsername, userType: fetchedUserType } = response.data;
          username.value = fetchedUsername;
          userType.value = fetchedUserType;
        } else {
          error.value = '获取用户名失败';
        }
      } catch (err) {
        error.value = err.message;
      }
    };

    const fetchInfo = async () => {
      try {
        const response = await instance.get(INFO_URL);
        if (response.status === 200) {
          const data = response.data.data;
          if (userType.value === 'teacher') {
            form.value.id = data.tno;
            form.value.name = data.tname;
            form.value.mail = data.tmail;
            form.value.office = data.toffice;
            form.value.phone = data.tphone;
            form.value.intro= data.tintro;
          } else {
            form.value.id = data.sno;
            form.value.name = data.sname;
            form.value.mail = data.smail;
          }
        } else {
          console.error('Failed to fetch data:', response.status);
        }
      } catch (error) {
        console.error('Error fetching info:', error);
      }
    };

    const handleSelect = (key) => {
      selectedTab.value = key;
    };

    const goHome = () => {
      if(userType.value === 'student'){
        router.push('/student');
      }else if(userType.value === 'teacher'){
        router.push('/teacher');
      }
      
    };

    const logout = () => {
      localStorage.removeItem('token');
      router.push('/login');
    };

    const goToUser = (username) => {
      router.push(`/user/${username}`);
    }

    const fetchAtmessage = async () => {
      const response = await instance.get(ATMESSAGE_URL);
      if(response.status === 200){
        atmessages.value = response.data.data;
      } else {
        this.errorMessage = '请求@信息失败，请稍后再试';
        console.error(error);
      }
    };


    onMounted(async () => {
      await fetchUsername();
      await fetchInfo();
      await fetchAtmessage();

    });

    return {
      form,
      oldPassword,
      newPassword,
      confirmPassword,
      errorMessage,
      successMessage,
      error,
      username,
      userType,
      selectedTab,
      atmessages,
      follows,
      fans,
      folders,

      logout,
      goHome,
      goToUser,
      handleSelect,
    };
  },
  methods: {
    async updatePassword() {
      this.errorMessage = '';
      this.successMessage = '';

      try {
        const response = await axios.post(UPDATE_URL, {
          oldPassword: this.oldPassword,
          newPassword: this.newPassword,
          confirmPassword: this.confirmPassword,
        });
        if (response.status === 200) {
          ElMessage.success('密码修改成功');
          this.oldPassword = '';
          this.newPassword = '';
          this.confirmPassword = '';
          this.logout();
        } else {
          this.errorMessage = response.data.error || '修改失败，请检查输入是否正确';
        }
      } catch (error) {
        this.errorMessage = '请求失败，请稍后再试';
        console.error(error);
      }
    },
    goToDetail(dno,courseNo) {
      // 跳转到讨论详情页
      this.$router.push({name: 'Review', params: {dno,courseNo}});
    },

    //根据@信息跳转到对应帖子详情
    async viewReview(message){
      await instance.post(ATMESSAGE_URL,{
        messageId: message.id
      });
      const url = `course/${message.cno}/discussion/${message.dno}`;
      this.$router.push(url);
    },

  }
};
  </script>
  
  <style scoped>
  .follow-list h3:hover {
    color: #4769ff; 
    font-weight: bold; 
    cursor: pointer;  
  }

  .fan-list h3:hover {
    color: #4769ff; 
    font-weight: bold; 
    cursor: pointer;  
  }

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
  
  .folder-item {
    display: flex; 
    align-items: center; 
    gap: 60%; /* 控制 p 和 el-switch 之间的间距 */
  }

  .folder-btn {
    display: flex; 
    align-items: center; 
    gap: 10px; /* 控制 p 和 el-switch 之间的间距 */
  }
  </style>