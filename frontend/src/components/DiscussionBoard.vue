<template>
  <div class="discussion-board">
    <h2>讨论区</h2>

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
<!--学生界面可以拿来复用 根据token确定是学生还是老师，展示对应的选项按钮 -->
<!--老师可以删除任意人发的讨论 学生只能删除自己发布的讨论-->
<!--编辑只能编辑自己发布的，老师应该没有权限去编辑别人的吧-->
<!--教师应该也能收藏？ 不知道也许吧-->
        <button @click="deleteDiscussion(discussion.dno)">删除</button> <!-- 添加删除按钮 -->
        <button @click="editDiscussion(discussion)">编辑</button> <!-- 添加编辑按钮 -->
        <button >加入收藏</button> <!-- 添加收藏按钮 -->

        <hr />
      </div>
    </div>
     <!-- 编辑讨论表单 -->
    <div v-if="isEditing">

<!--这一段的编辑逻辑应该是弹出窗口，或者是跳转到新界面，交给你去改了-->
      <h3>编辑讨论</h3>
      <form @submit.prevent="updateDiscussion">
        <div>
          <label for="edit-title">标题</label>
          <input type="text" id="edit-title" v-model="editingDiscussion.dtitle" required />
        </div>
        <div>
          <label for="edit-content">正文</label>
          <textarea id="edit-content" v-model="editingDiscussion.dinfo" required></textarea>
        </div>
        <button type="submit">保存</button>
        <button @click="cancelEdit">取消</button>
      </form>
    </div>

    <!-- 发起讨论功能 -->
    <div class="new-discussion">
    <h3>发起新讨论</h3>
    <form @submit.prevent="createDiscussion">
      <div>
        <label for="title">标题</label>
        <input type="text" id="title" v-model="newDiscussion.title" required />
      </div>
      <div>
        <label for="content">正文</label>
        <textarea id="content" v-model="newDiscussion.content" required></textarea>
      </div>
      <div>
        <label for="image">上传图片</label>
        <input type="file" id="image" @change="handleFileUpload" accept="image/*" />
      </div>
      <button type="submit">提交</button>
    </form>
  </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_URL = 'http://localhost:8000/chatRoom/0001/discussion';

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
      discussions: [], // 所有讨论
      filteredDiscussions: [], // 经过过滤的讨论列表
      loading: true,
      searchQuery: '', // 搜索关键字
      newDiscussion: {
        title: '',
        content: '',
        havePic:''
      },
      isEditing: false,
      editingDiscussion:{},
      selectedImage:null,
    };
  },
  created() {
    this.fetchDiscussions();
  },
  methods: {
    // 获取讨论数据
    async fetchDiscussions() {
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
      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
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

    handleFileUpload(event) {
      // 获取选择的文件
      this.selectedImage = event.target.files[0];
    },

    // 发起新讨论
    async createDiscussion() {
      if (!this.newDiscussion.title || !this.newDiscussion.content) {
        alert('标题和正文不能为空');
        return;
      }

      // 创建 FormData 对象
      const formData = new FormData();
      formData.append('dtitle', this.newDiscussion.title);
      formData.append('dinfo', this.newDiscussion.content);

      // 如果有选择的图片，则添加到 FormData
      if (this.selectedImage) {
        formData.append('image', this.selectedImage); // 假设后端字段名为 'image'
      }

      try {
        const response = await axios.post('API_URL', formData, {
          headers: {
            'Content-Type': 'multipart/form-data', // 指定内容类型为多部分表单
          },
        });

        if (response.data.code === 200) {
          // 新讨论成功，重置表单并重新获取讨论数据
          alert('讨论已提交');
          this.newDiscussion.title = '';
          this.newDiscussion.content = '';
          this.selectedImage = null; // 重置图片选择
          this.fetchDiscussions(); // 重新加载讨论列表
        } else {
          console.error('讨论提交失败', response.data);
        }
      } catch (error) {
        console.error('请求失败', error);
      }
    },
  },

    // 删除讨论
    async deleteDiscussion(dno) {
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
    },

    // 更新讨论
    async updateDiscussion() {
      if (confirm('确定要保存更改吗？')) {
        try {
          const response = await instance.put(`${API_URL}/${this.editingDiscussion.dno}`, {
            dtitle: this.editingDiscussion.dtitle,
            dinfo: this.editingDiscussion.dinfo
          });

          if (response.data.code === 200) {
            alert('讨论已更新');
            this.fetchDiscussions(); // 重新加载讨论列表
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
    },

    // 跳转到讨论详情页
    goToDiscussionDetail(dno) {
      this.$router.push({ name: 'Review', params: { dno } });
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
