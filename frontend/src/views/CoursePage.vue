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
            <el-menu-item index="4-1" @click="goDiscussion">讨论区</el-menu-item>
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
        <div class="content-header">
          <h2>{{ getContentTitle() }}</h2>
          <div class="content-actions">
            <el-button 
              type="primary"
              v-if="selectedTab === 'introduction' && userType === 'teacher'"
              @click="showEditDialog"
            >编辑
            </el-button>
            <el-button 
              type="primary" 
              @click="showUploadDialog"
              v-if="(selectedTab === 'outline' || selectedTab === 'calendar') && userType === 'teacher'"
            >上传
            </el-button>
            <el-button 
              type="success" 
              @click="handleDownload"
              v-if="selectedTab === 'outline' || selectedTab === 'calendar'"
              >下载
            </el-button>
          </div>
        </div>
        
        <div v-if="selectedTab === 'introduction'" class="course-intro">
          <p>{{ courseData?.data?.cintro || 'cintro' }}</p>
        </div>
        <div v-if="selectedTab === 'outline'" class="course-outline">
          <div v-if="courseData?.data?.coutline" class="pdf-container">
            <VuePdfEmbed annotation-layer text-layer :source="BUCKET_URL + courseData.data.coutline" />
          </div>
          <p v-else>No PDF available</p>
        </div>
        <div v-if="selectedTab === 'calendar'" class="course-calendar">
          <div v-if="courseData?.data?.calendar" class="pdf-container">
            <VuePdfEmbed annotation-layer text-layer :source="BUCKET_URL + courseData.data.calendar" />
          </div>
          <p v-else>No PDF available</p>
        </div>
        <div v-if="selectedTab === 'professor'" class="course-professor">
          <p>教师姓名：{{ courseData?.data?.teacher?.tname || 'tname'}}</p>
          <p>邮箱：{{ courseData?.data?.teacher?.tmail || 'tmail'}}</p>
          <p>办公室：{{ courseData?.data?.teacher?.toffice || 'toffice'}}</p>
          <p>电话：{{ courseData?.data?.teacher?.tphone || 'tphone'}}</p>
          <p>介绍：{{ courseData?.data?.teacher?.tintro || 'tintro'}}</p>
        </div>

        <div v-if="selectedTab === 'ppts'" class="course-ppts">
          <div class="content-actions">
            <el-upload
              class="upload-demo"
              action="/api/upload-material"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
            >
              <el-button type="primary">上传课件</el-button>
            </el-upload>
          </div>
          <el-tree
            :data="materialsTree"
            :props="defaultProps"
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>{{ node.label }}</span>
                <span v-if="!node.isLeaf">
                  <el-button
                    type="text"
                    size="small"
                    @click.stop="() => handleAddFolder(data)"
                  >
                    添加文件夹
                  </el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
        <div v-if="selectedTab === 'papers'" class="course-papers">
        </div>
        <div v-if="selectedTab === 'exercises'" class="course-exercises">
          
        </div>

        <div v-if="selectedTab === 'homework'" class="course-homework">
          
        </div>

        <div v-if="selectedTab === 'AIhelper'" class="course-AIhelper">
          
        </div>

        <div v-if="selectedTab === 'notice'" class="course-notice">
          
        </div>
      </main>
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
          <el-button type="primary" @click="handleUpload">确定</el-button>
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
      v-model="previewDialogVisible"
      title="课件预览"
      width="80%"
    >
      <div v-if="selectedMaterial">
        <VuePdfEmbed v-if="selectedMaterial.type === 'pdf'" :source="selectedMaterial.url" />
        <img v-else-if="selectedMaterial.type === 'image'" :src="selectedMaterial.url" style="max-width: 100%;" />
        <div v-else>
          无法预览此类型的文件。 <a :href="selectedMaterial.url" target="_blank">下载文件</a>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

  <script>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { Location, Folder, ChatDotRound, DataBoard, Bell } from '@element-plus/icons-vue';
  import VuePdfEmbed from 'vue-pdf-embed'

  // optional styles
  import 'vue-pdf-embed/dist/styles/annotationLayer.css'
  import 'vue-pdf-embed/dist/styles/textLayer.css'

  const USERNAME_URL = 'http://localhost:8000/homepage/getusername/'
  const API_URL = 'http://localhost:8000/homepage/';
  const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';

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
    components:{
      Location,
      Folder,
      ChatDotRound,
      DataBoard,
      Bell,
      VuePdfEmbed,
    },

    setup() {
      const route = useRoute();
      const router = useRouter();
      const courseNo = route.params.courseNo;
      const courseData = ref(null);
      const selectedTab = ref('introduction');
      const username = ref('');
      const userType = ref('');
      const error = ref('');

      const uploadDialogVisible = ref(false);
      const uploadForm = ref({
        file: null
      });

      const editDialogVisible = ref(false);
      const editForm = ref({
        cintro: ''
      });

      const materialsTree = ref([]);
      const defaultProps = {
        children: 'children',
        label: 'name',
      };
      const previewDialogVisible = ref(false);
      const selectedMaterial = ref(null);

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

      const fetchMaterials = async () => {
      try {
        const response = await axios.get('/api/course-materials');
        materialsTree.value = response.data;
      } catch (error) {
        console.error('Error fetching materials:', error);
        ElMessage.error('获取课件失败');
      }
    };

    const handleUploadSuccess = () => {
      ElMessage.success('上传成功');
      fetchMaterials(); // Refresh the materials list
    };

    const handleUploadError = () => {
      ElMessage.error('上传失败');
    };

    const handleNodeClick = (data) => {
      if (data.type === 'folder') return;
      selectedMaterial.value = data;
      previewDialogVisible.value = true;
    };

    const handleAddFolder = async (data) => {
      const folderName = await ElMessageBox.prompt('请输入文件夹名称', '新建文件夹');
      if (folderName.value) {
        try {
          await axios.post('/api/add-folder', { parentId: data.id, name: folderName.value });
          ElMessage.success('文件夹创建成功');
          fetchMaterials(); // Refresh the materials list
        } catch (error) {
          console.error('Error creating folder:', error);
          ElMessage.error('创建文件夹失败');
        }
      }
    };

      const handleSelect = (key) => {
        selectedTab.value = key;
      };

      const goDiscussion = () => {
        router.push(`/course/${courseNo}/discussion/`);
      };

      const showUploadDialog = () => {
        uploadDialogVisible.value = true;
      };

      const handleFileChange = (file) => {
        uploadForm.value.file = file.raw;
      };

      const handleUpload = async () => {
        if (!uploadForm.value.file) {
          ElMessage.error('请选择文件');
          return;
        }

        const formData = new FormData();
        formData.append('file', uploadForm.value.file);

        try {
          const response = await instance.post(`${API_URL}upload/`, formData, {
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

      const handleDownload = () => {
        console.log('Download button clicked');
      };

      const showEditDialog = () => {
        editForm.value.cintro = courseData.value?.data?.cintro || '';
        editDialogVisible.value = true;
      };

      const handleEditSubmit = async () => {
        try {
          const response = await instance.put(`${API_URL}course/${courseNo}/update_intro/`, {
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

      const getContentTitle = () => {
        switch (selectedTab.value) {
          case 'introduction': return '课程介绍';
          case 'outline': return '教学大纲';
          case 'calendar': return '教学日历';
          case 'professor': return '教师信息';
          case 'ppts': return '课件';
          case 'papers': return '历年试题库';
          case 'exercises': return '习题库';
          case 'homework': return '作业';
          case 'AIhelper': return 'AI问答';
          case 'notice': return '通知';
          default: return '';
        }
      };
  
      onMounted(() => {
        fetchUsername();
        fetchCourseData();
        fetchMaterials();
      });
  
      return {
        BUCKET_URL,
        courseData,
        selectedTab,
        handleSelect,
        goDiscussion,
        username,
        userType,
        error,
        uploadDialogVisible,
        uploadForm,
        showUploadDialog,
        handleFileChange,
        handleUpload,
        handleDownload,
        getContentTitle,
        editDialogVisible,
        editForm,
        showEditDialog,
        handleEditSubmit,
        materialsTree,
        defaultProps,
        previewDialogVisible,
        selectedMaterial,
        handleUploadSuccess,
        handleUploadError,
        handleNodeClick,
        handleAddFolder,
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

.course-content {
  display: flex;
  min-height: calc(100vh - 80px);
}

.sidebar {
  background-color: #f0f0f0;
  padding: 20px;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
  position: relative;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-actions {
  display: flex;
  gap: 10px;
}

.pdf-container {
  width: 100%;
  height: 900px;
  overflow-y: auto;
  border: 1px solid #ccc;
}

.pdf-container iframe {
  border: none;
}

.el-upload__tip {
  font-size: 12px;
  color: #606266;
  margin-top: 7px;
}

.course-ppts {
  margin-top: 20px;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
</style>