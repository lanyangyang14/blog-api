import request from './request'

// 获取文章评论树
export const getComments = (postId) => {
  return request.get(`/posts/${postId}/comments`)
}

// 发表评论
export const createComment = (postId, data) => {
  return request.post(`/posts/${postId}/comments`, data)
}
