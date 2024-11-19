import request from '@/utils/request.js'

const API_URL='http://localhost:8000/homepage';

export const getUsernameService = () => {
    return request.get(`${API_URL}/getusername/`)
}

export const assignmentListService = (courseNo) => {
    return request.get(`${API_URL}/course/${courseNo}/assignments/`)
}
