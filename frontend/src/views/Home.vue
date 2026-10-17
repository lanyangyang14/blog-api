<template>
  <div class="layout">
    <el-container>
      <el-header class="header">
        <div class="logo">My Blog</div>
        <div class="actions">
          <el-button type="success" plain icon="User" @click="$router.push('/profile')" style="margin-right: 15px;">
            我的文章
          </el-button>
          <el-button type="primary" icon="Edit" @click="$router.push('/create')" style="margin-right: 15px;">
            写文章
          </el-button>
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="main-content">
        <!-- 搜索和操作区 -->
        <div class="toolbar">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文章标题或内容..."
            style="width: 300px; margin-right: 10px;"
            @keyup.enter="handleSearch"
            clearable
            @clear="handleSearch"
          >
            <template #append>
              <el-button icon="Search" @click="handleSearch" />
            </template>
          </el-input>

          <!-- 分类过滤 -->
          <el-select
            v-model="categoryId"
            placeholder="按分类过滤"
            clearable
            style="width: 150px; margin-right: 10px;"
            @change="handleSearch"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>

          <!-- 标签过滤 -->
          <el-select
            v-model="tagId"
            placeholder="按标签过滤"
            clearable
            style="width: 150px;"
            @change="handleSearch"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </div>

        <!-- 文章列表 -->
        <div v-loading="loading">
          <el-empty v-if="posts.length === 0" description="暂无文章" />

          <el-row :gutter="20">
            <el-col :span="8" v-for="post in posts" :key="post.id" style="margin-bottom: 20px;">
              <el-card shadow="hover" class="post-card" @click="goToDetail(post.slug)">
                <h3 class="post-title">{{ post.title }}</h3>
                <p class="post-summary">{{ post.summary || '暂无摘要' }}</p>
                <div class="post-meta">
                  <span>{{ post.author?.username || '匿名' }}</span>
                  <span>{{ formatDate(post.created_at) }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="total > 0">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="pageSize"
            v-model:current-page="currentPage"
            @current-change="handlePageChange"
          />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPosts } from '../api/post'
import { getCategories } from '../api/category'
import { getTags } from '../api/tag'

const router = useRouter()

// 列表数据
const posts = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(9)
const loading = ref(false)

// 搜索和过滤状态
const searchQuery = ref('')
const categories = ref([])
const tags = ref([])
const categoryId = ref(null)
const tagId = ref(null)

// 获取过滤条件（分类和标签）
const fetchFilters = async () => {
  try {
    const catRes = await getCategories()
    categories.value = catRes || []

    const tagRes = await getTags()
    tags.value = tagRes || []
  } catch (error) {
    console.error('获取过滤数据失败', error)
  }
}

// 获取文章列表
const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await getPosts({
      page: currentPage.value,
      size: pageSize.value,
      q: searchQuery.value || undefined,
      status: 'published',
      category_id: categoryId.value || undefined,
      tag_id: tagId.value || undefined
    })
    posts.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取文章列表失败', error)
  } finally {
    loading.value = false
  }
}

// 搜索/过滤触发
const handleSearch = () => {
  currentPage.value = 1
  fetchPosts()
}

// 分页切换
const handlePageChange = (page) => {
  currentPage.value = page
  fetchPosts()
}

const goToDetail = (slug) => {
  router.push(`/post/${slug}`)
}

const handleLogout = () => {
  localStorage.removeItem('token')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const formatDate = (isoString) => {
  return new Date(isoString).toLocaleDateString()
}

onMounted(() => {
  fetchPosts()
  fetchFilters() // 加载下拉框数据
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-bottom: 1px solid #eee;
  padding: 0 40px;
}
.logo {
  font-size: 22px;
  font-weight: bold;
  color: #409EFF;
}
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 10px; /* 让下拉框之间有间距 */
}
.post-card {
  cursor: pointer;
  height: 180px;
  display: flex;
  flex-direction: column;
}
.post-card:hover .post-title {
  color: #409EFF;
}
.post-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  transition: color 0.3s;
}
.post-summary {
  color: #606266;
  font-size: 14px;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  word-break: break-all;
}
.post-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
}
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
