import request from './request'

export function getSettings() {
  return request({
    url: '/settings',
    method: 'get'
  })
}

export function saveSettings(settings) {
  return request({
    url: '/settings',
    method: 'post',
    data: settings
  })
}

export function uploadBackgroundImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/settings/background-image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getBackgroundImageUrl() {
  return request({
    url: '/settings',
    method: 'get'
  })
}
