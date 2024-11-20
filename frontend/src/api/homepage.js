import request from '@/utils/request.js'

const API_URL='http://localhost:8000/homepage';

export const getUsernameService = () => {
    return request.get(`${API_URL}/getusername/`)
}

export const assignmentListService = (courseNo) => {
    return request.get(`${API_URL}/course/${courseNo}/assignments/`)
}

export const assignmentAddService = (courseNo,assignmentData) => {
    return request.post(`${API_URL}/course/${courseNo}/create_assignment/`,assignmentData)
}

export const assignmentDeleteService = (courseNo,assignmentId) => {
    return request.delete(`${API_URL}/course/${courseNo}/create_assignment/`,{
        data:{
            assignment_id:assignmentId
        }
    })
}

export const assignmentUpdateService = (courseNo,assignmentData) => {
    return request.put(`${API_URL}/course/${courseNo}/create_assignment/`,assignmentData)
}

export const pptListService = (courseNo) => {
    return request.get(`${API_URL}/course/${courseNo}/resources_folder`);
}

export const fileUploadService = (courseNo, fileData) => {
    return request.post(`${API_URL}/course/${courseNo}/resources_file`,fileData);
}

export const fileDeleteService = (courseNo, rno) => {
    return request.delete(`${API_URL}/course/${courseNo}/resources_file`,{
        data:{
            rno:rno
        }
    })
}

export const subfolderAddService = (courseNo,folderData) => {
    return request.post(`${API_URL}/course/${courseNo}/resources_folder`,folderData);
}

export const subfolderDeleteService = (courseNo,folderId) => {
    return request.delete(`${API_URL}/course/${courseNo}/resources_folder`,{
        data:{
            folderId:folderId
        }
    })
}