<template>
  <div class="post-create-container">
    <el-page-header @back="goBack" title="返回" style="margin-bottom: 20px;" />

    <el-card>
      <h2 style="margin-top: 0;">写文章</h2>

      <el-form :model="form" label-width="80px">
        <el-form-item label="文章标题" required>
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>

        <el-form-item label="URL标识" required>
          <el-input v-model="form.slug" placeholder="例如：my-first-post（只能包含字母、数字、中划线）" />
        </el-form-item>

        <el-form-item label="文章摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="选填，不填会自动截取" />
        </el-form-item>

        <el-form-item label="文章内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="15"
            placeholder="支持 Markdown 语法..."
          />
        </el-form-item>

        <el-form-item label="发布状态">
          <el-radio-group v-model="form.status">
            <el-radio label="published">直接发布</el-radio>
            <el-radio label="draft">保存草稿</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">提交</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createPost } from '../api/post'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  title: '',
  slug: '',
  summary: '',
  content: '',
  status: 'published'
})

const handleSubmit = async () => {
  if (!form.title || !form.slug || !form.content) {
    return ElMessage.warning('标题、URL标识、内容为必填项')
  }

  loading.value = true
  try {
    await createPost(form)
    ElMessage.success('发布成功')
    router.push('/')
  } catch (error) {
    // 错误已被 Axios 拦截器统一处理
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.post-create-container {
  max-width: 1000px;
  margin: 20px auto;
}
</style>
