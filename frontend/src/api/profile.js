import request from '../utils/request'

export const getProfileMe = () =>
  request({
    url: '/profile/me',
    method: 'get',
  })

export const getProfileStats = () =>
  request({
    url: '/profile/stats',
    method: 'get',
  })
