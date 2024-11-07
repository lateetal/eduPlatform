<template>
    <main class="main-content">
      <div class="content-header">
        <h2>{{ getContentTitle() }}</h2>
        <div class="content-actions">
          <el-button 
            type="primary"
            v-if="selectedTab === 'introduction' && userType === 'teacher'"
            @click="$emit('show-edit-dialog')"
          >编辑
          </el-button>
          <el-button 
            type="primary" 
            @click="$emit('show-upload-dialog')"
            v-if="(selectedTab === 'outline' || selectedTab === 'calendar') && userType === 'teacher'"
          >上传
          </el-button>
          <el-button 
            type="success" 
            @click="handleDownload"
            v-if="selectedTab === 'outline' || selectedTab === 'calendar'"
          >下载
          </el-button>
        </div>
      </div>
      
      <div v-if="selectedTab === 'introduction'" class="course-intro">
        <p>{{ courseData?.data?.cintro || 'cintro' }}</p>
      </div>
      <div v-if="selectedTab === 'outline'" class="course-outline">
        <div v-if="courseData?.data?.coutline" class="pdf-container">
          <VuePdfEmbed annotation-layer text-layer :source="BUCKET_URL + courseData.data.coutline" />
        </div>
        <p v-else>No PDF available</p>
      </div>
      <div v-if="selectedTab === 'calendar'" class="course-calendar">
        <div v-if="courseData?.data?.calender" class="pdf-container">
          <VuePdfEmbed annotation-layer text-layer :source="BUCKET_URL + courseData.data.calender" />
        </div>
        <p v-else>No PDF available</p>
      </div>
      <div v-if="selectedTab === 'professor'" class="course-professor">
        <p>教师姓名：{{ courseData?.data?.teacher?.tname || 'tname'}}</p>
        <p>邮箱：{{ courseData?.data?.teacher?.tmail || 'tmail'}}</p>
        <p>办公室：{{ courseData?.data?.teacher?.toffice || 'toffice'}}</p>
        <p>电话：{{ courseData?.data?.teacher?.tphone || 'tphone'}}</p>
        <p>介绍：{{ courseData?.data?.teacher?.tintro || 'tintro'}}</p>
      </div>
      <div v-if="selectedTab === 'student'"  class="course-student">
        <ul>
          <li v-for="student in students" :key="student.sno">
            <h3>{{ student.sno }}</h3>
            <p>{{ student.sname }}</p>
          </li>
        </ul>
      </div>
      <div v-if="selectedTab === 'ppts'" class="course-ppts">
        <CoursePPT :courseNo="courseNo" />
      </div>
  
      <div v-if="selectedTab === 'papers'" class="course-papers">
        <!-- Implement papers content -->
      </div>
      <div v-if="selectedTab === 'exercises'" class="course-exercises">
        <!-- Implement exercises content -->
      </div>
  
      <div v-if="selectedTab === 'homework'" class="course-homework">
        <!-- Implement homework content -->
      </div>
      
      <div v-if="selectedTab === 'discussion'" class="course-discussion">
        <DiscussionBoard :courseNo="courseNo" />
      </div>

      <div v-if="selectedTab === 'AIhelper'" class="course-AIhelper">
        <div id="chat-container">
          <div v-for="(msg, index) in chatHistory" :key="index" :class="msg.role">
            <div v-html="convertMarkdown(msg.content)"></div>
          </div>
        </div>
        <input type="text" v-model="userInput" placeholder="输入消息..." />
        <button @click="handleSend">发送</button>
      </div>
  
      <div v-if="selectedTab === 'notice'" class="course-notice">
        <form @submit.prevent="sendMessage">
          <div>
            <ul>
              <li v-for="message in messages" :key="message.mno">
                <p>{{ message.mtitle }}</p>
                <p>{{ message.minfo }}</p>
                <button v-if="userType === 'teacher'" @click="deleteMessage(message.mno)">删除</button>
              </li>
            </ul>
          </div>
  
          <div v-if="userType === 'teacher'">
            <input v-model="title" placeholder="标题" required />
            <textarea v-model="info" placeholder="正文" required></textarea>
            <button type="submit">发送通知</button>
          </div>
        </form>
      </div>
    </main>
  </template>
  
  <script>
