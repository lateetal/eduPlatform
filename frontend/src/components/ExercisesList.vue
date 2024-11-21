<template>
<div class="exercises-container">
    <div class="header">
        <div class="tabs">
            <button v-if="props.userType==='teacher'" class="tab active" @click="dialogTitle = '新建习题';dialogVisible = true">新建习题</button>
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
            <th>题干</th>
            <th>知识点</th>
            <th>题型</th>
            <th>难易</th>
            <th>创建时间</th>
            <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(exercise,index) in exercises" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ exercise.content }}</td>
            <td>{{ exercise.knowledge_point }}</td>
            <td>{{ exercise.question_type }}</td>
            <td>{{ exercise.difficulty }}</td>
            <td>{{ exercise.created_at }}</td>
            <td class="actions">
                <button class="action-btn edit" @click="viewDialog(exercise)">查看</button>
                <button v-if="props.userType==='teacher'" class="action-btn delete" @click="deleteExercise(exercise.id)">删除</button>
            </td>
            </tr>
        </tbody>
    </table>

    <el-dialog
        v-model="dialogVisible"
        :title="dialogTitle"
        width="50%"
        :before-close="handleClose"
    >
        <el-form :model="exerciseForm" label-width="120px">
            <el-form-item label="题型">
                <el-select 
                    v-model="exerciseForm.question_type"
                    placeholder="选择题型"
                >
                    <el-option
                        v-for="(item,index) in questionTypes"
                        :key="index"
                        :label="item.label"
                        :value="item.value"
                    />
                </el-select>
            </el-form-item>

            <el-form-item label="难度">
                <el-select 
                    v-model="exerciseForm.difficulty"
                    placeholder="选择难度"
                >
                    <el-option
                        v-for="(item,index) in difficultyTypes"
                        :key="index"
                        :label="item.label"
                        :value="item.value"
                    />
                </el-select>
            </el-form-item>
          
            <el-form-item label="题干">
                <el-input 
                    v-model="exerciseForm.content" 
                    placeholder="请输入题干" 
                />
            </el-form-item>

            <el-form-item label="知识点">
                <el-input 
                    v-model="exerciseForm.knowledge_point" 
                    placeholder = "请输入知识点"
                />
            </el-form-item>

            <el-form-item 
                v-if="exerciseForm.question_type === '单选题' || exerciseForm.question_type === '多选题'"
                label="选项"
            >
                <!-- 如果是单选题，使用 el-radio-group -->
                <el-radio-group v-if="exerciseForm.question_type === '单选题'" v-model="exerciseForm.correct_answer">
                    <el-radio :label="'A'">
                        <el-input v-model="exerciseForm.options.A" placeholder="请输入选项A"></el-input>
                    </el-radio>
                    <el-radio :label="'B'">
                        <el-input v-model="exerciseForm.options.B" placeholder="请输入选项B"></el-input>
                    </el-radio>
                    <el-radio :label="'C'">
                        <el-input v-model="exerciseForm.options.C" placeholder="请输入选项C"></el-input>
                    </el-radio>
                    <el-radio :label="'D'">
                        <el-input v-model="exerciseForm.options.D" placeholder="请输入选项D"></el-input>
                    </el-radio>
                </el-radio-group>

                <!-- 如果是多选题，使用 el-checkbox-group -->
                <el-checkbox-group v-else v-model="exerciseForm.correct_answer">
                    <el-checkbox :label="'A'">
                        <el-input v-model="exerciseForm.options.A" placeholder="请输入选项A"></el-input>
                    </el-checkbox>
                    <el-checkbox :label="'B'">
                        <el-input v-model="exerciseForm.options.B" placeholder="请输入选项B"></el-input>
                    </el-checkbox>
                    <el-checkbox :label="'C'">
                        <el-input v-model="exerciseForm.options.C" placeholder="请输入选项C"></el-input>
                    </el-checkbox>
                    <el-checkbox :label="'D'">
                        <el-input v-model="exerciseForm.options.D" placeholder="请输入选项D"></el-input>
                    </el-checkbox>
                </el-checkbox-group>
            </el-form-item>

            <el-form-item v-else label="答案">
                <el-input v-model="exerciseForm.answer_explanation" placeholder="请输入答案" autosize />
            </el-form-item>

        </el-form>

        <template v-if="dialogTitle==='新建习题'" #footer>
          <span class="dialog-footer">
            <el-button @click="handleClose()">取消</el-button>
            <el-button type="primary" @click="addExerice()">
              确认
            </el-button>
          </span>
        </template>
      </el-dialog>
