<template>
    <div class="homework-container">
      <div class="header">
        <el-button v-if="userType==='teacher'" type="primary" @click="dialogTitle='布置作业';dialogVisible = true">
          布置作业
        </el-button>
      </div>
  
      <div class="table-container">
        <el-table :data="homeworks" style="width: 100%">
          <el-table-column label="作业标题" width="200">
            <template #default="scope">
              <router-link :to="{name:'AssignmentDetail',params:{courseNo:props.courseNo,assignmentId:scope.row.id}}">{{ scope.row.title }}</router-link>
            </template>
          </el-table-column>
          <el-table-column label="提交人数" width="100">
            <template #default="scope">
              {{ scope.row.submitNum }} / {{ scope.row.studentNum }}
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始时间" width="180" />
          <el-table-column prop="due_date" label="截止时间" width="180" />
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button v-if="userType==='teacher'" type="primary" link @click="publicGrade(scope.row)">
                公布成绩
              </el-button>
              <el-button v-if="userType==='teacher'" type="primary" link @click="editDialog(scope.row)">
                编辑
              </el-button>
              <el-button v-if="userType==='teacher'" type="danger" link @click="delAssignment(scope.row.id)">
                删除
              </el-button>
              <el-button v-if="userType==='student'" type="primary" @click="commitDialog(scope.row)">
                提交
              </el-button>
              <el-button v-if="userType==='student'" type="info" @click="assignmentView(scope.row)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
  
      <!-- 布置作业对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
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

          <el-form-item label="开始日期">
            <el-date-picker
              v-model="homeworkForm.start_date"
              type="date"
              placeholder="选择开始日期"
              format="YYYY/MM/DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="截止日期">
            <el-date-picker
              v-model="homeworkForm.due_date"
              type="date"
              placeholder="选择截止日期"
              format="YYYY/MM/DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="学生互评">
            <el-switch v-model="homeworkForm.isMutualAssessment" />
          </el-form-item>

          <el-form-item label="允许逾期提交">
            <el-switch v-model="homeworkForm.allowDelaySubmission" />
          </el-form-item>

          <el-form-item label="满分">
            <el-input-number v-model="homeworkForm.maxGrade" :min="1" :max="100" />
          </el-form-item>

          <el-form-item label="选择文件">
            <el-upload
              class="upload-demo"
              action="#"
              :on-change="handleFileChange"
              :auto-upload="false"
            >
              <el-button type="primary">上传附件</el-button>
              <template #tip>
                <div class="el-upload__tip">只能上传pdf文件</div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="dialogTitle==='布置作业'?addAssignment():editAssignment()">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!--作业提交对话框-->
      <el-dialog
        v-model="commitDialogVisible"
        title="提交作业"
         width="50%"
      >
        <p>作业标题：{{commitAssignment.title}}</p>
        <el-form :model="commitForm" label-width="120px">
          <el-form-item label="作业描述">
            <el-input v-model="commitForm.submission_text" />
          </el-form-item>
          <el-form-item label="选择附件">
            <el-upload
              class="upload-demo"
              action="#"
              :on-change="handleFileChange"
              :auto-upload="false"
            >
              <el-button type="primary">上传附件</el-button>
              <template #tip>
                <div class="el-upload__tip">只能上传pdf文件</div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="commitDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="commitHomework">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { ElMessage } from 'element-plus';
  import { assignmentListService,
          assignmentAddService,
          assignmentDeleteService,
          assignmentUpdateService,
          assignmentCommitService } from '@/api/homepage';
  
  const props = defineProps({
    courseNo: {
      type: String,
      required: true
    },
    userType: {
      type: String,
      required: true,
    }
  })

  const dialogVisible = ref(false)
  const homeworks = ref([]);
  const homeworkForm = ref({
    title: '',
    description: '',
    start_date: '',
    due_date: '',
    assignment_file: '',
    isMutualAssessment: false,
    allowDelaySubmission: false,
    maxGrade: 100,
  });
  const uploadForm = ref({ file: null });
  const dialogTitle = ref('');
  const editId = ref(null);
  const commitDialogVisible = ref(false);
  const commitForm = ref({
    submission_text:'',
  })
  const commitAssignment = ref({});

  const fetchHomeworks = async () => {
    try{
      let result = await assignmentListService(props.courseNo);
      if(result.status === 200){
        homeworks.value = result.data.data;
      } else if(result.status === 404){
        homeworks.value = [];
      }
      
    } catch(err){
      console.log(err);
    }   
  }

  fetchHomeworks();

  const clearHomeworkForm = () => {
    homeworkForm.value = {
      title: '',
      description: '',
      start_date: '',
      due_date: '',
      assignment_file: '',
      isMutualAssessment: false,
      allowDelaySubmission: false,
      maxGrade: 100,
    };
  }
  
  const handleClose = () => {
    dialogVisible.value = false;
    clearHomeworkForm();
  }
  
  const addAssignment = async () => {
    try {
      if(homeworkForm.value.isMutualAssessment){
        homeworkForm.value.isMutualAssessment = 1;
      } else {
        homeworkForm.value.isMutualAssessment = 0;
      }

      if(homeworkForm.value.allowDelaySubmission){
        homeworkForm.value.allowDelaySubmission = 1;
      } else {
        homeworkForm.value.allowDelaySubmission = 0;
      }
      const formData = new FormData()
      formData.append('title', homeworkForm.value.title)
      formData.append('description', homeworkForm.value.description)
      formData.append('start_date', homeworkForm.value.start_date)
      formData.append('due_date', homeworkForm.value.due_date)
      formData.append('isMutualAssessment', homeworkForm.value.isMutualAssessment)
      formData.append('allowDelaySubmission', homeworkForm.value.allowDelaySubmission)
      formData.append('maxGrade', homeworkForm.value.maxGrade)
      formData.append('assignment_file', uploadForm.value.file);

      const result = await assignmentAddService(props.courseNo, formData)

      if (result.status === 201) {
        ElMessage.success('作业布置成功')
        dialogVisible.value = false
        clearHomeworkForm()
        fetchHomeworks()
      } else {
        ElMessage.error(result.data.error || '作业布置失败，请重试。')
      }
    } catch (error) {
      console.error('Error adding assignment:', error)
      ElMessage.error('发生错误，请稍后重试。')
    }
  }

  const handleFileChange = (file) => {
    uploadForm.value.file = file.raw;
  };

  const delAssignment = async (assignmentId) => {
    let result = await assignmentDeleteService(props.courseNo,assignmentId);
    if(result.status === 201){
      ElMessage.success('作业删除成功');
      fetchHomeworks();
    }
  }

  const editDialog = (assignment) => {
    editId.value = assignment.id;
    homeworkForm.value = assignment;
    dialogTitle.value = '编辑作业';
    dialogVisible.value = true;
  }

  const editAssignment = async () => {
    try {
      if(homeworkForm.value.isMutualAssessment){
        homeworkForm.value.isMutualAssessment = 1;
      } else {
        homeworkForm.value.isMutualAssessment = 0;
      }

      if(homeworkForm.value.allowDelaySubmission){
        homeworkForm.value.allowDelaySubmission = 1;
      } else {
        homeworkForm.value.allowDelaySubmission = 0;
      }
      const formData = new FormData()
      formData.append('assignment_id',editId.value)
      formData.append('title', homeworkForm.value.title)
      formData.append('description', homeworkForm.value.description)
      formData.append('start_date', homeworkForm.value.start_date)
      formData.append('due_date', homeworkForm.value.due_date)
      formData.append('isMutualAssessment', homeworkForm.value.isMutualAssessment)
      formData.append('allowDelaySubmission', homeworkForm.value.allowDelaySubmission)
      formData.append('maxGrade', homeworkForm.value.maxGrade)
      formData.append('assignment_file', uploadForm.value.file);

      const result = await assignmentUpdateService(props.courseNo, formData)

      if (result.status === 200) {
        ElMessage.success('作业修改成功')
        dialogVisible.value = false;
        clearHomeworkForm()
        fetchHomeworks()
      } else {
        ElMessage.error(result.data.error || '作业修改失败，请重试。')
      }
    } catch (error) {
      console.error('Error adding assignment:', error)
      ElMessage.error('发生错误，请稍后重试。')
    }
  }

  const commitDialog = (assignment) => {
    commitAssignment.value = assignment;
    commitForm.value.submission_text = '';
    uploadForm.value.file = '';
    commitDialogVisible.value = true;
  }

  const commitHomework= async () => {
    const formData = new FormData();
    formData.append('submission_text',commitForm.value.submission_text);
    formData.append('submission_file',uploadForm.value.file);
    try {
      let result = await assignmentCommitService(props.courseNo,commitAssignment.value.id,formData);
      if(result.status === 201){
        ElMessage.success('提交作业成功');
        fetchHomeworks();
      }
    } catch (err) {
      ElMessage.error('提交作业失败');
      console.log(err);
    }
    commitDialogVisible.value = false;
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