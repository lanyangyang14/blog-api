<template>
  <div class="profile-container">
    <el-page-header @back="$router.push('/')" title="返回首页" style="margin-bottom: 20px;" />

    <el-card>
      <h2 style="margin-top: 0;">我的文章</h2>

      <el-table :data="myPosts" style="width: 100%" v-loading="loading" empty-text="你还没有发布过文章">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'published' ? 'success' : 'info'">
              {{ scope.row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="200">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button size="small" @click="$router.push(`/post/${scope.row.slug}`)">查看</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPosts, deletePost } from '../api/post'

const myPosts = ref([])
const loading = ref(false)

// ⚠️ 这里为了简单，我们使用后端返回的 ID 过滤。
// 真实项目中，你应该有一个 /api/v1/users/me/posts 的接口
// 但后端的 list_posts 支持按 author_id 过滤
const fetchMyPosts = async () => {
  loading.value = true
  try {
    // 从 Token 中解析出当前用户 ID（或者后端有专门的 /auth/me 接口）
    // 简单起见，我们假设后端的 /posts 接口支持传 author_id 过滤
    // 这里需要你先获取当前用户信息。为了不写太复杂，我们先拉取所有文章，在前端过滤
    // （后续可以优化为后端过滤）

    // 1. 获取当前用户信息 (通过 token)
    const token = localStorage.getItem('token')
    // 其实 JWT 的 payload 里就有 sub (user_id)，我们可以直接解析，或者调 /auth/me
    // 但为了代码最简，这里先调接口拿所有文章，然后让用户看所有的。
    // 更好的做法：调 /auth/me 拿到 id，然后传 author_id

    // 临时方案：直接拉取所有文章（包括草稿），前端根据当前登录用户过滤（需要知道自己的 ID）
    // 我们这里再写一个简单的方法获取当前用户ID：
    const meRes = await request.get('/auth/me')
    const userId = meRes.id

    const res = await getPosts({ size: 100, author_id: userId })
    myPosts.value = res.items
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 需要引入 request
import request from '../api/request'

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇文章吗？', '警告', { type: 'warning' })
    await deletePost(id)
    ElMessage.success('删除成功')
    fetchMyPosts() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      // 错误被拦截器处理了
    }
  }
}

onMounted(() => {
  fetchMyPosts()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}
</style>
