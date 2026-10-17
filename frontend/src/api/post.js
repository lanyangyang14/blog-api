import request from './request'

export const getPosts = (params) => {
  return request.get('/posts', { params })
}

export const getPostDetail = (slug) => {
  return request.get(`/posts/${slug}`)
}

export const createPost = (data) => {
  return request.post('/posts', data)
}
// 点赞 / 取消点赞
export const likePost = (postId) => {
  return request.post(`/posts/${postId}/like`)
}

export const unlikePost = (postId) => {
  return request.delete(`/posts/${postId}/like`)
}

// 获取点赞状态
export const getLikeStatus = (postId) => {
  return request.get(`/posts/${postId}/like`)
}

// 删除文章（仅作者或管理员可用）
export const deletePost = (postId) => {
  return request.delete(`/posts/${postId}`)
}
