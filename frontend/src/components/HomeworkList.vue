<template>
    <div class="homework-container">
      <div class="header">
        <el-button v-if="userType==='teacher'" type="primary" @click="dialogVisible = true">布置作业</el-button>
      </div>
  
      <div class="table-container">
        <el-table :data="homeworks" style="width: 100%">
          <el-table-column type="selection" width="55" />
          <el-table-column prop="title" label="作业标题" />
          <el-table-column prop="start_date" label="发布时间" width="180" />
          <el-table-column prop="due_date" label="截止时间" width="180" />
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button type="primary" link @click="$emit('view-homework', scope.row)">
                查看详情
              </el-button>
              <el-button type="primary" link @click="$emit('edit-homework', scope.row)">
                编辑
              </el-button>
              <el-button type="danger" link @click="$emit('delete-homework', scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
  
      <!-- 布置作业对话框 -->
      <el-dialog
        v-model="dialogVisible"
        title="布置作业"
        width="50%"
        :before-close="handleClose"
      >
        <el-form :model="homeworkForm" label-width="120px">
          <el-form-item label="作业标题">
            <el-input v-model="homeworkForm.title" placeholder="请输入作业标题" />
          </el-form-item>
          <el-form-item label="作业描述">
            <el-input
              v-model="homeworkForm.description"
              type="textarea"
              rows="4"
              placeholder="请输入作业描述"
            />
          </el-form-item>
          <el-form-item label="截止日期">
            <el-date-picker
              v-model="homeworkForm.deadline"
              type="datetime"
              placeholder="选择截止日期"
            />
          </el-form-item>
          <el-form-item label="班次">
            <el-select v-model="homeworkForm.class" placeholder="请选择班次">
              <el-option label="G27" value="G27" />
              <el-option label="G28" value="G28" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSubmit">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  
  const props = defineProps({
    homeworks: {
      type: Array,
      required: true
    },
    courseNo: {
      type: String,
      required: true
    },
    userType: {
      type: String,
      required: true,
    }
  })
  
  const emit = defineEmits(['add-homework', 'view-homework', 'edit-homework', 'delete-homework'])
  
  const dialogVisible = ref(false)
  const homeworkForm = reactive({
    title: '',
    description: '',
    deadline: '',
    class: ''
  })
  
  const handleClose = () => {
    dialogVisible.value = false
  }
  
  const handleSubmit = () => {
    emit('add-homework', { ...homeworkForm, courseNo: props.courseNo })
    dialogVisible.value = false
    // Reset form
    Object.keys(homeworkForm).forEach(key => homeworkForm[key] = '')
  }
  
  </script>
  
  <style scoped>
  .homework-container {
    padding: 20px;
    background-color: #fff;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .table-container {
    border: 1px solid #ebeef5;
    border-radius: 4px;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px 40px;
  }
  </style>