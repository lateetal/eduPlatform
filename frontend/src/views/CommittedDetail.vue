<template>
    <div class="main-content">
        <div class="basic-info">
          <h2>基本信息</h2>
          
          <div class="info-item">
            <label>作业标题：</label>
            <span>{{ assignment.title }}</span>
          </div>

          <div class="info-item">
            <label>学生：</label>
            <span>{{ committed.student_id }} {{ committed.student_name }}</span>
          </div>

          <div class="info-item">
            <label>提交时间</label>
            <span>{{ committed.submitted_at.split('.')[0] }}</span>
          </div>

          <div class="info-item" v-if="committed.delay_time">
            <label>逾期时间</label>
            <span>{{ committed.delay_time }}</span>
          </div>

          <div class="info-item">
            <label>分数：</label>
            <span v-if="committed.grade !== -1">{{ committed.grade }} / {{assignment.maxGrade}}</span>
            <span v-else>未评分</span>
          </div>

          <div class="info-item">
            <label>内容：</label>
            <p>{{ committed.submission_text }}</p>
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
                :source="BUCKET_URL + committed.submission_file" 
            />
          </div>

          <div class="info-item">
            <label>提交时间：</label>
            <span>{{  }}</span>
          </div>
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
import { assignmentSearchService,
        committedViewService,} from '@/api/homepage';

const route = useRoute();
const router = useRouter();
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/';
const assignmentId = route.params.assignmentId;
const courseNo = route.params.courseNo;
const sno = route.params.sno;
const assignment = ref({});
const fileName = ref('');
const previewVisible = ref(false);
const committed = ref({});

const fetchAssignment = async () => {
    try {
        let result = await assignmentSearchService(courseNo, assignmentId);
        if(result.status === 200){
            assignment.value = result.data.data;
        }
    } catch (err){
        ElMessage.error('获取作业信息失败');
        console.log(err);
    }
}
fetchAssignment();

const fetchCommitted = async () => {
    try {
        let result = await committedViewService(courseNo,assignmentId,sno);
        if(result.status === 200) {
            committed.value = result.data.data;
            fileName.value = committed.value.submission_file.split('/').pop();
        }
    } catch (err) {
        ElMessage.error('获取已提交作业失败');
        console.log(err);
    }
}
fetchCommitted();

const goBack = () => {
    router.go(-1);
}

const downloadFile = () => {
    const downloadUrl = BUCKET_URL + committed.value.submission_file;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = committed.value.submission_file.split('/').pop(); 
    link.click();
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