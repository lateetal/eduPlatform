<template>
  <div class="discussion-board">
    <div class="container">
      <h2 class="title">讨论区 {{ currentPath }}</h2>

      <!-- 搜索功能 -->
      <div class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          @input="filterDiscussions"
          placeholder="搜索讨论标题或内容"
        />
      </div>

      <!-- 显示加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 如果没有讨论 -->
      <div v-else-if="filteredDiscussions.length === 0" class="no-discussions">
        暂无讨论帖子。
      </div>

      <!-- 显示讨论列表 -->
      <div v-else class="discussion-list">
        <div v-for="discussion in filteredDiscussions" :key="discussion.dno" class="discussion-item">
          <h3 @click="goToDiscussionDetail(discussion.dno)" class="discussion-title">{{ discussion.dtitle }}</h3>
          <p @click="goToDiscussionDetail(discussion.dno)" class="discussion-content">{{ discussion.dinfo }}</p>
          <div class="discussion-meta">
            <span class="author">{{ discussion.ownerNo }}</span>
            <span class="post-time">发表于：{{ formatDate(discussion.postTime) }}</span>
          </div>
          <p v-if="discussion.havePic" class="has-image">此帖有图片</p>

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

          <div class="action-buttons">
            <button @click="deleteDiscussion(discussion.dno)" class="delete-btn">删除</button>
            <button @click="editDiscussion(discussion)" class="edit-btn">编辑</button>
            <button @click="postFavorite(discussion)" class="favorite-btn">
              {{ discussion.is_favourited ? '取消收藏' : '加入收藏' }}
            </button>
            <button class="zan-btn">赞</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑讨论弹出窗口 -->
    <div v-if="isEditing" class="modal">
      <div class="modal-content">
        <h3>编辑讨论</h3>
        <form @submit.prevent="updateDiscussion">
          <div class="form-group">
            <label for="title">标题:</label>
            <input type="text" v-model="editingDiscussion.dtitle" required />
          </div>
          <div class="form-group">
            <label for="content">正文:</label>
            <textarea v-model="editingDiscussion.dinfo" required></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="submit-btn">提交</button>
            <button type="button" @click="cancelEdit" class="cancel-btn">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 发起讨论功能 -->
    <div class="new-discussion">
      <h3>发帖</h3>
      <form @submit.prevent="submitPost">
        <div class="form-group">
          <label for="title">标题:</label>
          <input type="text" v-model="title" required />
        </div>
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
        <button type="submit" class="submit-btn">提交帖子</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import OSS from 'ali-oss';

