import request from './request'

export function createBackup() {
  return request({
    url: '/admin/backup',
    method: 'post'
  })
}

export function getMaintenanceStatus() {
  return request({
    url: '/admin/maintenance',
    method: 'get'
  })
}

export function toggleMaintenance(enable) {
  return request({
    url: '/admin/maintenance',
    method: 'post',
    data: { enable }
  })
}

export function uploadSystemLogo(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/admin/system-logo',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getSystemLogoUrl() {
  return request({
    url: '/admin/system-logo',
    method: 'get'
  })
}

export function uploadBackgroundImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/admin/background-image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getBackgroundImageUrl() {
  return request({
    url: '/admin/background-image',
    method: 'get'
  })
}
