<template>
    <div class="smart-course-platform">
      <header class="header">
        <h1>用户主页</h1>
        <div class="user-info">
          <button class="btn btn-ghost" @click="isFollowed?delFollow():followUser()">{{ isFollowed?'已关注':'关注' }}</button>
          <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
          <span>{{ id }} ({{ userType === 'student' ? '学生' : '教师' }})</span>
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
            <div class="folder-list">
              <el-collapse v-if="folders.length > 0" accordion>
                <el-collapse-item v-for="folder in folders" :key="folder.fno" @click="getFavor(folder.fno)">
                    <template #title>
                      <span class="folder-name">{{folder.fname}}</span>
                      <div class="folder-btn">
                        <span>赞：{{ folder.likeNum }}</span>
                        <el-button type="primary" @click="favorFolder(folder.fno)" v-if="username !== id">
                          {{ isFavored(folder.fno)?'已收藏':'收藏' }}
                        </el-button>
                        <el-button type="primary" @click="likeFolder(folder)">
                          {{ folder.is_liked?'已点赞':'点赞' }}
                        </el-button>
                      </div>
                    </template>
                  <div>
                    <ul>
                      <li v-for="discussion in folderDiscussions" :key="discussion.id" class="discussion-list">
                        <p>
                          <button @click="delFavorDialog(discussion)">删除</button>
                        <span @click="goToDiscussion(discussion.dis_detail)">{{discussion.dis_detail.dtitle}}</span>
                        </p>
                      </li>  
                    </ul>
                  </div>
                </el-collapse-item>
              </el-collapse>
              <span v-else>暂无收藏夹</span>
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
  import {getUsernameService} from '@/api/homepage.js'
  
  const INFO_URL = 'http://localhost:8000/home/getinfo';
  
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
      const folders = ref([]);
      const id = ref('');
      const name = ref('');
      const mail = ref('');
      const office = ref('');
      const phone = ref('');
      const intro = ref('');
      const userType = ref('');
      const selectedTab = ref('info');
      const isFollowed = ref(false);
      const folderDiscussions = ref([]);
      const favoredFolders = ref([]);
      const username = ref('');

      const fetchUsername = async () => {
        let result = await getUsernameService();
        username.value = result.data.username;
        console.log(username.value);
      }
      
  
      const fetchInfo = async () => {
        try {
          // In a real application, you would pass the user ID as a parameter
          const response = await instance.get(`${INFO_URL}/${route.params.userId}`);
          if (response.status === 200) {
            const data = response.data.data;
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
  
      const handleSelect = (key) => {
        selectedTab.value = key;
      };
  
      const goBack = () => {
        router.go(-1);
      };

      const followUser = async () => {
        const API_URL = 'http://localhost:8000/chatRoom/getfollower'
        try{
          const response = await instance.post(API_URL,{
            follower:id.value
          })
          if(response.data.code === 200){
            alert('关注成功');
            fetchIsFollowed();
          }else if(response.data.code === 403){
            alert('不能关注自己');
          }
        }catch(err){
          console.error(err);
        }
      }
      const fetchIsFollowed = async() => {
        const API_URL = 'http://localhost:8000/chatRoom/getfollower';
        try{
          const response = await instance.get(API_URL);
          if(response.status === 200){
            isFollowed.value = response.data.data.some(item => item.followedUsername === id.value);
          }
        }catch(err){
          console.error(err);
        }
      }

      const delFollow = async() => {
        const API_URL = 'http://localhost:8000/chatRoom/getfollower';
        try{
          const response = await instance.delete(API_URL,{
            data:{
              follower:id.value
            }
          });
          if(response.status === 200){
            alert('取消关注成功');
            fetchIsFollowed();
          }
        }catch(err){
          console.error(err);
        }
      }

      //获取当前主页的收藏夹
      const fetchFolders = async() => {
        try{
          const response = await instance.get(`http://localhost:8000/chatRoom/all/folder/${id.value}`);
          if(response.status === 200){
            folders.value = response.data.data.personal_folders.filter(item => item.fstatus === true);
          }
        }catch(err){
          console.error(err);
        }
      }

      //获取收藏夹下的讨论
      const getFavor = async(fno) => {
        const API_URL = `http://localhost:8000/chatRoom/folder/${fno}`;
        try{
          const response = await instance.get(API_URL);
          if(response.status === 200 ){
            folderDiscussions.value = response.data.data.favorites;
          }
        }catch(err){
          console.error(err);
        }
      }

      //收藏或取消收藏 收藏夹
      const favorFolder = async(fno) => {
        const API_URL = `http://localhost:8000/chatRoom/collectOtherFolder`;
        if(isFavored(fno)){
          try{
            const response = await instance.delete(API_URL,{
              data:{
                fno:fno
              }
            });
            if(response.status === 200){
              alert('取消收藏成功');
              fetchFavoredFolders();
            }
          }catch(err){
            console.log(err);
          }
        }
        else{
          try{
            const response = await instance.post(API_URL,{
              fno:fno
            });
            if(response.status === 200 ){
              alert('收藏成功');
              fetchFavoredFolders();
            }
          }catch(err){
            console.error(err);
          }
        }
      }

      //获取用户收藏的收藏夹
      const fetchFavoredFolders = async() => {
        try{
          const response = await instance.get(`http://localhost:8000/chatRoom/all/folder/0`);
          if(response.status === 200){
            favoredFolders.value = response.data.data.others_folders;
          }
        }catch(err){
          console.error(err);
        }
      }

      const isFavored = (fno) => {
        if(favoredFolders.value.length === 0){
          return false;
        }else if(favoredFolders.value.some(item => item.fno === fno)){
          return true;
        }
        return false;
      }

      const likeFolder = async(folder) => {
        try{
          const response = await instance.post('http://localhost:8000/chatRoom/like/folder',{
            fno:folder.fno
          })
          if(response.status === 200){
            alert(folder.is_liked?'取消点赞成功':'点赞成功');
            fetchFolders();
          }
        }catch(err){
          console.log(err);
        }
      }
  
      onMounted(async () => {
        await fetchInfo();
        await fetchIsFollowed();
        await fetchFolders();
        await fetchFavoredFolders();
        await fetchUsername();
      });
  
      return {
        id,
        name,
        mail,
        office,
        phone,
        intro,
        userType,
        selectedTab,
        folders,
        isFollowed,
        folderDiscussions,
        favoredFolders,
        username,

        goBack,
        handleSelect,
        followUser,
        delFollow,
        getFavor,
        favorFolder,
        isFavored,
        likeFolder,
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
  
  .folder-name {
  font-size: 18px;
  width: 200px;
}

.folder-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 60%;
}

.folder-btn span{
  width:50px;
}

.discussion-list p:hover {
  color: #4769ff;
  font-weight: bold;
  cursor: pointer;
}

.el-collapse-item .el-collapse-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
  </style>