import request from './request'

export function getDailyLogs(params) {
  return request({
    url: '/daily-log',
    method: 'get',
    params
  })
}

export function getDailyLog(date) {
  return request({
    url: `/daily-log/${date}`,
    method: 'get'
  })
}

export function createOrUpdateLog(data) {
  return request({
    url: '/daily-log',
    method: 'post',
    data
  })
}

export function getStatistics(params) {
  return request({
    url: '/daily-log/statistics',
    method: 'get',
    params
  })
}

