<template>
<div class="exercises-container">
    <div class="header">
        <div class="tabs">
            <button v-if="props.userType==='teacher'" class="tab active" @click="uploadForm.file='';dialogVisible = true">上传试卷</button>
        </div>
        <div class="search">
            <input type="text" placeholder="搜索习题关键字" class="search-input" />
            <button class="search-btn">搜索</button>
        </div>
    </div>

    <table class="exercises-table">
        <thead>
            <tr>
            <th>序号</th>
            <th>标题</th>
            <th>描述</th>
            <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(paper,index) in papers" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ paper.rname }}</td>
                <td>{{ paper.rdesc }}</td>
                <td class="actions">
                    <button class="action-btn edit" @click="downloadPaper(paper)">下载</button>
                    <button v-if="props.userType==='teacher'" class="action-btn delete" @click="deletePaper(paper.rno)">删除</button>
                </td>
            </tr>
        </tbody>
    </table>

    <el-dialog
        v-model="dialogVisible"
        title="上传试卷"
        width="50%"
        :before-close="handleClose"
      >
        <el-form :model="paperForm" label-width="120px">
          <el-form-item label="标题">
            <el-input v-model="paperForm.resource_name" placeholder="请输入作业标题" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="paperForm.resource_description"
              type="textarea"
              rows="4"
              placeholder="请输入描述"
            />
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
            <el-button @click="dialogVisible = false;clearPaperForm()">取消</el-button>
            <el-button type="primary" @click="addPaper()">
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
import { paperListService,
        paperAddService,
        paperDeleteService} from '@/api/homepage';

const props = defineProps({
    courseNo: {
        type: String,
        required: true
    },
    userType: {
        type: String,
        required: true
    },
})    

const dialogVisible = ref(false);
const papers = ref([]);
const paperForm = ref({
    resource_name:'',
    resource_description:'',
});
const uploadForm = ref({ file: null });

const clearPaperForm = () => {
    paperForm.value = {
        resource_name:'',
        resource_description:'',
    }
}

const handleClose = () => {
    dialogVisible.value = false;
    clearPaperForm();
}

const handleFileChange = (file) => {
    uploadForm.value.file = file.raw;
};

const fetchPapers = async () => {
    try {
        let result = await paperListService(props.courseNo);
        if(result.status === 200) {
            papers.value = result.data.data.Uncategorized;
        }
    } catch (err) {
        ElMessage.error('获取试卷失败');
        console.log(err);
    }
}
fetchPapers();

const addPaper = async () => {
    const formData = new FormData();
    formData.append('resource_name',paperForm.value.resource_name);
    formData.append('resource_description',paperForm.value.resource_description);
    formData.append('resource_file',uploadForm.value.file);
    try {
        let result = await paperAddService(props.courseNo, formData);
        if(result.status === 201){
            ElMessage.success('上传试卷成功');
            fetchPapers();
            dialogVisible.value = false;
            clearPaperForm();
        }
    } catch (err){
        ElMessage.error('上传试卷失败');
        console.log(err);
    }
}

const deletePaper = async (rno) => {
    try {
        let result = await paperDeleteService(props.courseNo,rno);
        if(result.status === 200) {
            ElMessage.success('删除试卷成功');
            fetchPapers();
        }
    } catch (err) {
        ElMessage.error('删除试卷失败');
        console.log(err);
    }
}

const downloadPaper = (paper) => {
    const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/';
    const downloadUrl = BUCKET_URL + paper.rfile;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = paper.rfile.split('/').pop(); 
    link.click();
}

</script>

<style scoped>
.exercises-container {
padding: 20px;
background-color: #fff;
}

.header {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 20px;
}

.tabs {
display: flex;
gap: 10px;
}

.tab {
padding: 8px 16px;
background-color: #5c7cba;
color: white;
border: none;
border-radius: 4px;
cursor: pointer;
}

.tab.active {
background-color: #4a63a3;
}

.search {
display: flex;
gap: 10px;
}

.search-input {
padding: 6px 12px;
border: 1px solid #ddd;
border-radius: 4px;
width: 200px;
}

.search-btn {
padding: 6px 16px;
background-color: #5c7cba;
color: white;
border: none;
border-radius: 4px;
cursor: pointer;
}

.exercises-table {
width: 100%;
border-collapse: collapse;
}

.exercises-table th,
.exercises-table td {
padding: 12px;
text-align: left;
border-bottom: 1px solid #eee;
}

.exercises-table th {
background-color: #f8f9fa;
font-weight: normal;
}

.actions {
display: flex;
gap: 8px;
}

.action-btn {
padding: 4px 8px;
border: none;
border-radius: 4px;
cursor: pointer;
color: white;
}

.action-btn.edit {
background-color: #5c7cba;
}

.action-btn.score {
background-color: #5c7cba;
}

.action-btn.delete {
background-color: #5c7cba;
}

.action-btn:hover {
opacity: 0.9;
}
</style>