const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';

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
  data() {
    return {
      BUCKET_URL,
      discussions: [], // 所有讨论
      filteredDiscussions: [], // 经过过滤的讨论列表
      loading: true,
      searchQuery: '', // 搜索关键字

      title: '',
      content: '',
      selectedFiles: [],
      imagePreviews: [],
      ossClient: null,

      isEditing: false,
      editingDiscussion:{},
      selectedImage:null,
      courseNo: this.$route.params.courseNo,
    };
  },
  created() {
    this.initOSSClient();
    this.fetchDiscussions();
  },
  methods: {
    // 获取讨论数据
    async fetchDiscussions() {
      const API_URL = `http://localhost:8000/chatRoom/${this.courseNo}/discussion`
      try {
        const response = await instance.get(API_URL);
        if (response.data.code === 200) {
          this.discussions = response.data.data;
          this.filteredDiscussions = this.discussions; // 初始化时不进行过滤
        } else {
          console.error('获取讨论失败', response.data);
        }
      } catch (error) {
        console.error('请求失败', error);
      } finally {
        this.loading = false;
      }
    },

    // 格式化日期
    formatDate(dateString) {
      const options = {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'};
      return new Date(dateString).toLocaleDateString('zh-CN', options);
    },

    // 根据搜索查询过滤讨论内容
    filterDiscussions() {
      const query = this.searchQuery.toLowerCase();
      this.filteredDiscussions = this.discussions.filter(discussion =>
          discussion.dtitle.toLowerCase().includes(query) ||
          discussion.dinfo.toLowerCase().includes(query)
      );
    },

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
      const API_URL = `http://localhost:8000/chatRoom/${this.courseNo}/discussion`
      if (!this.title || !this.content) {
        alert('请填写标题和正文！');
        return;
      }

      const uploadedImages = await this.uploadImages();

      // 提交帖子数据
      const postData = {
        title: this.title,
        content: this.content,
        images: uploadedImages,
      };

      try {
        // 使用 axios 提交数据到后端接口
        const response = await instance.post(API_URL, postData);
        console.log('帖子提交响应:', response.data);
        alert('帖子提交成功！');
        await this.fetchDiscussions();
      } catch (error) {
        console.error('帖子提交失败:', error);
        alert('帖子提交失败，请重试！');
      }

      // 清空表单
      this.title = '';
      this.content = '';
      this.selectedFiles = [];
      this.imagePreviews = [];
    },


    // 删除讨论
    async deleteDiscussion(dno) {
      const API_URL = `http://localhost:8000/chatRoom/${this.courseNo}/discussion`
      if (confirm('确定要删除该讨论吗？')) { // 确认提示
        try {
          const response = await instance.delete(`${API_URL}/${dno}`); // 使用 dno 进行删除请求
          if (response.data.code === 200) {
            // 删除成功，重新获取讨论列表
            alert('讨论已删除');
            this.fetchDiscussions(); // 重新加载讨论列表
          } else {
            console.error('删除失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
    },

    // 编辑讨论
    editDiscussion(discussion) {
      this.editingDiscussion = { ...discussion }; // 深拷贝讨论数据
      this.isEditing = true; // 设置为编辑状态
      this.imagePreviews = []; // 清空预览
    },

    // 更新讨论
    async updateDiscussion() {
      const API_URL = `http://localhost:8000/chatRoom/${this.courseNo}/discussion`
      if (confirm('确定要保存更改吗？')) {
        try {
          const response = await instance.put(`${API_URL}/${this.editingDiscussion.dno}`, {
            dtitle: this.editingDiscussion.dtitle,
            dinfo: this.editingDiscussion.dinfo
          });

          if (response.data.code === 200) {
            alert('讨论已更新');
            await this.fetchDiscussions(); // 重新加载讨论列表
            this.cancelEdit(); // 取消编辑状态
          } else {
            console.error('编辑失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
    },

    // 取消编辑
    cancelEdit() {
      this.isEditing = false; // 退出编辑状态
      this.editingDiscussion = {}; // 清空编辑内容
      this.imagePreviews = []; // 清空预览
    },


    // 跳转到讨论详情页
    goToDiscussionDetail(dno) {
      this.$router.push({name: 'Review', params: {dno}});
    },

    //对收藏进行操作
    async postFavorite(discussion){
      const API_URL = `http://localhost:8000/homepage/favorite/${discussion.dno}`
      const hit = discussion.is_favourited ? '确定要取消收藏' : '确定要加入收藏';
      const hit2 = discussion.is_favourited ? '取消收藏成功' : '加入收藏成功';
     if (confirm(hit)) { // 确认提示
        try {
          const response = await instance.post(API_URL); // 使用 dno 进行删除请求
          if (response.data.code === 200) {
            // 删除成功，重新获取讨论列表
            alert(hit2);
            await this.fetchDiscussions();
          } else {
            console.error('添加收藏失败失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
  },
  },


};
</script>

<style scoped>
.discussion-board {
  font-family: Arial, sans-serif;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f5f5;
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

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
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

.discussion-title {
  font-size: 18px;
  color: #2c3e50;
  margin-bottom: 10px;
  cursor: pointer;
}

.discussion-content {
  color: #34495e;
  margin-bottom: 10px;
  cursor: pointer;
}

.discussion-meta {
  font-size: 14px;
  color: #7f8c8d;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.has-image {
  color: #3498db;
  font-size: 14px;
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

.edit-btn {
  background-color: #f39c12;
  color: white;
}

.favorite-btn {
  background-color: #2ecc71;
  color: white;
}

.action-buttons button:hover {
  opacity: 0.8;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.submit-btn,
.cancel-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  background-color: #3498db;
  color: white;
}

.cancel-btn {
  background-color: #95a5a6;
  color: white;
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

.image-preview {
  margin-top: 15px;
}

.image-preview h4 {
  margin-bottom: 10px;
}
</style>
