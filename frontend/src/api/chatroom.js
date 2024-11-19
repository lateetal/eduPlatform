import request from '@/utils/request.js'

const API_URL = 'http://localhost:8000/chatRoom'

export const TopicListService = (courseNo,topicData) => {
    return request.get(`${API_URL}/${courseNo}/showtopic`,topicData)
}

export const FolderListService = () => {
    return request.get(`${API_URL}/all/folder/0`)
}

export const FolderAddDiscussionService = (fno, discussionData) => {
    return request.post(`${API_URL}/folder/${fno}`,discussionData)
}

export const DiscussionAddLikeService = (dno) => {
    return request.post(`${API_URL}/DiscussionLike/${dno}`)
}