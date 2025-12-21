import request from './request'

export function getBusinessDataList(params) {
  return request({
    url: '/business/data',
    method: 'get',
    params
  })
}

export function getBusinessData(id) {
  return request({
    url: `/business/data/${id}`,
    method: 'get'
  })
}

export function createBusinessData(data) {
  return request({
    url: '/business/data',
    method: 'post',
    data
  })
}

export function updateBusinessData(id, data) {
  return request({
    url: `/business/data/${id}`,
    method: 'put',
    data
  })
}

export function deleteBusinessData(id) {
  return request({
    url: `/business/data/${id}`,
    method: 'delete'
  })
}

export function getStatistics() {
  return request({
    url: '/business/statistics',
    method: 'get'
  })
}

