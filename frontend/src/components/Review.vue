<template>
  <div class="discussion-board">
    <div class="container">
      <h2 class="title">{{ discussion.dtitle }}</h2>

      <!-- 搜索功能 -->
      <div class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索回复内容"
        />
        <button @click="filterReviews">查找</button>
      </div>

      <!-- 显示加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 讨论详情 -->
      <div v-else-if="discussion" class="discussion-item">
        <p class="discussion-content">{{ discussion.dinfo }}</p>
        <div class="discussion-meta">
          <span class="author">{{ discussion.ownerNo }}</span>
          <span class="post-time">发表于：{{ formatDate(discussion.postTime) }}</span>
        </div>

        <!-- 展示图片 -->
        <div v-if="discussion.pictures && discussion.pictures.length" class="image-gallery">
          <h4>图片展示：</h4>
          <div class="image-grid">
            <img
              v-for="(picture, index) in discussion.pictures"
              :key="index"
              :src="`${BUCKET_URL}${picture.pfile}`"
              alt="讨论图片"
              class="discussion-image"
            />
          </div>
        </div>
      </div>

      <!-- 评论列表 -->
      <div v-if="filteredReviews.length > 0" class="discussion-list">
        <h3 class="subtitle">评论</h3>
        <div v-for="comment in filteredReviews" :key="comment.rno" class="discussion-item">
          <p class="discussion-content">{{ comment.rinfo }}</p>
          <div class="discussion-meta">
            <span class="author">{{ comment.ownerNo }}</span>
            <span class="post-time">发表于：{{ formatDate(comment.postTime) }}</span>
          </div>
          <p>点赞数：{{ comment.likeNum }}</p>

          <!-- 评论图片 -->
          <div v-if="comment.pictures && comment.pictures.length" class="image-gallery">
            <h4>评论图片：</h4>
            <div class="image-grid">
              <img
                v-for="(picture, index) in comment.pictures"
                :key="index"
                :src="`${BUCKET_URL}${picture.pfile}`"
                alt="评论图片"
                class="discussion-image"
              />
            </div>
          </div>

          <div class="action-buttons">
            <button @click="deleteComment(comment.rno)" class="delete-btn">删除</button>
            <button @click="likeComment(comment)" class="favorite-btn">
              {{ comment.is_liked ? '取消点赞' : '点赞' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 如果没有评论 -->
      <div v-else-if="!loading" class="no-discussions">
        暂无评论。
      </div>

      <!-- 发表评论 -->
      <div class="new-discussion">
        <h3>发表评论</h3>
        <form @submit.prevent="submitPost">
          <div class="form-group">
            <label for="content">正文:</label>
            <textarea v-model="content" required></textarea>
          </div>
          <div class="form-group">
            <label for="images">上传图片:</label>
            <input type="file" @change="handleFileUpload" multiple accept="image/*" />
          </div>
          <div v-if="imagePreviews.length" class="image-preview">
            <h4>预览:</h4>
            <div class="image-grid">
              <img v-for="(img, index) in imagePreviews" :key="index" :src="img" alt="Image Preview" />
            </div>
          </div>
          <button type="submit" class="submit-btn">提交评论</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import OSS from 'ali-oss';

const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';
const API_URL = 'http://localhost:8000/chatRoom/';

// 创建 Axios 实例
const instance = axios.create();

// 添加请求拦截器
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default {
  name: 'ReviewPage',
  data() {
    return {
      BUCKET_URL,
      discussion: {},
      reviews: [],
      filteredReviews: [],
      loading: true,
      error: null,
      searchQuery: '',
      content: '',
      selectedFiles: [],
      imagePreviews: [],
      ossClient: null,
      courseNo: '',
      dno: ''
    };
  },
  created() {
    this.initOSSClient();
    this.courseNo = this.$route.params.courseNo;
    this.dno = this.$route.params.dno;
    this.fetchDiscussionDetail();
  },
  methods: {
    initOSSClient() {
      this.ossClient = new OSS({
        region: 'oss-cn-beijing',
        accessKeyId: 'LTAI5tAtNfQg5VqN22gT3Tsn',
        accessKeySecret: 'Mqha28ubnHLtRlZaaDhXiqz6O9Xnwf',
        bucket: 'edu-platform-2024',
      });
    },
    async fetchDiscussionDetail() {
      this.loading = true;
      this.error = null;
      try {
        const response = await instance.get(`${API_URL}${this.courseNo}/discussion/${this.dno}/review`);
        this.discussion = response.data.data;
        this.reviews = this.discussion.reviews || [];
        this.filteredReviews = this.reviews;
      } catch (err) {
        this.error = `获取讨论详情失败: ${err.message}`;
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateString) {
      const options = {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'};
      return new Date(dateString).toLocaleDateString('zh-CN', options);
    },
    async filterReviews() {
      if (!this.searchQuery.trim()) {
        this.filteredReviews = this.reviews;
        return;
      }

      this.loading = true;
      const API_URL = `http://localhost:8000/chatRoom/${this.courseNo}/discussion/${this.dno}/review/filtered`;
      
      try {
        const response = await instance.post(API_URL, {
          keyword: this.searchQuery.trim()
        });

        if (response.data.code === 200) {
          this.filteredReviews = response.data.data.reviews;
          
        } else {
          console.error('过滤评论失败', response.data);
          alert('过滤评论失败，请重试');
        }
      } catch (error) {
        console.error('请求失败', error);
        alert('请求失败，请重试');
      } finally {
        this.loading = false;
      }
    },

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
        const fileName = `course/pic/${Date.now()}_${file.name}`;
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
        alert('请填写评论内容！');
        return;
      }

      const uploadedImages = await this.uploadImages();

      const postData = {
        content: this.content,
        images: uploadedImages,
      };

      try {
        const response = await instance.post(`${API_URL}${this.courseNo}/discussion/${this.dno}/review`, postData);
        console.log('评论提交响应:', response.data);
        alert('评论提交成功！');
        await this.fetchDiscussionDetail();
      } catch (error) {
        console.error('评论提交失败:', error);
        alert('评论提交失败，请重试！');
      }

      this.content = '';
      this.selectedFiles = [];
      this.imagePreviews = [];
    },
    async deleteComment(commentId) {
      if (confirm('确定要删除该评论吗？')) {
        try {
          const response = await instance.delete(`${API_URL}${this.courseNo}/discussion/${this.dno}/review/${commentId}`);
          if (response.status === 200) {
            alert('评论已删除');
            await this.fetchDiscussionDetail();
          }
        } catch (err) {
          this.error = `删除评论失败: ${err.message}`;
        }
      }
    },
    async likeComment(comment) {
      try {
        const response = await instance.post(`${API_URL}Like/${comment.rno}`);
        if (response.status === 200) {
          alert(comment.is_liked ? '取消点赞成功' : '点赞成功');
          await this.fetchDiscussionDetail();
        }
      } catch (err) {
        this.error = `操作失败: ${err.message}`;
      }
    }
  }
};
</script>

<style>
.discussion-board {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  padding: 20px;
}

.container {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 20px;
  color: #333;
  margin-top: 20px;
  margin-bottom: 15px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
}

.search-bar input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 16px;
}

.search-bar button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.search-bar button:hover {
  background-color: #45a049;
}

.loading {
  text-align: center;
  padding: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-discussions {
  text-align: center;
  color: #666;
  padding: 20px;
}

.discussion-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.discussion-item {
  background-color: #fff;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 15px;
  transition: box-shadow 0.3s ease;
}

.discussion-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.discussion-content {
  color: #34495e;
  margin-bottom: 10px;
}

.discussion-meta {
  font-size: 14px;
  color: #7f8c8d;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.image-gallery {
  margin-top: 10px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.discussion-image {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-buttons button {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
}

.favorite-btn {
  background-color: #2ecc71;
  color: white;
}

.action-buttons button:hover {
  opacity: 0.8;
}

.new-discussion {
  margin-top: 30px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.new-discussion h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
}

.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 100px;
}

.image-preview {
  margin-top: 15px;
}

.image-preview h4 {
  margin-bottom: 10px;
}

.submit-btn {
  padding: 8px 15px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #2980b9;
}
</style>