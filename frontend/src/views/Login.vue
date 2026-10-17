<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 style="text-align: center; margin-bottom: 20px;">博客后台</h2>

      <el-tabs v-model="activeTab">
        <!-- 登录 -->
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" @keyup.enter="handleLogin">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-button type="primary" style="width: 100%" @click="handleLogin" :loading="loading">登 录</el-button>
          </el-form>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm">
            <el-form-item>
              <el-input v-model="registerForm.username" placeholder="用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.email" placeholder="邮箱" prefix-icon="Message" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-button type="success" style="width: 100%" @click="handleRegister" :loading="loading">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../api/request.js'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '' })

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) return ElMessage.warning('请填写完整')
  loading.value = true
  try {
    // 使用 /auth/login/json 接口
    const res = await request.post('/auth/login/json', loginForm)
    localStorage.setItem('token', res.access_token)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    // 错误在拦截器统一处理了
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    return ElMessage.warning('请填写完整')
  }
  loading.value = true
  try {
    await request.post('/auth/register', registerForm)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
  } catch (error) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  border-radius: 8px;
}
</style>
