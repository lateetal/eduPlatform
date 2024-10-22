<template>
  <div class="discussion-detail">
    <h2>{{ discussion.dtitle }}</h2>
    <p>{{ discussion.dinfo }}</p>
    <p>作者：{{ discussion.ownerNo }}</p>
    <p>发表于：{{ formatDate(discussion.postTime) }}</p>
    <p v-if="discussion.havePic">此帖有图片</p>

    <!-- 显示评论列表 -->
    <div v-if="discussion.reviews && discussion.reviews.length > 0">
      <h3>评论</h3>
      <div v-for="comment in discussion.reviews" :key="comment.rno">
        <p>{{ comment.ownerNo }}: {{ comment.rinfo }}</p>
        <p>发表于：{{ formatDate(comment.postTime) }}</p>
        <p>点赞数：{{ comment.likeNum }}</p>
      </div>
    </div>

    <!-- 回复框 -->
    <div>
      <textarea v-model="newComment" placeholder="发表评论"></textarea>
      <button @click="submitComment">提交评论</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading">加载中...</div>
    <div v-if="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'ReviewComponent',
  data() {
    return {
      discussion: {}, // 存储讨论详情
      newComment: '',  // 新评论内容
      loading: false,  // 加载状态
      error: null      // 错误信息
    };
  },
  created() {
    const dno = this.$route.params.dno; // 从路由参数中获取讨论ID
    this.fetchDiscussionDetail(dno); // 获取讨论详情
  },
  methods: {
    async fetchDiscussionDetail(dno) {
      this.loading = true; // 开始加载
      this.error = null;   // 清除之前的错误
      try {
        const response = await fetch(`http://localhost:8000/chatRoom/0001/discussion/${dno}/review`);
        if (!response.ok) {
          throw new Error(`网络错误: ${response.statusText}`);
        }
        const data = await response.json();
        this.discussion = data.data; // 更新讨论数据，假设后端返回的数据格式符合预期
      } catch (err) {
        this.error = `获取讨论详情失败: ${err.message}`; // 捕获并显示错误信息
      } finally {
        this.loading = false; // 加载结束
      }
    },
    formatDate(date) {
      // 格式化时间，示例：将日期格式化为 YYYY-MM-DD
      const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      };
      return new Date(date).toLocaleString(undefined, options); // 使用本地字符串格式化日期
    },
    submitComment() {
      // 提交评论的逻辑
      console.log(this.newComment); // 在控制台输出评论内容
      // 这里可以添加 AJAX 请求提交评论
      // 例如：
      // const response = await fetch(`http://localhost:8000/chatRoom/0001/discussion/${this.discussion.dno}/review`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({ rinfo: this.newComment, ownerNo: yourOwnerNo }) // 替换 yourOwnerNo 为实际用户 ID
      // });
      // const result = await response.json();
      // // 处理返回结果...
    }
  }
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