</div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { exerciseListService,
        exerciseAddService,
        exerciseDeleteService,
        } from '@/api/homepage';

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

const exercises = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('');
const exerciseForm = ref({
    question_type: '',
    difficulty: '',
    knowledge_point: '',
    content: '',
    options: {
        A:'',
        B:'',
        C:'',
        D:'',
    },
    correct_answer: '',
    answer_explanation: '',
});
const questionTypes = [
    {
        value:'单选题',
        label:'单选题',
    },
    {
        value:'多选题',
        label:'多选题',
    },
    {
        value:'主观题',
        label:'主观题',
    },
];
const difficultyTypes = [
    {
        value:'简单',
        label:'简单',
    },
    {
        value:'中等',
        label:'中等',
    },
    {
        value:'困难',
        label:'困难',
    },
];

const fetchExercises = async () => {
    try{
        let result = await exerciseListService(props.courseNo,'all');
        if(result.status === 200) {
            exercises.value = result.data.data;
        }
    } catch (err) {
        console.log(err);
    }
}
fetchExercises();

const handleClose = () => {
    exerciseForm.value = {
        question_type: '',
        difficulty: '',
        knowledge_point: '',
        content: '',
        options: {
            A:'',
            B:'',
            C:'',
            D:'',
        },
        correct_answer: [],
        answer_explanation: '',
    }
    dialogVisible.value = false;
}

const addExerice = async () => {
    const formData = new FormData();
    formData.append('question_type', exerciseForm.value.question_type);
    formData.append('difficulty', exerciseForm.value.difficulty);
    formData.append('knowledge_point', exerciseForm.value.knowledge_point);
    formData.append('content', exerciseForm.value.content);

    // 判断题型是否是单选题或者多选题
    if (exerciseForm.value.question_type === '单选题' || exerciseForm.value.question_type === '多选题') {
        // 将 options 转换为 JSON 字符串
        formData.append('options', JSON.stringify(exerciseForm.value.options));

        if (exerciseForm.value.question_type === '单选题') {
            formData.append('correct_answer', exerciseForm.value.correct_answer);
        } else {
            formData.append('correct_answer', exerciseForm.value.correct_answer.join(','));
        }
    } else if (exerciseForm.value.question_type === '主观题') {
        formData.append('answer_explanation', exerciseForm.value.answer_explanation);
    }

    try {
        let result = await exerciseAddService(props.courseNo, formData);
        if (result.status === 201) {
            ElMessage.success('新建习题成功');
            await fetchExercises();
    }
        } catch (err) {
        ElMessage.error('新建习题失败');
        console.log(err);
    }
    handleClose();
};

const deleteExercise = async(id) => {
    try {
        let result = await exerciseDeleteService(props.courseNo, id);
        if(result.status === 200){
            ElMessage.success('删除习题成功');
            fetchExercises();
        }
    } catch (err) {
        ElMessage.error('删除习题失败');
        console.log(err);
    }
}

const viewDialog = (exercise) => {
    dialogTitle.value = '查看习题';
    exerciseForm.value = exercise;
    if(exercise.options){
      exerciseForm.value.options = JSON.parse(exercise.options)
    }

    if(exerciseForm.value.question_type === '多选题'){
        const arr = exerciseForm.value.correct_answer.split(',');
        exerciseForm.value.correct_answer = arr;
    }
    dialogVisible.value = true;
}

watch(
  () => exerciseForm.value.question_type,
  (newType) => {
    if (newType === '多选题') {
      // 如果是从单选题切换到多选题，将 correct_answer 转换为数组
      if (typeof exerciseForm.value.correct_answer === 'string') {
        exerciseForm.value.correct_answer = [exerciseForm.value.correct_answer];
      }
    } else {
      // 如果是从多选题切换回单选题，确保 correct_answer 只有一个选项
      if (Array.isArray(exerciseForm.value.correct_answer)) {
        exerciseForm.value.correct_answer = exerciseForm.value.correct_answer[0] || '';
      }
    }
  }
);
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