<template>
  <div class="discussion-board">
    <h2>讨论区 {{ currentPath }}</h2>

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
    <div v-if="loading">加载中...</div>

    <!-- 如果没有讨论 -->
    <div v-else-if="filteredDiscussions.length === 0">没有讨论帖子。</div>
<!--学生界面可以拿来复用 根据token确定是学生还是老师，展示对应的选项按钮 -->
<!--老师可以删除任意人发的讨论 学生只能删除自己发布的讨论-->
<!--编辑只能编辑自己发布的，老师应该没有权限去编辑别人的吧-->
<!--教师应该也能收藏？ 不知道也许吧-->
    <!-- 显示讨论列表 -->
    <div v-else>
      <div v-for="discussion in filteredDiscussions" :key="discussion.dno" class="discussion">
<!--        这里改变一下 提示用户这里能点开-->
        <h3  @click="goToDiscussionDetail(discussion.dno)">{{ discussion.dtitle }}</h3>
        <p @click="goToDiscussionDetail(discussion.dno)">{{ discussion.dinfo }}</p>
<!--        改成展示用户名-->
        <p>{{ discussion.ownerNo }}</p>
        <p>
          <small>发表于：{{ formatDate(discussion.postTime) }}</small>
        </p>
        <p v-if="discussion.havePic">此帖有图片</p>

        <!-- 展示图片 -->
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

        <button @click="deleteDiscussion(discussion.dno)">删除</button> <!-- 添加删除按钮 -->
        <button @click="editDiscussion(discussion)">编辑</button> <!-- 添加编辑按钮 -->
        <button @click="postFavorite(discussion)">
          {{ discussion.is_favourited ? '取消收藏':'加入收藏'}}
        </button> <!-- 添加收藏按钮 -->

        <hr />
      </div>
    </div>
     <!-- 编辑讨论表单 -->
    <div v-if="isEditing">

<!--这一段的编辑逻辑应该是弹出窗口，或者是跳转到新界面，交给你去改了-->
      <!-- 编辑讨论弹出窗口 -->
    <div v-if="isEditing" class="modal">
      <div class="modal-content">
        <h3>编辑讨论</h3>
        <form @submit.prevent="updateDiscussion">
          <div>
            <label for="title">标题:</label>
            <input type="text" v-model="editingDiscussion.dtitle" required />
          </div>
          <div>
            <label for="content">正文:</label>
            <textarea v-model="editingDiscussion.dinfo" required></textarea>
          </div>
<!--          <div>-->
<!--            <label for="images">上传图片:</label>-->
<!--            <input type="file" @change="handleFileUpload" multiple accept="image/*" />-->
<!--          </div>-->
<!--          <div class="image-preview">-->
<!--            <h2>预览:</h2>-->
<!--            <div v-if="imagePreviews.length">-->
<!--              <img v-for="(img, index) in imagePreviews" :key="index" :src="img" alt="Image Preview" style="max-width: 100px; margin: 5px;" />-->
<!--            </div>-->
<!--          </div>-->
          <button type="submit">提交帖子</button>
          <button type="button" @click="cancelEdit">取消</button>
        </form>
      </div>
    </div>
    </div>

    <!-- 发起讨论功能 -->
    <div class="post-form">
    <h3>发帖</h3>
    <form @submit.prevent="submitPost">
      <div>
        <label for="title">标题:</label>
        <input type="text" v-model="title" required />
      </div>
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
      <button type="submit">提交帖子</button>
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

    // // 处理文件上传
    // handleFileUpload(event) {
    //   const files = event.target.files;
    //   this.imagePreviews = Array.from(files).map(file => URL.createObjectURL(file));
    // },

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
/* 样式可以根据需要调整 */
.search-bar {
  margin-bottom: 20px;
}

.new-discussion {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.new-discussion form {
  display: flex;
  flex-direction: column;
}

.new-discussion label {
  margin-bottom: 5px;
}

.new-discussion input,
.new-discussion textarea {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.new-discussion button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.new-discussion button:hover {
  background-color: #45a049;
}
</style>
