<template>
  <div class="discussion-board">
    <div class="container">
      <!-- 搜索功能 -->
      <div class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索讨论标题或内容"
        />
        <button @click="filterDiscussions">查找</button>
      </div>

      <!-- 显示加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 如果没有讨论 -->
      <div v-else-if="paginatedDiscussions.length === 0" class="no-discussions">
        暂无讨论帖子。
      </div>

      <!-- 显示讨论列表 -->
      <div v-else class="discussion-list">
        <div v-for="discussion in paginatedDiscussions" :key="discussion.dno" class="discussion-item">
          <span class="author" @click="goToUser(discussion.ownerNo)">{{ discussion.ownerName }}</span>
          <h3 @click="goToDiscussionDetail(discussion.dno)" class="discussion-title">{{ discussion.dtitle }}</h3>
          <p @click="goToDiscussionDetail(discussion.dno)" class="discussion-content">{{ discussion.dinfo }}</p>
          <div class="discussion-meta">
            <span class="post-time">发表于：{{ formatDate(discussion.postTime) }}</span>
            <span class="like_num">点赞数：{{ discussion.like }}</span>
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

            <button @click="likeDiscussion(discussion)" class="favorite-btn">
              {{ discussion.is_liked ? '取消点赞' : '点赞' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 分页控件 -->
      <div class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
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
  name: 'DiscussionBoard',
  props: {
    courseNo: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const router = useRouter();
    const discussions = ref([]);
    const filteredDiscussions = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const title = ref('');
    const content = ref('');
    const selectedFiles = ref([]);
    const imagePreviews = ref([]);
    const ossClient = ref(null);
    const isEditing = ref(false);
    const editingDiscussion = ref({});
    const currentPage = ref(1);
    const itemsPerPage = 3;

    const initOSSClient = () => {
      ossClient.value = new OSS({
        region: 'oss-cn-beijing',
        accessKeyId: 'LTAI5tAtNfQg5VqN22gT3Tsn',
        accessKeySecret: 'Mqha28ubnHLtRlZaaDhXiqz6O9Xnwf',
        bucket: 'edu-platform-2024',
      });
    };

    const fetchDiscussions = async () => {
      const API_URL = `http://localhost:8000/chatRoom/${props.courseNo}/discussion`;
      try {
        const response = await instance.get(API_URL);
        if (response.data.code === 200) {
          discussions.value = response.data.data;
          filteredDiscussions.value = discussions.value;
        } else {
          console.error('获取讨论失败', response.data);
        }
      } catch (error) {
        console.error('请求失败', error);
      } finally {
        loading.value = false;
      }
    };

    const filterDiscussions = async () => {
      if (!searchQuery.value.trim()) {
        filteredDiscussions.value = discussions.value;
        return;
      }

      loading.value = true;
      const API_URL = `http://localhost:8000/chatRoom/${props.courseNo}/discussion/filtered`;
      
      try {
        const response = await instance.post(API_URL, {
          keyword: searchQuery.value.trim()
        });

        if (response.data.code === 200) {
          filteredDiscussions.value = response.data.data;
          currentPage.value = 1; // Reset to first page after filtering
        } else {
          console.error('过滤讨论失败', response.data);
          alert('过滤讨论失败，请重试');
        }
      } catch (error) {
        console.error('请求失败', error);
        alert('请求失败，请重试');
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString) => {
      const options = {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'};
      return new Date(dateString).toLocaleDateString('zh-CN', options);
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      if (files.length + selectedFiles.value.length > 9) {
        alert('最多只能上传9张图片！');
        return;
      }

      selectedFiles.value = [...selectedFiles.value, ...files];
      imagePreviews.value = selectedFiles.value.map(file => URL.createObjectURL(file));
    };

    const uploadImages = async () => {
      const uploadedImageUrls = [];

      for (const file of selectedFiles.value) {
        const fileName = `course/pic/${Date.now()}_${file.name}`;
        try {
          const result = await ossClient.value.put(fileName, file);
          uploadedImageUrls.push(result.url);
        } catch (error) {
          console.error('上传失败:', error);
        }
      }
      return uploadedImageUrls;
    };

    const submitPost = async () => {
      const API_URL = `http://localhost:8000/chatRoom/${props.courseNo}/discussion`;
      if (!title.value || !content.value) {
        alert('请填写标题和正文！');
        return;
      }

      const uploadedImages = await uploadImages();

      const postData = {
        title: title.value,
        content: content.value,
        images: uploadedImages,
      };

      try {
        const response = await instance.post(API_URL, postData);
        console.log('帖子提交响应:', response.data);
        alert('帖子提交成功！');
        await fetchDiscussions();
      } catch (error) {
        console.error('帖子提交失败:', error);
        alert('帖子提交失败，请重试！');
      }

      title.value = '';
      content.value = '';
      selectedFiles.value = [];
      imagePreviews.value = [];
    };

    const deleteDiscussion = async (dno) => {
      const API_URL = `http://localhost:8000/chatRoom/${props.courseNo}/discussion`;
      if (confirm('确定要删除该讨论吗？')) {
        try {
          const response = await instance.delete(`${API_URL}/${dno}`);
          if (response.data.code === 200) {
            alert('讨论已删除');
            await fetchDiscussions();
          } else {
            console.error('删除失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
    };

    const editDiscussion = (discussion) => {
      editingDiscussion.value = { ...discussion };
      isEditing.value = true;
      imagePreviews.value = [];
    };

    const updateDiscussion = async () => {
      const API_URL = `http://localhost:8000/chatRoom/${props.courseNo}/discussion`;
      if (confirm('确定要保存更改吗？')) {
        try {
          const response = await instance.put(`${API_URL}/${editingDiscussion.value.dno}`, {
            dtitle: editingDiscussion.value.dtitle,
            dinfo: editingDiscussion.value.dinfo
          });

          if (response.data.code === 200) {
            alert('讨论已更新');
            await fetchDiscussions();
            cancelEdit();
          } else {
            console.error('编辑失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
    };

    const cancelEdit = () => {
      isEditing.value = false;
      editingDiscussion.value = {};
      imagePreviews.value = [];
    };

    const goToDiscussionDetail = (dno) => {
      router.push(`/course/${props.courseNo}/discussion/${dno}`);
    };

    const postFavorite = async (discussion) => {
      const API_URL = `http://localhost:8000/homepage/favorite/${discussion.dno}`;
      const hit = discussion.is_favourited ? '确定要取消收藏' : '确定要加入收藏';
      const hit2 = discussion.is_favourited ? '取消收藏成功' : '加入收藏成功';
      if (confirm(hit)) {
        try {
          const response = await instance.post(API_URL);
          if (response.data.code === 200) {
            alert(hit2);
            await fetchDiscussions();
          } else {
            console.error('添加收藏失败', response.data);
          }
        } catch (error) {
          console.error('请求失败', error);
        }
      }
    };

    const likeDiscussion = async (discussion) => {
      const API_URL = `http://localhost:8000/chatRoom/DiscussionLike/${discussion.dno}`
      try {
        const response = await instance.post(API_URL);
        if (response.status === 200) {
          alert(discussion.is_liked ? '取消点赞成功' : '点赞成功');
          await fetchDiscussions();
        }
      } catch (err) {
        console.error('请求失败', err);
      }
    };

    const paginatedDiscussions = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return filteredDiscussions.value.slice(start, end);
    });

    const totalPages = computed(() => Math.ceil(filteredDiscussions.value.length / itemsPerPage));

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    const goToUser = (userNo) => {
      router.push(`/user/${userNo}`);
    }

    onMounted(() => {
      initOSSClient();
      fetchDiscussions();
    });

    return {
      BUCKET_URL,
      paginatedDiscussions,
      loading,
      searchQuery,
      title,
      content,
      selectedFiles,
      imagePreviews,
      isEditing,
      editingDiscussion,
      currentPage,
      totalPages,
      filterDiscussions,
      formatDate,
      handleFileUpload,
      submitPost,
      deleteDiscussion,
      editDiscussion,
      updateDiscussion,
      cancelEdit,
      goToDiscussionDetail,
      postFavorite,
      likeDiscussion,
      prevPage,
      nextPage,
      goToUser,
    };
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

.author:hover {
  color: #4769ff; 
  font-weight: bold; 
  cursor: pointer;  
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

.zan-btn {
  background-color: #3498db;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}

.pagination button {
  padding: 5px 10px;
  margin: 0 5px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.pagination span {
  margin: 0 10px;
}
</style>