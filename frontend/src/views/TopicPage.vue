<template>
    <div class="topic-board">
        <div class="title-container">
            <h2 class="title">{{ topicTitle }}</h2>
            <button class="btn btn-ghost" @click="goBack">
                <el-icon><ArrowLeft /></el-icon>
                返回
            </button>
        </div>

        <!-- 显示讨论列表 -->
        <div v-if="discussions.length===0">
            暂无讨论
        </div>

        <div v-else class="discussion-list">
            <div v-for="discussion in discussions" :key="discussion.dno" class="discussion-item">
                <span class="author" @click="goToUser(discussion.ownerName)">{{ discussion.ownerName }}</span>
                <h3 @click="goToDiscussionDetail(discussion.dno)" class="discussion-title" v-html="highlightHashtags(discussion.dtitle)"></h3>
                <p @click="goToDiscussionDetail(discussion.dno)" class="discussion-content" v-html="highlightHashtags(discussion.dinfo)"></p>
                
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
                    <button @click="folderDialog(discussion)" class="favorite-btn">
                        {{discussion.is_favorited ? '已收藏':'收藏'}}
                    </button>

                    <button @click="likeDiscussion(discussion)" class="favorite-btn">
                        {{ discussion.is_liked ? '取消点赞' : '点赞' }}
                    </button>
                </div>

            </div>
        </div>



    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTopicService } from '@/api/chatroom.js'

const route = useRoute();
const router = useRouter();
const courseNo = route.params.courseNo;
const topicTitle = route.params.topicTitle;
const discussions = ref([]);

const goBack = () => {
    router.go(-1);
}

const fetchTopic = async() => {
    let result = await getTopicService(courseNo,{
        params:{
            topic:topicTitle
        }  
    });
    discussions.value = result.data;
}

fetchTopic();

const highlightHashtags = (text) => {
    if (typeof text !== 'string' || !text) {
        return ''; 
    }
    return text.replace(/#(\S+)(\s|$)/g, '<span class="hashtag" data-hashtag="$1">$&</span>');
}

const formatDate = (dateString) => {
    const options = {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'};
    return new Date(dateString).toLocaleDateString('zh-CN', options);
}

</script>

<style>
.topic-board {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title-container {
  display: flex;
  justify-content: space-between;
  align-items: center; 
}

.title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.btn {
  background-color: transparent;
  border: 1px solid #333;
  padding: 8px 16px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.btn-ghost:hover {
  background-color: #f0f0f0;
}
</style>