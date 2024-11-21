<template>
    <div class="main-content">
        <div class="basic-info">
          <h2>基本信息</h2>
          
          <div class="info-item">
            <label>作业标题：</label>
            <span>{{ assignment.title }}</span>
          </div>

          <div class="info-item">
            <label>作业满分：</label>
            <span>{{ assignment.maxGrade }} 分</span>
          </div>

          <div class="info-item">
            <label>作业内容：</label>
            <p>{{ assignment.description }}</p>
          </div>

          <div class="info-item">
            <label>作业附件：</label>
            <div class="attachment-buttons">
                <span>{{ fileName }}</span>
              <el-button type="primary" @click="previewVisible = true">预览附件</el-button>
              <el-button @click="downloadFile">下载附件</el-button>
            </div>
            <VuePdfEmbed 
                v-if="previewVisible"
                annotation-layer 
                text-layer 
                :source="BUCKET_URL + assignment.assignment_file" 
            />
          </div>

          <div class="info-item">
            <label>提交时间：</label>
            <span>{{ assignment.start_date }} - {{ assignment.due_date }}</span>
          </div>

          <div class="info-item">
            <label v-if="assignment.allowDelaySubmission">逾期可提交</label>
          </div>
        </div>

        <div v-if="userType==='student'" class="mutual-tasks">
          <h2>互评任务</h2>
          <el-table :data="tasks" style="width: 100%">
              <el-table-column prop="student_id" label="学号" />
              <el-table-column prop="student_name" label="姓名" />
              <el-table-column label="提交时间">
                <template #default="scope">
                  <span>{{scope.row.submitted_at.split('.')[0]}}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="text" @click="goToCommittedDetail(scope.row)">互评</el-button>
                </template>
              </el-table-column>
            </el-table>
        </div>

        <div class="actions">
          <el-button type="primary" @click="goBack">关闭</el-button>
        </div>
      </div>
</template>

<script setup>
import {ref} from 'vue';
import { useRoute,useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import VuePdfEmbed from 'vue-pdf-embed';
import {getUsernameService, 
        assignmentSearchService,
        mutualListService, } from '@/api/homepage';

const route = useRoute();
const router = useRouter();
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/';
const assignmentId = route.params.assignmentId;
const courseNo = route.params.courseNo;
const assignment = ref({});
const fileName = ref('');
const previewVisible = ref(false);
const userType = ref('');
const tasks = ref([]);

const fetchUserType = async () => {
  try {
    let result = await getUsernameService();
    if(result.status === 200) {
      userType.value = result.data.userType;
    }
  } catch (err) {
    ElMessage.error('获取用户信息失败');
    console.log(err);
  }
}
fetchUserType();

const fetchAssignment = async () => {
    try {
        let result = await assignmentSearchService(courseNo, assignmentId);
        if(result.status === 200){
            assignment.value = result.data.data;
            if(assignment.value.assignment_file){
              fileName.value = assignment.value.assignment_file.split('/').pop();
            }
        }
    } catch (err){
        ElMessage.error('获取作业信息失败');
        console.log(err);
    }
}
fetchAssignment();

const fetchTasks = async () => {
  try {
    let result = await mutualListService(assignmentId);
    if(result.status === 200) {
      tasks.value = result.data.data;
      console.log(tasks)
    }
  } catch (err) {
    ElMessage.error('获取互评任务失败');
    console.log(err);
  }
}
fetchTasks();

const goBack = () => {
    router.go(-1);
}

const downloadFile = () => {
    const downloadUrl = BUCKET_URL + assignment.value.assignment_file;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = assignment.value.assignment_file.split('/').pop(); 
    link.click();
}

const goToCommittedDetail = (committed) => {
    router.push({
      name:'CommittedDetail', 
      params:{
        courseNo:courseNo,
        assignmentId:committed.assignment_id,
        sno:committed.student_id,
      }});
  }

</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f4f6f9;
  color: #333;
}

/* 主容器 */
.main-content {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 基本信息部分 */
.basic-info {
  margin-bottom: 20px;
}

.basic-info h2 {
  font-size: 24px;
  color: #4a90e2;
  margin-bottom: 20px;
}

/* 每一项信息 */
.info-item {
  margin-bottom: 16px;
}

.info-item label {
  font-weight: bold;
  color: #555;
  display: inline-block;
  width: 120px;
}

.info-item span,
.info-item p {
  color: #333;
  line-height: 1.6;
}

/* 作业附件按钮 */
.attachment-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.attachment-buttons span {
  font-size: 14px;
  color: #333;
}

.el-button {
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 4px;
}

.el-button.primary {
  background-color: #4a90e2;
  border-color: #4a90e2;
}

.el-button.primary:hover {
  background-color: #3578c3;
  border-color: #3578c3;
}

.el-button {
  background-color: #f0f2f5;
  border-color: #dcdfe6;
  color: #555;
}

.el-button:hover {
  background-color: #e6e8eb;
  border-color: #c0c4cc;
}

.el-button:focus {
  box-shadow: none;
}

/* 提交时间样式 */
.info-item p {
  margin-top: 8px;
}

/* 操作按钮 */
.actions {
  text-align: center;
  margin-top: 20px;
}

.actions .el-button {
  width: 120px;
}
</style>
