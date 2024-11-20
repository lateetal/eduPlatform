<template>
    <div class="ppts-manager">
      <!-- 左侧树形结构 -->
      <div class="folder-tree">
        <div class="tree-header">
          <h3>电子课件</h3>
        </div>
        <div class="tree-content">
          <div class="tree-root" @click="selectFile(resources)">
            <el-icon>
              <FolderOpened v-if="selectedFolder.id === resources.id" />
              <Folder v-else />
            </el-icon>
            电子课件
          </div>

          <div v-for="folder in resources.subfolders" :key="folder.id" class="tree-item">
            <FolderTree 
              :folder="folder" 
              :selectedFolder="selectedFolder" 
              @selectFile="selectFile"
            />
          </div>
        </div>
      </div>
  
      <!-- 右侧内容区 -->
      <div class="content-area">
        <div class="action-buttons">
          <el-button type="primary" @click="uploadDialogVisible = true">上传文件</el-button>
          <el-button type="success" @click="newFolderDialogVisible = true">新建目录</el-button>
          <el-button type="info" @click="deleteFolderDialogVisible = true">删除文件夹</el-button>
        </div>
  
        <div class="file-table">
          <table>
            <thead>
              <tr>
                <th>名称</th>
                <th>属性</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentFiles" :key="item.rno">
                <td>{{ item.rname }}</td>
                <td>
                  <el-icon><Document /></el-icon>
                </td>
                <td>
                  <el-button-group>
                    <el-button size="small" @click="downloadItem(item)">下载</el-button>
                    <el-button size="small" @click="deleteFile(item)">删除</el-button>
                  </el-button-group>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  
      <!-- 上传文件对话框 -->
      <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
        <span>上传至文件夹</span>
        <el-input 
          v-model="selectedFolder.folder_name"
          style="width:200px"
          disabled
        />
        <p>上传文件</p>
        <el-upload
          class="upload-demo"
          action="#"
          :on-change="handleFileChange"
          :auto-upload="false"
        >
          <el-button type="primary">上传附件</el-button>
        </el-upload>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="uploadDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="uploadFile">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>
  
      <!-- 新建目录对话框 -->
      <el-dialog v-model="newFolderDialogVisible" title="新建目录" width="500px">
        <el-form :model="newFolderForm">
          <el-form-item label="当前文件夹">
            <el-input 
              v-model="selectedFolder.folder_name"
              style="width:200px"
              disabled
            />
          </el-form-item>
          <el-form-item label="目录名称">
            <el-input v-model="newFolderForm.name" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="newFolderForm.name = '';newFolderDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="createFolder">确定</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog v-model="deleteFolderDialogVisible" title="删除文件夹" width="500px">
        <span>文件夹名</span>
        <el-input 
          v-model="selectedFolder.folder_name"
          style="width:200px"
          disabled
        />
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="deleteFolderDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="deleteFolder">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
<script setup>
import { ref } from 'vue'
import { Document, Folder, FolderOpened } from '@element-plus/icons-vue'
import { pptListService,
        fileUploadService,
        fileDeleteService,
        subfolderAddService,
        subfolderDeleteService} from '@/api/homepage.js'
import { ElMessage } from 'element-plus';
import FolderTree from './FolderTree.vue';

const props = defineProps({
  courseNo: {
    type: String,
    required: true
  },
  userType:{
    type: String,
    required: true
  },
});

const resources = ref([]);
const currentFiles = ref([]);
const selectedFolder = ref({});
const uploadDialogVisible = ref(false);
const uploadForm = ref({ file: null });
const newFolderDialogVisible = ref(false)
const newFolderForm = ref({
  name: ''
});
const deleteFolderDialogVisible = ref(false);

const fetchResources = async () => {
  try{
    let result = await pptListService(props.courseNo);
    if(result.status === 200){
      resources.value = result.data;
      selectFile(resources);
    } else {
      ElMessage.error(result.data.error || '获取电子课件失败');
    }
  } catch(err){
    ElMessage.error('获取电子课件失败，未定义错误');
    console.log(err);
  }
}

fetchResources();

