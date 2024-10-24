<template>
  <div class="discussion-detail">
    <!-- 搜索功能 -->
    <div class="search-bar">
      <input
        type="text"
        v-model="searchQuery"
        @input="filterReview"
        placeholder="搜索回复内容"
      />
    </div>

    <h2>{{ discussion.dtitle }}</h2>
    <p>{{ discussion.dinfo }}</p>
    <p>作者：{{ discussion.ownerNo }}</p>
    <p>发表于：{{ formatDate(discussion.postTime) }}</p>
    <div v-if="discussion.pictures && discussion.pictures.length">
          <h4>图片展示：</h4>
          <div class="images">
            <img
              v-for="(picture, index) in discussion.pictures"
              :key="index"
              :src="`${BUCKET_URL}${picture.pfile}`"
              alt="讨论图片"
              class="discussion-image"
            />
          </div>
    </div>

    <!-- 显示评论列表 -->
    <div v-if="discussion.reviews && discussion.reviews.length > 0">
        <h3>评论</h3>
        <div v-for="comment in discussion.reviews" :key="comment.rno">
            <p>{{ comment.ownerNo }}: {{ comment.rinfo }}</p>
            <p>发表于：{{ formatDate(comment.postTime) }}</p>
            <p>点赞数：{{ comment.likeNum }}</p>
            <button @click="deleteComment(comment.rno)">删除</button>
            <button @click="likeComment(comment)">
               {{ comment.is_liked ? '取消点赞':'点赞'}}
            </button>
            <!-- 添加评论图片展示逻辑 -->
            <div v-if="comment.pictures && comment.pictures.length">
                <h4>评论图片：</h4>
                <div class="images">
                    <img
                        v-for="(picture, index) in comment.pictures"
                        :key="index"
                        :src="`${BUCKET_URL}${picture.pfile}`"
                        alt="评论图片"
                        class="discussion-image"
                    />
                </div>
            </div>
        </div>
    </div>
    <!-- 发起讨论功能 -->
    <div class="post-form">
    <h3>回复评论</h3>
    <form @submit.prevent="submitPost">
      <div>
        <label for="content">正文:</label>
        <textarea v-model="content" required></textarea>
      </div>
      <div>
        <label for="images">上传图片:</label>
        <input type="file" @change="handleFileUpload" multiple accept="image/*" />
      </div>
      <div class="image-preview">
        <h2>预览:</h2>
        <div v-if="imagePreviews.length">
          <img v-for="(img, index) in imagePreviews" :key="index" :src="img" alt="Image Preview" style="max-width: 100px; margin: 5px;" />
        </div>
      </div>
      <button type="submit">提交评论</button>
    </form>
  </div>
    <!-- 加载状态 -->
    <div v-if="loading">加载中...</div>
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios';
import OSS from 'ali-oss';

const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com'
const API_URL = 'http://localhost:8000/chatRoom/0001/discussion/5/review';

// 创建 Axios 实例
const instance = axios.create();

// 添加请求拦截器
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token'); // 从本地存储获取令牌
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});


