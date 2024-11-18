import request from '@/utils/request.js'

export const getTopicService = (courseNo,topicData) => {
    return request.get(`http://localhost:8000/chatRoom/${courseNo}/showtopic`,topicData)
}