const selectFile = (file) => {
  selectedFolder.value = file;
  currentFiles.value = selectedFolder.value.resources;
};

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw;
};

const uploadFile = async () => {
  if(uploadForm.value.file){
    const formData = new FormData()
    formData.append('folderPath',selectedFolder.value.id)
    formData.append('rname', uploadForm.value.file.name)
    formData.append('resourceFile',uploadForm.value.file)
    try{
      let result = await fileUploadService(props.courseNo,formData);
      if(result.status === 201){
        ElMessage.success('上传文件成功');
        fetchResources();
        uploadDialogVisible.value = false;
      } else {
        ElMessage.error(result.data.error || '上传文件失败')
      }
    } catch(err){
      ElMessage.error('上传文件失败，未定义错误');
      console.log(err);
    }
  } else {
    ElMessage.error('未选择文件');
  }
  
}

const deleteFile = async (file) => {
  try{
    let result = await fileDeleteService(props.courseNo,file.rno);
    if(result.status === 200){
      ElMessage.success('删除文件成功');
      fetchResources();
    } else {
      ElMessage.error(result.data.error || '删除文件失败');
    }
  } catch (err) {
    ElMessage.error('上传文件失败，未定义错误');
    console.log(err);
  }
}


const createFolder = async () => {
  if (newFolderForm.value.name) {
    const formData = new FormData()
    formData.append('folderPath',selectedFolder.value.folderPathInSql + selectedFolder.value.id + '/')
    formData.append('folderName',newFolderForm.value.name);
    try {
      let result = await subfolderAddService(props.courseNo,formData);
      if(result.status === 200){
        ElMessage.success('新建文件夹成功');
        fetchResources();
        newFolderDialogVisible.value = false;
      } else {
        ElMessage.error(result.data.error || '新建文件夹失败')
      }
    } catch (err) {
      ElMessage.error('新建文件夹失败，未定义错误');
      console.log(err);
    }
  }
}

const deleteFolder = async () => {
  try{
    let result = await subfolderDeleteService(props.courseNo,selectedFolder.value.id);
    if(result.status === 200){
      ElMessage.success('删除文件夹成功');
      fetchResources();
      deleteFolderDialogVisible.value = false;
    } else {
      ElMessage.error(result.data.error || '删除文件夹失败');
    }
  } catch (err) {
    ElMessage.error('删除文件夹失败，未定义错误');
    console.log(err);
  }
}

const downloadItem = (item) => {
  const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/';
  const downloadUrl = BUCKET_URL + item.rfileInOSS;
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = item.rfileInOSS.split('/').pop(); 
  link.click();
}

  </script>
  
  <style scoped>
  .ppts-manager {
    display: flex;
    height: 100%;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  }
  
  .folder-tree {
    width: 250px;
    border-right: 1px solid #e0e0e0;
    background-color: #f8f9fa;
  }
  
  .tree-header {
    padding: 16px;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .tree-header h3 {
    margin: 0;
    color: #333;
  }
  
  .tree-content {
    padding: 16px;
  }

  .tree-root {
    cursor: pointer;
    border-radius: 4px;
  }

  .tree-root:hover {
    background-color: #e9ecef;
  }
  
  .tree-item {
    margin-bottom: 8px;
  }
  
  .folder-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .folder-item:hover {
    background-color: #e9ecef;
  }
  
  .sub-items {
    margin-left: 24px;
  }
  
  .file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .file-item:hover {
    background-color: #e9ecef;
  }
  
  .file-item.active {
    background-color: #e3f2fd;
  }
  
  .content-area {
    flex-grow: 1;
    padding: 20px;
  }
  
  .action-buttons {
    margin-bottom: 20px;
    display: flex;
    gap: 8px;
  }
  
  .file-table {
    width: 100%;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e0e0e0;
  }
  
  th {
    background-color: #f8f9fa;
    font-weight: 600;
  }
  
  tr:hover {
    background-color: #f8f9fa;
  }
  
  .upload-demo {
    width: 100%;
  }
  
  .el-upload__text {
    margin-top: 8px;
    color: #606266;
  }
  
  .el-upload__text em {
    color: #409EFF;
    font-style: normal;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 20px;
  }
  </style>