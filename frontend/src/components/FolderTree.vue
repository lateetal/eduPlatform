<template>
    <div class="tree-item">
      <div class="folder-item" @click="selectFile(folder)">
        <el-icon>
          <FolderOpened v-if="selectedFolder.id === folder.id" />
          <Folder v-else />
        </el-icon>
        {{ folder.folder_name }}
      </div>
  
      <!-- 如果文件夹有子文件夹，则递归渲染 -->
      <div v-if="folder.subfolders && folder.subfolders.length > 0" class="sub-items">
        <FolderTree
          v-for="subfolder in folder.subfolders"
          :key="subfolder.id"
          :folder="subfolder"
          :selectedFolder="selectedFolder"
          @selectFile="selectFile"
        />
      </div>
    </div>
  </template>
  
  <script>
  import { Folder, FolderOpened } from '@element-plus/icons-vue'; // 导入ElementPlus的图标
  export default {
    name: 'FolderTree',
    components: {
      Folder,
      FolderOpened
    },
    props: {
      folder: {
        type: Object,
        required: true
      },
      selectedFolder: {
        type: Object,
        required: true
      }
    },
    methods: {
      selectFile(folder) {
        this.$emit('selectFile', folder); // 向父组件传递选择的文件夹
      }
    }
  };
  </script>
  
  <style scoped>
  .tree-item {
    margin-left: 20px;
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
    margin-left: 20px; 
  }
  </style>
  