<template>
  <div class="course-page">
    <CourseHeader :courseData="courseData" />
    <div class="course-content">
      <CourseSidebar 
        :selectedTab="selectedTab" 
        @select-tab="handleSelect"
      />
      <CourseContent 
        :selectedTab="selectedTab"
        :courseData="courseData"
        :userType="userType"
        :courseNo="courseNo"
        :messages="messages"
        :students="students"
        @show-edit-dialog="showEditDialog"
        @show-upload-dialog="showUploadDialog"
        @show-new-folder-dialog="newFolderDialogVisible = true"
        @delete-message="deleteMessage"
        @send-message="sendMessage"
      />
    </div>
    <el-dialog
      title="上传文件"
      v-model="uploadDialogVisible"
      width="30%"
    >
      <el-form :model="uploadForm">
        <el-form-item label="选择文件">
          <el-upload
            class="upload-demo"
            action="#"
            :on-change="handleFileChange"
            :auto-upload="false"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传pdf文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleUpload(selectedTab)">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      title="编辑课程介绍"
      v-model="editDialogVisible"
      width="50%"
    >
      <el-form :model="editForm">
        <el-form-item label="课程介绍">
          <el-input
            type="textarea"
            v-model="editForm.cintro"
            :rows="10"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">提交</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      title="新建文件夹"
      v-model="newFolderDialogVisible"
      width="30%"
    >
      <el-input v-model="newFolderName" placeholder="请输入文件夹名称" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="newFolderDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createNewFolder">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import CourseHeader from '@/components/CourseHeader.vue';
import CourseSidebar from '@/components/CourseSidebar.vue';
import CourseContent from '@/components/CourseContent.vue';
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';

// optional styles
import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'

const USERNAME_URL = 'http://localhost:8000/homepage/getusername/';
const API_URL = 'http://localhost:8000/homepage/';

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
  components:{
    CourseHeader,
    CourseSidebar,
    CourseContent,
  },

  setup() {
    const route = useRoute();
    const courseNo = route.params.courseNo;
    const courseData = ref(null);
    const selectedTab = ref('introduction');
    const username = ref('');
    const userType = ref('');
    const error = ref('');
    const uploadDialogVisible = ref(false);
    const uploadForm = ref({ file: null });
    const editDialogVisible = ref(false);
    const editForm = ref({ cintro: '' });
    const messages = ref([]);
    const students = ref([]);
    const newFolderDialogVisible = ref(false);
    const newFolderName = ref('');

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

    const showUploadDialog = () => {
      uploadDialogVisible.value = true;
    };

    const handleFileChange = (file) => {
      uploadForm.value.file = file.raw;
    };

    const handleUpload = async (selectedTab) => {
      if (!uploadForm.value.file) {
        ElMessage.error('请选择文件');
        return;
      }
      const formData = new FormData();
      formData.append('file', uploadForm.value.file);

      try {
        let file_type
        if(selectedTab == 'outline'){
          file_type = 'outline';
        }else{
          file_type = 'calender'
        }
        const response = await instance.post(`${API_URL}course/${courseNo}/upload_file/${file_type}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.status === 200) {
          ElMessage.success('文件上传成功');
          uploadDialogVisible.value = false;
          await fetchCourseData();
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        ElMessage.error('文件上传失败');
      }
    };

    const showEditDialog = () => {
      editForm.value.cintro = courseData.value?.data?.cintro || '';
      editDialogVisible.value = true;
    };

    const handleEditSubmit = async () => {
      try {
        const response = await instance.put(`${API_URL}course/${courseNo}/update_intro`, {
          cintro: editForm.value.cintro
        });

        if (response.status === 200) {
          ElMessage.success('课程介绍更新成功');
          editDialogVisible.value = false;
          await fetchCourseData();
        }
      } catch (error) {
        console.error('Error updating course intro:', error);
        ElMessage.error('更新课程介绍失败');
      }
    };

    const createNewFolder = () => {
      if (newFolderName.value) {
        // Implement folder creation logic here
        newFolderDialogVisible.value = false;
        newFolderName.value = '';
      }
    };

    const fetchMessages = async () => {
      try {
        const response = await instance.get(`${API_URL}course/${courseNo}/message`);
        messages.value = response.data.data;
      } catch (error) {
        console.error('Error fetching messages:', error);
        ElMessage.error('获取通知失败');
      }
    };

    const deleteMessage = async (mno) => {
      try {
        await instance.delete(`${API_URL}course/${courseNo}/message`, { data: { mno } });
        await fetchMessages();
        ElMessage.success('通知删除成功');
      } catch (error) {
        console.error('Error deleting message:', error);
        ElMessage.error('删除通知失败');
      }
    };

    const sendMessage = async ({ title, info }) => {
      try {
        await instance.post(`${API_URL}course/${courseNo}/message`, { title, info });
        await fetchMessages();
        ElMessage.success('通知发送成功');
      } catch (error) {
        console.error('Error sending message:', error);
        ElMessage.error('发送通知失败');
      }
    };

    const fetchAllStudent = async () => {
      try {
        const response = await instance.get(`${API_URL}course/${courseNo}/student`);
        if (response.data.code === 200) {
          students.value = response.data.data;
        } else {
          ElMessage.error('获取所有选课学生失败');
        }
      } catch (err) {
        console.error('Error fetching students:', err);
        ElMessage.error('获取学生信息时发生错误');
      }
    };

    

    onMounted(() => {
      fetchUsername();
      fetchCourseData();
      fetchMessages();
      fetchAllStudent();
    });

    watch(() => selectedTab.value, (newTab) => {
      if (newTab === 'notice') {
        fetchMessages();
      } else if (newTab === 'student') {
        fetchAllStudent();
      }
    });

    return {
      courseData,
      selectedTab,
      handleSelect,
      username,
      userType,
      error,
      uploadDialogVisible,
      uploadForm,
      showUploadDialog,
      handleFileChange,
      handleUpload,
      editDialogVisible,
      editForm,
      showEditDialog,
      handleEditSubmit,
      messages,
      students,
      newFolderDialogVisible,
      newFolderName,
      createNewFolder,
      deleteMessage,
      sendMessage,
      courseNo,
    };
  },
};
</script>

  
<style scoped>
.course-page {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #333;
  background-color: #f5f7fa;
}

.course-content {
  display: flex;
  min-height: calc(100vh - 80px);
} 

.main-content {
  flex-grow: 1;
  padding: 30px;
  background-color: #fff;
  margin: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0,0,0,0.05);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #4a69bd;
  padding-bottom: 10px;
}

.content-header h2 {
  font-size: 24px;
  color: #4a69bd;
}

.content-actions {
  display: flex;
  gap: 10px;
}
</style>