<template>
    <div class="homework-container" v-if="!showManagePage">
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
          <el-table-column v-if="userType==='student'" label="提交时间" width="180">
            <template #default="scope">
              <span v-if="committeds?.some(item => item.assignment_id === scope.row.id)">{{ committeds.find(item => item.assignment_id === scope.row.id).submitted_at.split('.')[0] }}</span>
              <span v-else>未提交</span>
            </template>
          </el-table-column>
          <el-table-column v-if="userType==='student'" label="分数" width="100">
            <template #default="scope">
              <span v-if="committeds?.some(item => item.assignment_id === scope.row.id)">{{ committeds.find(item => item.assignment_id === scope.row.id).grade === -1 ? '未评': committeds.find(item => item.assignment_id === scope.row.id).grade}}</span>
              <span v-else>未提交</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="scope">
              <el-button v-if="userType==='teacher'" type="primary" link @click="manageAssignment(scope.row)">
                批阅管理
              </el-button>
              <el-button v-if="userType==='teacher' && scope.row.isMutualAssessment && !scope.row.isPostMutualAssessment" type="primary" link @click="generateMutual(scope.row)">
                互评任务
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
              <el-button 
                v-if="userType==='student' && committeds?.some(item => item.assignment_id === scope.row.id)"
                type="info"
                @click="goToCommittedDetail(committeds?.find(item => item.assignment_id === scope.row.id))"
              >
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

      <!--互评任务发布对话框-->
      <el-dialog 
        v-model="mutualDialogVisible"
        title="提示"
        width="500"
      >
        <label>作业：{{ mutalAssignment.title }}</label>
        <p>确认发布互评任务吗？</p>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="mutualDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="publishMutual();mutualDialogVisible = false">
              确认
            </el-button>
          </div>
        </template>
      </el-dialog>

    </div>

    <div class="manage-container" v-if="showManagePage">
      <h2>作业批阅/管理</h2>
      <div class="assignment-details">
        <h3>作业标题：{{ managedAssignment.title }}</h3>
        <p>提交时间：{{ managedAssignment.start_date }} - {{ managedAssignment.due_date }}</p>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="作业批阅/成绩" name="review">
            <el-table :data="submissions.data" style="width: 100%">
              <el-table-column prop="student_id" label="学号" />
              <el-table-column prop="student_name" label="姓名" />
              <el-table-column label="提交时间">
                <template #default="scope">
                  <span>{{scope.row.submitted_at.split('.')[0]}}</span>
                </template>
              </el-table-column>
              <el-table-column label="成绩">
                <template #default="scope">
                  <span>{{scope.row.grade === -1?'未评':scope.row.grade}}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="text" @click="goToCommittedDetail(scope.row)">批阅</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="未提交学生名单" name="notSubmitted">
            <el-table :data="submissions.not_submitted_students">
              <el-table-column prop="sno" label="学号" />
              <el-table-column prop="sname" label="姓名" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { ElMessage } from 'element-plus';
  import {assignmentListService,
          assignmentAddService,
          assignmentDeleteService,
          assignmentUpdateService,
          assignmentCommitService,
          committedListService,
          manageListService,
          mutualAddService, } from '@/api/homepage';
  
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

  const router = useRouter();
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
  const committeds = ref([]);
  const showManagePage = ref(false);
  const mutualDialogVisible = ref(false);
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


  const fetchCommitteds = async () => {
    if(props.userType === 'student') {
      try {
        let result = await committedListService(props.courseNo);
        if(result.status === 200) {
          committeds.value = result.data.data;
        }
      } catch (err) {
        ElMessage.error('获取已提交作业失败');
        console.log(err);
      }
    }
  }
  fetchCommitteds();

  

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
        await fetchHomeworks();
      } else if (result.status === 200) {
        ElMessage.success('覆盖作业成功');
      } else if(result.status === 205){
        ElMessage.warning('逾期不能提交');
      }
    } catch (err) {
      ElMessage.error('提交作业失败');
      console.log(err);
    }
    commitDialogVisible.value = false;
  }

  const goToCommittedDetail = (committed) => {
    router.push({
      name:'CommittedDetail', 
      params:{
        courseNo:props.courseNo,
        assignmentId:committed.assignment_id,
        sno:committed.student_id,
      }});
  }

  const manageAssignment = (assignment) => {
    managedAssignment.value = assignment;
    fetchManaged();
    showManagePage.value = true;
  }

  const mutalAssignment = ref({});

  const generateMutual = (assignment) => {
    mutalAssignment.value = assignment;
    mutualDialogVisible.value = true;
  }

  const publishMutual = async() => {
    try {
      let result = await mutualAddService(mutalAssignment.value.id);
      if(result.status === 200){
        ElMessage.success('发布互评任务成功');
      }
    } catch (err) {
      ElMessage.error('发布互评任务失败');
      console.log(err);
    }
  }

  //manage-page
  const managedAssignment = ref({});
  const activeTab = ref('review');
  const submissions = ref([]); 

  const fetchManaged = async() => {
    try {
      let result = await manageListService(props.courseNo,managedAssignment.value.id);
      if(result.status === 200){
        submissions.value = result.data;
      }
    } catch (err) {
      ElMessage.error('获取作业管理失败');
      console.log(err);
    }
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

  .manage-container {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.assignment-details {
  margin-top: 20px;
}

.assignment-details h3 {
  margin-bottom: 10px;
}

.assignment-details p {
  margin-bottom: 20px;
}
  </style>