import DiscussionBoard from './DiscussionBoard.vue';
import CoursePPT from './CoursePPT.vue';
import { ref } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed';
import { marked } from 'marked';
  
  const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';
  const AI_URL = 'http://localhost:8000/homepage/aichat';

  export default {
    components: {
      DiscussionBoard,
      CoursePPT,
      VuePdfEmbed,
    },
    props: {
      selectedTab: {
        type: String,
        required: true,
      },
      courseData: {
        type: Object,
        required: true,
      },
      userType: {
        type: String,
        required: true,
      },
      courseNo: {
        type: String,
        required: true,
      },
      messages: {
        type: Array,
        required: true,
      },
      students: {
        type: Array,
        required: true,
      },
    },
    emits: ['show-edit-dialog', 'show-upload-dialog', 'show-new-folder-dialog', 'delete-message', 'send-message'],
    setup(props, { emit }) {
      const chatContainer = ref(null);
      const userInput = ref('');
      const chatHistory = ref([]);
      const title = ref('');
      const info = ref('');
  
      const getContentTitle = () => {
        switch (props.selectedTab) {
          case 'introduction': return '课程介绍';
          case 'outline': return '教学大纲';
          case 'calendar': return '教学日历';
          case 'professor': return '教师信息';
          case 'ppts': return '课件';
          case 'papers': return '历年试题库';
          case 'exercises': return '习题库';
          case 'homework': return '作业';
          case 'discussion': return '讨论区';
          case 'AIhelper': return 'AI问答';
          case 'notice': return '通知';
          case 'student': return '选课学生';
          default: return '';
        }
      };
  
      const handleDownload = () => {
        console.log('Download button clicked');
        // Implement download logic here
      };
  
      const updateChatHistory = () => {
        if (chatContainer.value) {
          chatContainer.value.innerHTML = chatHistory.value.map(msg => `
            <div class="message ${msg.role}">${msg.content}</div>
          `).join('');
        }
      };
  
      const handleSend = async () => {
        const input = userInput.value.trim();
        if (input) {
          chatHistory.value.push({ role: 'user', content: input });
          updateChatHistory();
          userInput.value = '';
  
          try {
            const response = await fetch(AI_URL, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ input }),
            });
  
            if (response.ok) {
              const data = await response.json();
              chatHistory.value.push({ role: 'ai', content: data.message });
            } else {
              chatHistory.value.push({ role: 'ai', content: '请求失败，请稍后再试。' });
            }
          } catch (error) {
            chatHistory.value.push({ role: 'ai', content: '网络错误，请稍后再试。' });
          }
          updateChatHistory();
        }
      };
  
      const convertMarkdown = (content) => {
        return marked(content);
      };

      const deleteMessage = (mno) => {
        emit('delete-message', mno);
      };
  
      const sendMessage = () => {
        emit('send-message', { title: title.value, info: info.value });
        title.value = '';
        info.value = '';
      };

      return {
        BUCKET_URL,
        chatContainer,
        userInput,
        chatHistory,
        title,
        info,

        getContentTitle,
        handleDownload,
        handleSend,
        updateChatHistory,
        convertMarkdown,
        deleteMessage,
        sendMessage,
      };
    },
  };
  </script>
  
  <style scoped>
  .main-content {
    flex-grow: 1;
    padding: 30px;
    background-color: #fff;
    margin: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
  }
  
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    border-bottom: 2px solid #4a69bd;
    padding-bottom: 10px;
  }
  
  .content-header h2 {
    font-size: 24px;
    color: #4a69bd;
  }
  
  .content-actions {
    display: flex;
    gap: 10px;
  }
  
  /* Styles for student list */
  .course-student ul {
    list-style-type: none;
    padding: 0;
  }
  
  .course-student li {
    background-color: #f0f4f8;
    margin-bottom: 10px;
    padding: 15px;
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .course-student h3 {
    margin: 0;
    font-size: 18px;
    color: #4a69bd;
  }
  
  .course-student p {
    margin: 5px 0 0;
    font-size: 18px;
    color: #666;
  }
  
  /* Styles for AI Q&A */
  .course-AIhelper {
    display: flex;
    flex-direction: column;
    height: 500px;
  }
  
  #chat-container {
    flex-grow: 1;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    padding: 15px;
    margin-bottom: 15px;
  }
  
  .course-AIhelper .user, .course-AIhelper .ai {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 5px;
  }
  
  .course-AIhelper .user {
    background-color: #e1f5fe;
    align-self: flex-end;
  }
  
  .course-AIhelper .ai {
    background-color: #f0f4f8;
    align-self: flex-start;
  }
  
  .course-AIhelper input[type="text"] {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-bottom: 10px;
  }
  
  .course-AIhelper button {
    padding: 10px 20px;
    background-color: #4a69bd;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .course-AIhelper button:hover {
    background-color: #3a559d;
  }
  
  /* Styles for course notifications */
  .course-notice ul {
    list-style-type: none;
    padding: 0;
  }
  
  .course-notice li {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    margin-bottom: 15px;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  
  .course-notice li p:first-child {
    font-size: 18px;
    font-weight: 600;
    color: #4a69bd;
    margin-bottom: 10px;
  }
  
  .course-notice li p:last-child {
    font-size: 14px;
    color: #666;
  }
  
  .course-notice button {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .course-notice button:hover {
    background-color: #d32f2f;
  }
  
  .course-notice form div {
    margin-top: 20px;
  }
  
  .course-notice input, .course-notice textarea {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }
  
  .course-notice textarea {
    height: 100px;
    resize: vertical;
  }
  
  .course-notice form button {
    background-color: #4caf50;
    padding: 10px 20px;
  }
  
  .course-notice form button:hover {
    background-color: #45a049;
  }

  .course-discussion {
  width: 100%;
}
  </style>