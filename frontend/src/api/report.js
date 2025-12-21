import request from './request'

export function submitReport() {
  return request({
    url: '/reports/submit',
    method: 'post'
  })
}

export function previewReport() {
  return request({
    url: '/reports/preview',
    method: 'get',
    responseType: 'blob'
  })
}

export function getReports(userId = null, includeHistory = false) {
  const params = {}
  if (userId) {
    params.user_id = userId
  }
  if (includeHistory) {
    params.include_history = 'true'
  }
  return request({
    url: '/reports/list',
    method: 'get',
    params
  })
}

export function viewReport(reportId) {
  return request({
    url: `/reports/view/${reportId}`,
    method: 'get',
    responseType: 'blob'
  })
}

