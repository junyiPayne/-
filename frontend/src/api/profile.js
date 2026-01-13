import request from './request'

export function getProfile() {
  return request({
    url: '/profile',
    method: 'get'
  })
}

export function createProfile(data) {
  return request({
    url: '/profile',
    method: 'post',
    data
  })
}

export function updateProfile(data) {
  return request({
    url: '/profile',
    method: 'put',
    data
  })
}

export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/profile/avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
