import request from './request'

// 获取所有分类
export const getCategories = () => {
  return request.get('/categories')
}
