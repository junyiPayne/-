import request from './request'

export function getClassrooms() {
  return request({
    url: '/classrooms',
    method: 'get'
  })
}

export function getAvailableClassrooms() {
  return request({
    url: '/classrooms/available',
    method: 'get'
  })
}

export function createClassroom(data) {
  return request({
    url: '/classrooms',
    method: 'post',
    data
  })
}

export function updateClassroom(id, data) {
  return request({
    url: `/classrooms/${id}`,
    method: 'put',
    data
  })
}

export function deleteClassroom(id) {
  return request({
    url: `/classrooms/${id}`,
    method: 'delete'
  })
}

export function getClassroomUsers(classroomId) {
  return request({
    url: `/classrooms/${classroomId}/users`,
    method: 'get'
  })
}
