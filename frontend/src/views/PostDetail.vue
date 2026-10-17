<template>
  <div class="post-detail-container" v-loading="loading">
    <el-page-header @back="goBack" title="返回" style="margin-bottom: 20px;" />

    <el-card v-if="post">
      <h1 class="title">{{ post.title }}</h1>
      <div class="meta">
        <span>作者: {{ post.author?.username || '匿名' }}</span>
        <span>发布于: {{ formatDate(post.created_at) }}</span>
        <span>浏览: {{ post.view_count }}</span>
      </div>

      <!-- 点赞按钮，增加安全访问符 ?. -->
      <div class="like-section">
        <el-button
          :type="likeStatus?.is_liked ? 'danger' : 'default'"
          round
          @click="toggleLike"
        >
          <el-icon style="margin-right: 5px;"><Star /></el-icon>
          {{ likeStatus?.is_liked ? '已赞' : '点赞' }} ({{ likeStatus?.like_count || 0 }})
        </el-button>
      </div>

      <el-divider />

      <div class="markdown-body" v-html="renderedContent"></div>
    </el-card>

    <el-card v-if="post" style="margin-top: 20px;">
      <h3>评论 ({{ commentCount }})</h3>

      <div class="comment-editor">
        <el-input v-model="newComment" type="textarea" :rows="3" placeholder="说点什么吧..." />
        <el-button type="primary" style="margin-top: 10px;" @click="handleComment">发表评论</el-button>
      </div>

      <el-divider />

      <el-empty v-if="comments.length === 0" description="还没有评论，快来抢沙发吧~" />

      <div class="comment-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <span class="username">{{ comment.author?.username || '匿名' }}</span>
            <span class="time">{{ formatDate(comment.created_at) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>

          <div v-if="comment.replies?.length > 0" class="reply-list">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <span class="username">{{ reply.author?.username || '匿名' }}</span>：
              <span>{{ reply.content }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPostDetail, getLikeStatus, likePost, unlikePost } from '../api/post'
import { getComments, createComment } from '../api/comment'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(false)

const likeStatus = ref({ is_liked: false, like_count: 0 })
const comments = ref([])
const newComment = ref('')

const commentCount = computed(() => {
  let count = comments.value.length
  comments.value.forEach(c => {
    if (c.replies) count += c.replies.length
  })
  return count
})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

const renderedContent = computed(() => {
  if (!post.value || !post.value.content) return ''
  return md.render(post.value.content)
})

// 核心修复：把所有的请求拆开，不要让一个报错卡死整体
const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getPostDetail(route.params.slug)
    post.value = res

    // 拉取评论和点赞，用 try-catch 包起来，防止报错导致 loading 卡死
    try {
      const commentsRes = await getComments(res.id)
      comments.value = commentsRes
    } catch (e) {
      console.error('评论获取失败', e)
    }

    try {
      const likeRes = await getLikeStatus(res.id)
      likeStatus.value = likeRes || { is_liked: false, like_count: 0 }
    } catch (e) {
      console.error('点赞状态获取失败', e)
    }

  } catch (error) {
    ElMessage.error('文章不存在或已被删除')
    router.push('/')
  } finally {
    loading.value = false // 无论前面报什么错，一定会在这里关掉转圈
  }
}

const toggleLike = async () => {
  if (!post.value) return
  try {
    if (likeStatus.value.is_liked) {
      await unlikePost(post.value.id)
      likeStatus.value.is_liked = false
      likeStatus.value.like_count -= 1
    } else {
      await likePost(post.value.id)
      likeStatus.value.is_liked = true
      likeStatus.value.like_count += 1
    }
  } catch (error) {}
}

const handleComment = async () => {
  if (!newComment.value.trim()) return ElMessage.warning('请输入评论内容')
  if (!post.value) return
  try {
    await createComment(post.value.id, { content: newComment.value })
    ElMessage.success('评论发表成功')
    newComment.value = ''
    const commentsRes = await getComments(post.value.id)
    comments.value = commentsRes
  } catch (error) {}
}

const goBack = () => { router.back() }
const formatDate = (isoString) => new Date(isoString).toLocaleString()

onMounted(() => { fetchDetail() })
</script>

<style scoped>
.post-detail-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}
.title { text-align: center; margin-bottom: 10px; }
.meta { text-align: center; color: #909399; font-size: 14px; }
.meta span { margin: 0 10px; }
.like-section { text-align: center; margin-top: 20px; }
.markdown-body { line-height: 1.8; font-size: 16px; color: #333; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 20px; }
.markdown-body :deep(pre) { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
.comment-editor { margin-bottom: 20px; }
.comment-item { padding: 15px 0; border-bottom: 1px solid #f0f0f0; }
.comment-header { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 14px; }
.comment-header .username { font-weight: bold; color: #409EFF; }
.comment-header .time { color: #999; }
.comment-content { font-size: 15px; line-height: 1.5; color: #333; }
.reply-list { background-color: #f9f9f9; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 14px; }
.reply-item { margin-bottom: 5px; }
.reply-item .username { color: #409EFF; }
</style>
