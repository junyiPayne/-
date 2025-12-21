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