export default {
  name: 'ReviewComponent',
  data() {
    return {
      BUCKET_URL,
      API_URL,
      discussion: {}, // 存储讨论详情
      newComment: '',  // 新评论内容
      loading: false,  // 加载状态
      error: null,     // 错误信息

      filteredDiscussions: [], // 经过过滤的讨论列表
      searchQuery: '', // 搜索关键字

      content: '',
      selectedFiles: [],
      imagePreviews: [],
      ossClient: null,

      isEditing: false,
      editingDiscussion:{},
      selectedImage:null,
    };
  },
  created() {
    this.initOSSClient();
    // const dno = this.$route.params.dno; // 从路由参数中获取讨论ID
    this.fetchDiscussionDetail(); // 获取讨论详情
  },
  methods: {
    async fetchDiscussionDetail() {
      this.loading = true; // 开始加载
      this.error = null;   // 清除之前的错误
      try {
        const response = await instance.get(API_URL); // 调用API获取数据
        this.discussion = response.data.data; // 更新讨论数据，注意访问data属性

        console.log(this.discussion); // 打印讨论数据用于调试
      } catch (err) {
        this.error = `获取讨论详情失败: ${err.message}`; // 捕获并显示错误信息
      } finally {
        this.loading = false; // 加载结束
      }
    },
    // 格式化日期
    formatDate(dateString) {
      const options = {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'};
      return new Date(dateString).toLocaleDateString('zh-CN', options);
    },

    // 根据搜索查询过滤讨论内容
    // filterReview() {
    //   const query = this.searchQuery.toLowerCase();
    //   this.filteredDiscussions = this.discussion.filter(discussion =>
    //       discussion.reviews.rfino.toLowerCase().includes(query)
    //   );
    // },

    // 初始化阿里云OSS客户端
    initOSSClient() {
      this.ossClient = new OSS({
        region: 'oss-cn-beijing', // 例如 'oss-cn-hangzhou'
        accessKeyId: 'LTAI5tAtNfQg5VqN22gT3Tsn',
        accessKeySecret: 'Mqha28ubnHLtRlZaaDhXiqz6O9Xnwf',
        bucket: 'edu-platform-2024',
      });
    },
    // 发起新讨论
    handleFileUpload(event) {
      const files = Array.from(event.target.files);
      if (files.length + this.selectedFiles.length > 9) {
        alert('最多只能上传9张图片！');
        return;
      }

      this.selectedFiles = [...this.selectedFiles, ...files];
      this.imagePreviews = this.selectedFiles.map(file => URL.createObjectURL(file));
    },
    async uploadImages() {
      const uploadedImageUrls = [];

      for (const file of this.selectedFiles) {
        const fileName = `course/pic/${Date.now()}_${file.name}`; // 根据需要生成文件名
        try {
          const result = await this.ossClient.put(fileName, file);
          uploadedImageUrls.push(result.url);
        } catch (error) {
          console.error('上传失败:', error);
        }
      }
      return uploadedImageUrls;
    },
    async submitPost() {
      if (!this.content) {
        alert('请填写正文！');
        return;
      }

      const uploadedImages = await this.uploadImages();

      // 提交帖子数据
      const postData = {
        content: this.content,
        images: uploadedImages,
      };

      try {
        // 使用 axios 提交数据到后端接口
        const response = await instance.post(API_URL, postData);
        console.log('帖子提交响应:', response.data);
        alert('帖子提交成功！');
        // await this.fetchDiscussions();
      } catch (error) {
        console.error('帖子提交失败:', error);
        alert('帖子提交失败，请重试！');
      }

      // 清空表单
      this.content = '';
      this.selectedFiles = [];
      this.imagePreviews = [];
    },

    async deleteComment(commentId) {
      try {
        const response = await instance.delete(`${API_URL}/${commentId}`);
        if (response.status === 200) {
          this.discussion.reviews = this.discussion.reviews.filter(comment => comment.rno !== commentId);
        }
      } catch (err) {
        this.error = `删除评论失败: ${err.message}`;
      }
    },

    async likeComment(comment) {
      const API_URL = 'http://localhost:8000/chatRoom/Like'
      try {
        const response = await instance.post(`${API_URL}/${comment.rno}`);
        if (response.status === 200) {
            alert('操作成功');
            await this.fetchDiscussionDetail()
        }
      } catch (err) {
        this.error = `操作失败: ${err.message}`;
      }
    },
  },
};
</script>

<style>
/* 你的样式 */
.discussion-detail {
  padding: 20px;
}

h2 {
  color: #333;
}

h3 {
  margin-top: 20px;
}

textarea {
  width: 100%;
  height: 80px;
  margin-top: 10px;
}

button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #007BFF;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
