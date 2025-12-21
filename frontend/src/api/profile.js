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

