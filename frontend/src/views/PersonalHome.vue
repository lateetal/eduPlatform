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
            <div class="folder-header">
              <h2>收藏夹</h2>
              <el-button type="primary" @click="createFolderDialog()">
                创建收藏夹
              </el-button>
            </div>
            
            <div class="folder-list">
              <el-collapse v-if="folders.length > 0" accordion>
                <el-collapse-item v-for="folder in folders" :key="folder.fno" @click="getFavor(folder.fno)">
                    <template #title>
                      <span class="folder-name">{{folder.fname}}</span>
                      <div class="folder-btn">
                        <span>赞：{{ folder.likeNum }}</span>
                        <el-switch
                          v-model="folder.fstatus"
                          active-text="公开"
                          disabled
                        />
                        <el-button type="primary" @click="editFolderDialog(folder)">
                          <el-icon><Edit /></el-icon>
                        </el-button>
                        <el-button type="primary" @click="deleteFolderDialog(folder)">
                          <el-icon><Delete /></el-icon>
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

            <div class="other-folders">
              <h2>收藏的收藏夹</h2>
              <el-collapse v-if="otherFolders.length>0" accordion>
                <el-collapse-item v-for="folder in otherFolders" :key="folder.fno" @click="getFavor(folder.fno)">
                    <template #title>
                      <span class="folder-name">{{folder.fname}}</span>
                      <div class="folder-btn">
                        <el-button type="primary" @click="delFavoredFolder(folder.fno)">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                    </template>
                  <div>
                    <ul>
                      <li v-for="discussion in otherDiscussions" :key="discussion.id" class="discussion-list">
                        <p>
                        <span @click="goToDiscussion(discussion.dis_detail)">{{discussion.dis_detail.dtitle}}</span>
                        </p>  
                      </li>  
                    </ul>
                  </div>
                </el-collapse-item>
              </el-collapse>
              <span v-else>暂无收藏的收藏夹</span>
            </div>
          </div>

          <div v-if="selectedTab === 'follow'" class="person-follow">
            <h2>关注列表</h2>
            <div class="follow-list">
              <ul v-if="follows.length > 0">
                <li v-for="follow in follows" :key="follow.followed" class="follow-item">
                  <button @click="delFollow(follow.followedUsername)" class="delFollow-btn">移除</button>
                  <h3 @click="goToUser(follow.followedUsername)">{{ follow.followedName }} {{ follow.followedUsername }}</h3>
                </li>
              </ul>
              <span v-else>暂无关注</span>
            </div>
          </div>

          <div v-if="selectedTab === 'fans'" class="person-fans">
            <h2>粉丝列表</h2>
            <div class="fan-list">
              <ul v-if="fans.length > 0">
                <li v-for="fan in fans" :key="fan.fan_id" class="fan-item">
                  <button @click="delFan(fan.fanUsername)" class="delFan-btn">移除</button>
                  <h3 @click="goToUser(fan.fanUsername)">{{ fan.fanName }} {{ fan.fanUsername }}</h3>
                </li>
              </ul>
              <span v-else>暂无粉丝</span>
            </div>
          </div>

          <div v-if="selectedTab === 'message'" class="person-message">
             <h2>互动消息</h2>
            <div v-if="atmessages.length > 0">
              <ul>
                <li
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
                </li>
              </ul>
            </div>
          </div>
        </main>
      </div>
      <el-dialog
        :title="folderDialogTitle"
        v-model="folderDialogVisible"
        width="50%"
      >
        <el-form :model="folderForm">
          <el-form-item label="名称">
            <el-input
              type="textarea"
              v-model="folderForm.fname"
              :rows="1"
            ></el-input>
          </el-form-item>
          <el-form-item label="公开">
            <el-switch
              v-model="folderForm.fstatus"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="folderDialogVisible = false;clearFolderDialog()">取消</el-button>
            <el-button type="primary" @click="folderDialogVisible = false;handleFolderSubmit()">提交</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog
        v-model="deleteFolderDialogVisible"
        title="提示"
        width="50%"
      >
        <span>确定删除收藏夹吗？</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="deleteFolderDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="deleteFolderDialogVisible = false;deleteFolder()">
              确定
            </el-button>
          </div>
        </template>
      </el-dialog>

      <el-dialog
        v-model="delFavorDialogVisible"
        title="提示"
        width="50%"
      >
        <span>确定删除收藏 "{{ delDiscussion.dis_detail.dtitle }}" 吗？</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="delFavorDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="delFavorDialogVisible = false;delFavor()">
              确定
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { School, TopRight, Edit, Delete  } from '@element-plus/icons-vue';
  import axios from 'axios'
  import {ElMessage} from "element-plus";

  const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'
  const INFO_URL = 'http://localhost:8000/home/getinfo/0'
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
  components: { School, TopRight, Edit, Delete },
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
    const folderDialogVisible = ref(false);
    const folderDialogTitle = ref('');
    const deleteFolderDialogVisible = ref(false);
    const delFname = ref('');
    const delFavorDialogVisible = ref(false);
    const delDiscussion = ref({});

    const folderForm = ref({
      fno:0,
      fname:'',
      fstatus: true,
    })

    const follows = ref([]);
    const fans = ref([]);
    const folders = ref([]);
    const folderDiscussions = ref([]);
    const otherFolders = ref([]);
    const otherDiscussions = ref([]);

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

    const clearFolderDialog = () => {
      folderForm.value.fname = '';
      folderForm.value.fname = true;
    }

    const editFolderDialog = (folder) => {
      folderDialogTitle.value = '编辑收藏夹';
      folderDialogVisible.value = true;
      folderForm.value.fno = folder.fno;
      folderForm.value.fname = folder.fname;
      folderForm.value.fstatus = folder.fstatus;
    }

    const deleteFolderDialog = (folder) => {
      delFname.value = folder.fname;
      deleteFolderDialogVisible.value = true;
    }

    const createFolderDialog = () => {
      folderDialogTitle.value = '创建收藏夹';
      folderDialogVisible.value = true;
      folderForm.value.fname = '';
      folderForm.value.fstatus = true;
    }

    const handleFolderSubmit = () => {
      if(folderDialogTitle.value === '创建收藏夹'){
        createFolder();
      }else if(folderDialogTitle.value === '编辑收藏夹'){
        editFolder();
      }
    }

    const createFolder = async () => {
      try {
        const response = await instance.post('http://localhost:8000/chatRoom/all/folder/0',
        {fstatus:folderForm.value.fstatus, fname:folderForm.value.fname,});
        if (response.status === 200) {
          alert('创建收藏夹成功');
          await fetchFolder();
        }
      } catch (err) {
        console.error('请求失败', err);
      }
    }

    const editFolder = async () => {
      try {
        const response = await instance.put('http://localhost:8000/chatRoom/all/folder/0',
        {fstatus:folderForm.value.fstatus, fname:folderForm.value.fname,fno:folderForm.value.fno,});
        if (response.status === 200) {
          alert('修改收藏夹成功');
          await fetchFolder();
        }
      } catch (err) {
        console.error('请求失败', err);
      }
    }

    const deleteFolder = async () => {
      try{
        const response = await instance.delete('http://localhost:8000/chatRoom/all/folder/0',{
          data:{
            fname:delFname.value,
          }
        });
        if (response.status === 200) {
          alert('删除收藏夹成功');
          await fetchFolder();
        }
      }catch(err){
        console.error('删除失败',err);
      }
    }

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

    const goToDiscussion = (discussion) => {
      router.push(`/course/${discussion.cno}/discussion/${discussion.dno}`)
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

    const fetchFolder = async () => {
      try{
        const response = await instance.get('http://localhost:8000/chatRoom/all/folder/0');
        if(response.status === 200){
          folders.value = response.data.data.personal_folders;
          otherFolders.value = response.data.data.others_folders;
        }
      }catch(err){
        console.error(err);
      }
    };

    const onSubmit = async () => {

      if (userType.value === 'teacher') {
        try{
          const response = await instance.put('http://localhost:8000/home/modifyInfo',
            {mail:form.value.mail,
                  office:form.value.office,
                  phone:form.value.phone,
                  intro:form.value.intro,});
          if(response.status === 200){
            alert('修改成功');
          }
        }catch(err){
          console.error(err);
        }

      } else if (userType.value === 'student') {
        try {
          const response = await instance.put('http://localhost:8000/home/modifyInfo',
              {mail: form.value.mail});
          if (response.status === 200) {
            alert('修改成功');
          }
        } catch (err) {
          console.log(err);
        }
      }
    };

    const getFavor = async (fno) => {
      const API_URL = `http://localhost:8000/chatRoom/folder/${fno}`;
      try{
        const response = await instance.get(API_URL);
        if(response.status === 200 ){
          if(folders.value.filter(item => item.fno === fno)){
            folderDiscussions.value = response.data.data.favorites;
          }else if(otherFolders.value.filter(item => item.fno === fno)){
            otherDiscussions.value = response.data.data.favorites;
          }
        }
      }catch(err){
        console.error(err);
      }
    }

    const delFavorDialog = (discussion) => {
      delDiscussion.value = discussion;
      delFavorDialogVisible.value = true;
    }

    const delFavor = async() => {
      const API_URL = `http://localhost:8000/chatRoom/folder/${delDiscussion.value.fno}`;
      try{
        const response = await instance.delete(API_URL,{
          data:{
            dno:delDiscussion.value.dno
          }  
          }
        )
        if(response.status === 200){
          alert('取消收藏成功');
          getFavor(delDiscussion.value.fno)
        }
      }catch(err){
        console.error(err);
      }
    }

    const fetchFollower = async() => {
      const API_URL = 'http://localhost:8000/chatRoom/getfollower'
      try{
        const response = await instance.get(API_URL);
        if(response.status === 200){
          follows.value = response.data.data;
        }
      }catch(err){
        console.error(err);
      }
    }

    const fetchFans = async() => {
      const API_URL = 'http://localhost:8000/chatRoom/getfan'
      try{
        const response = await instance.get(API_URL);
        if(response.status === 200){
          fans.value = response.data.data;
        }
      }catch(err){
        console.error(err);
      }
    }

    const delFan = async(fanUsername) => {
      const API_URL = 'http://localhost:8000/chatRoom/getfan'
      try{
        const response = await instance.delete(API_URL,{
          data:{
            fan:fanUsername
          }
        });
        if(response.status === 200){
          alert('移除粉丝成功');
          fetchFans();
        }
      }catch(err){
        console.error(err);
      }
    }

    const delFollow = async(folloUsername) => {
      const API_URL = 'http://localhost:8000/chatRoom/getfollower';
      try{
        const response = await instance.delete(API_URL,{
          data:{
            follower:folloUsername
          }
        });
        if(response.status === 200){
          alert('移除关注成功');
          fetchFollower();
        }
      }catch(err){
        console.error(err);
      }
    }

    const delFavoredFolder = async(fno) => {
      const API_URL = `http://localhost:8000/chatRoom/collectOtherFolder`;
      try{
        const response = await instance.delete(API_URL,{
          data:{
            fno:fno
          }
        });
        if(response.status === 200){
          alert('取消收藏成功');
          fetchFolder();
        }
      }catch(err){
        console.log(err);
      }
    }


    onMounted(async () => {
      await fetchUsername();
      await fetchInfo();
      await fetchAtmessage();
      await fetchFolder();
      await fetchFollower();
      await fetchFans();
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
      folderDiscussions,
      otherFolders,
      folderDialogVisible,
      deleteFolderDialogVisible,
      folderForm,
      folderDialogTitle,
      delFname,
      delFavorDialogVisible,
      delDiscussion,
      otherDiscussions,

      logout,
      goHome,
      goToUser,
      goToDiscussion,
      handleSelect,
      clearFolderDialog,
      editFolderDialog,
      createFolderDialog,
      handleFolderSubmit,
      deleteFolderDialog,
      deleteFolder,
      onSubmit,
      getFavor,
      delFavorDialog,
      delFavor,
      delFan,
      delFollow,
      delFavoredFolder,
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

  .folder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.message-unread {
  color: red;
}

.message-read {
  color: green;
}

.unread {
  font-weight: bold;
}

.fan-item {
  display: flex;           
  align-items: center;     
  gap: 10px;               
}

.delFan-btn {
  margin-right: 10px;      
}

.follow-item{
  display: flex;           
  align-items: center;     
  gap: 10px; 
}

.delFollow-btn{
  margin-right: 10px;     
}
  </style>