<template>
    <div class="smart-course-platform">
      <header class="header">
        <h1>学生主页</h1>
        <div class="user-info">
          <img src="@/assets/avatar.jpg" alt="avatar" class="avatar" />
          <span>{{ username }} (学生)</span>
          <button class="btn btn-ghost" @click="goHome">
              <el-icon><School /></el-icon>
              课程主页
          </button>
          <button class="btn btn-ghost" @click="logout" >
            <el-icon  ><TopRight /></el-icon>
            安全退出
          </button>
        </div>
      </header>
      <main>
        <aside>
          <h2>个人信息</h2>
          <ul>
            <li>修改密码</li>
            <li>通知</li>
          </ul>
        </aside>
        <section class="profile-info">
          <div class="info-grid">
            <div>
              <label>姓名：</label>
              <span>{{ studentName }}</span>
            </div>
            <div>
              <label>学号：</label>
              <span>{{ studentId }}</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue'
  import {School, TopRight } from '@element-plus/icons-vue';
  
  
  export default{
      components:{School,TopRight},
      setup(){
          const studentName = ref('乔子轩')
          const studentId = ref('22301018')
  
          const logout = () => {
              // localStorage.removeItem('token');
              this.$router.push('/login')
          };
  
          return{
              studentName,
              studentId,
              logout,
          }
      },
  
      
  };
  </script>
  
  <style scoped>
  .smart-course-platform {
    font-family: Arial, sans-serif;
    color: #333;
  }
  
  .header {
    background-color: #2563eb;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .avatar {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    font-weight: 600;
  }
  
  .btn-ghost {
    background-color: transparent;
    color: white;
  }
  
  main {
    display: flex;
    padding: 2rem;
  }
  
  aside {
    width: 200px;
    background-color: #f0f0f0;
    padding: 1rem;
  }
  
  aside ul {
    list-style-type: none;
    padding: 0;
  }
  
  aside li {
    margin-bottom: 0.5rem;
  }
  
  .profile-info {
    flex-grow: 1;
    margin-left: 2rem;
    display: flex;
    justify-content: space-between;
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: auto auto;
    gap: 1rem;
  }
  
  .avatar-section {
    text-align: center;
  }
  
  .avatar-placeholder {
    width: 130px;
    height: 130px;
    background-color: #ddd;
    border-radius: 50%;
    margin-bottom: 1rem;
  }
  
  button {
    background-color: #4a69bd;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    cursor: pointer;
  }
  
  p {
    font-size: 0.8rem;
    color: #666;
  }
  </style>