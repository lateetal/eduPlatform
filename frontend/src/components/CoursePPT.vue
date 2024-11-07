<template>
    <div class="ppts-manager">
      <!-- 左侧树形结构 -->
      <div class="folder-tree">
        <div class="tree-header">
          <h3>电子课件</h3>
        </div>
        <div class="tree-content">
          <div v-for="semester in semesters" :key="semester.id" class="tree-item">
            <div class="folder-item" @click="semester.expanded = !semester.expanded">
              <el-icon><FolderOpened v-if="semester.expanded" /><Folder v-else /></el-icon>
              {{ semester.name }}
            </div>
            <div v-if="semester.expanded" class="sub-items">
              <div v-for="file in semester.files" :key="file.id" class="file-item" 
                   :class="{ active: selectedFile === file }"
                   @click="selectFile(file)">
                <el-icon><Document /></el-icon>
                {{ file.name }}
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 右侧内容区 -->
      <div class="content-area">
        <div class="action-buttons">
          <el-button type="primary" @click="showUploadDialog">上传文件</el-button>
          <el-button @click="showReferenceDialog">引用文件</el-button>
          <el-button @click="showNewFolderDialog">新建目录</el-button>
          <el-button @click="moveSelected">移动</el-button>
          <el-button @click="deleteSelected">删除</el-button>
          <el-button type="success" @click="publishSelected">发布</el-button>
          <el-button type="warning" @click="unpublishSelected">取消发布</el-button>
        </div>
  
        <div class="file-table">
          <table>
            <thead>
              <tr>
                <th><el-checkbox v-model="selectAll" @change="handleSelectAll" /></th>
                <th>目录名称</th>
                <th>属性</th>
                <th>操作</th>
                <th>发布状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentFiles" :key="item.id">
                <td><el-checkbox v-model="item.selected" /></td>
                <td>{{ item.name }}</td>
                <td>
                  <el-icon><Folder v-if="item.type === 'folder'" /><Document v-else /></el-icon>
                </td>
                <td>
                  <el-button-group>
                    <el-button size="small" @click="editItem(item)">编辑</el-button>
                    <el-button size="small" @click="downloadItem(item)">下载</el-button>
                    <el-button size="small" @click="deleteItem(item)">删除</el-button>
                  </el-button-group>
                </td>
                <td>
                  <el-switch
                    v-model="item.published"
                    @change="(val) => togglePublish(item, val)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
  
      <!-- 上传文件对话框 -->
      <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
        <el-upload
          class="upload-demo"
          drag
          action="/api/upload"
          multiple
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
        </el-upload>
      </el-dialog>
  
      <!-- 新建目录对话框 -->
      <el-dialog v-model="newFolderDialogVisible" title="新建目录" width="500px">
        <el-form :model="newFolderForm">
          <el-form-item label="目录名称">
            <el-input v-model="newFolderForm.name" />
          </el-form-item>
        </el-form>
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
  import { ref } from 'vue'
  import { Document, Folder, FolderOpened, UploadFilled } from '@element-plus/icons-vue'
  
  export default {
    name: 'CoursePPTs',
    components: {
      Document,
      Folder,
      FolderOpened,
      UploadFilled
    },
    props: {
      courseNo: {
        type: String,
        required: true
      }
    },
    setup() {
      const semesters = ref([
        {
          id: 1,
          name: '2023-2024第一学期',
          expanded: true,
          files: [
            { id: 1, name: '第1章 绪论', type: 'folder' },
            { id: 2, name: 'PPT模板', type: 'file' }
          ]
        },
        {
          id: 2,
          name: '2023-2023第二学期',
          expanded: false,
          files: []
        }
      ])
  
      const currentFiles = ref([
        { id: 1, name: '第1章 绪论', type: 'folder', selected: false, published: true },
        { id: 2, name: 'PPT模板', type: 'file', selected: false, published: false }
      ])
  
      const selectedFile = ref(null)
      const selectAll = ref(false)
      const uploadDialogVisible = ref(false)
      const newFolderDialogVisible = ref(false)
      const newFolderForm = ref({
        name: ''
      })
  
      const handleSelectAll = (val) => {
        currentFiles.value.forEach(file => file.selected = val)
      }
  
      const selectFile = (file) => {
        selectedFile.value = file
      }
  
      const showUploadDialog = () => {
        uploadDialogVisible.value = true
      }
  
      const showNewFolderDialog = () => {
        newFolderDialogVisible.value = true
      }
  
      const createNewFolder = () => {
        if (newFolderForm.value.name) {
          currentFiles.value.push({
            id: Date.now(),
            name: newFolderForm.value.name,
            type: 'folder',
            selected: false,
            published: false
          })
          newFolderDialogVisible.value = false
          newFolderForm.value.name = ''
        }
      }
  
      const handleUploadSuccess = () => {
        // Handle successful upload
        uploadDialogVisible.value = false
      }
  
      const handleUploadError = (error) => {
        // Handle upload error
        console.error('Upload failed:', error)
      }
  
      const moveSelected = () => {
        // Implement move functionality
      }
  
      const deleteSelected = () => {
        currentFiles.value = currentFiles.value.filter(file => !file.selected)
        selectAll.value = false
      }
  
      const publishSelected = () => {
        currentFiles.value.forEach(file => {
          if (file.selected) {
            file.published = true
          }
        })
      }
  
      const unpublishSelected = () => {
        currentFiles.value.forEach(file => {
          if (file.selected) {
            file.published = false
          }
        })
      }
  
      const editItem = (item) => {
        // Implement edit functionality
        console.log('edit',item)
      }
  
      const downloadItem = (item) => {
        // Implement download functionality
        console.log('delete',item)
      }
  
      const deleteItem = (item) => {
        currentFiles.value = currentFiles.value.filter(file => file.id !== item.id)
      }
  
      const togglePublish = (item, val) => {
        item.published = val
      }
  
      return {
        semesters,
        currentFiles,
        selectedFile,
        selectAll,
        uploadDialogVisible,
        newFolderDialogVisible,
        newFolderForm,
        handleSelectAll,
        selectFile,
        showUploadDialog,
        showNewFolderDialog,
        createNewFolder,
        handleUploadSuccess,
        handleUploadError,
        moveSelected,
        deleteSelected,
        publishSelected,
        unpublishSelected,
        editItem,
        downloadItem,
        deleteItem,
        togglePublish
      }
    }
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