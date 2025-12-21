import request from './request'

export function getHealthAssessment(data) {
  return request({
    url: '/ai/health-assessment',
    method: 'post',
    data
  })
}

export function getPrediction(data) {
  return request({
    url: '/ai/prediction',
    method: 'post',
    data
  })
}

