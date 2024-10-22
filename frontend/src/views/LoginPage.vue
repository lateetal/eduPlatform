<template>
  <div class="login-container">
    <h1>智慧课程平台</h1>
    <div class="login-card">
      <div class="left-side">
        <div class="book-illustration">
          <img src="@/assets/usagi.jpg" alt="Open book with educational icons" class="book-image" />
        </div>
      </div>
      <div class="right-side">
        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="input-group">
            <UserIcon class="input-icon" />
            <input type="text" v-model="username" placeholder="请输入工号/学号" required />
          </div>
          <div class="input-group">
            <LockIcon class="input-icon" />
            <input type="password" v-model="password" placeholder="请输入密码" required />
          </div>
          <div class="input-group">
            <ShieldCheckIcon class="input-icon" />
            <input type="text" v-model="captcha" placeholder="请输入验证码" required />
            <span class="captcha">4997</span>
          </div>
          <button type="submit" class="login-btn">登录</button>
          <a href="#" class="forgot-password">忘记密码?</a>
        </form>
      </div>
    </div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
  import axios from 'axios'
  import { UserIcon, LockIcon, ShieldCheckIcon} from 'lucide-vue-next'
  
  export default {
    components:{UserIcon, LockIcon, ShieldCheckIcon},
    name: 'LoginPage',
    data() {
      return {
        username: '',
        password: '',
        message: '',
        captcha: '',
      }
    },
    methods: {
      async handleSubmit() {
        try {
          const response = await axios.post('http://localhost:8000/login/api/token/', {
            username: this.username,
            password: this.password
          })
  
          const token = response.data.access
          localStorage.setItem('token', token)
  
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

          const userType = response.data.userType
          if (userType === 'student') {
            this.$router.push('/student')
          } else if (userType === 'teacher') {
            this.$router.push('/teacher')
          }
        } catch (error) {
          this.message = 'Invalid credentials'
        }
      }
    }
  }
</script>

<style scoped>
.login-container {
  min-height: 100vh; /* 1 */
  display: flex; /* 2 */
  flex-direction: column; /* 3 */
  justify-content: flex-start; /* 4: 上对齐 */
  align-items: center; /* 5 */
  background-image: url('@/assets/bg.jpg'); /* 6 */
  background-size: cover; /* 7 */
  background-position: center; /* 8 */
  background-repeat: no-repeat; /* 9 */
  margin-top: 10%; /* 10: 向下偏移 */
}

.login-card {
  display: flex;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  width: 800px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.left-side {
  flex: 1;
  background-color: #1e90ff;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

.book-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.book-image {
  max-width: 100%;
  max-height: 100%;
}

.right-side {
  flex: 1;
  padding: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

input {
  width: 80%;
  padding: 0.5rem 0.5rem 0.5rem 2.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.captcha {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: bold;
  color: #333;
}

.login-btn {
  background-color: #1e90ff;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: #187bcd;
}

.forgot-password {
  text-align: right;
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-password:hover {
  text-decoration: underline;
}

</style>