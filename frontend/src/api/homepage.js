import request from '@/utils/request.js'

const API_URL='http://localhost:8000/homepage';

export const getUsernameService = () => {
    return request.get(`${API_URL}/getusername/`)
}

//作业
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

export const assignmentSearchService = (courseNo,assignmentId) => {
    return request.get(`${API_URL}/course/${courseNo}/oneAssignment/`,{
        params:{
            assignment_id:assignmentId
        }
    });
}

export const assignmentCommitService = (courseNo,assignmentId,assignmentData) => {
    return request.post(`${API_URL}/student/course/${courseNo}/assignment/${assignmentId}/submit/`,assignmentData);
}

export const committedViewService = (courseNo,assignmentId,username) => {
    return request.get(`${API_URL}/course/${courseNo}/assignment/${assignmentId}/student/${username}`)
}

export const committedListService = (courseNo) => {
    return request.get(`${API_URL}/course/${courseNo}/getAllSubmit`);
}

export const manageListService = (courseNo,assignmentId) => {
    return request.get(`${API_URL}/course/${courseNo}/assignment/${assignmentId}/`)
}

export const mutualAddService = (assignmentId) => {
    return request.post(`${API_URL}/${assignmentId}/generateMutualAssessment`);
}

export const readOverAddService = (courseNo,assignmentId,sno,readOverData) => {
    return request.post(`${API_URL}/course/${courseNo}/assignment/${assignmentId}/student/${sno}/TeacherAssignment`,readOverData)
}

export const readOverSearchService = (courseNo,assignmentId,sno) => {
    return request.get(`${API_URL}/course/${courseNo}/assignment/${assignmentId}/student/${sno}/TeacherAssignment`)
}

export const mutualListService = (assignmentId) => {
    return request.get(`${API_URL}/${assignmentId}/mutualAssessment`)
}

export const mutualCommitService = (assignmentId,mutualData) => {
    return request.post(`${API_URL}/${assignmentId}/mutualAssessment`,mutualData)
}

//课程资源
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

export const fileSearchService = (courseNo, rno) => {
    return request.get(`${API_URL}/course/${courseNo}/resources_file`,{
        params:{
            rno:rno
        }
    })
}

export const exerciseListService = (courseNo,questionType) => {
    return request.get(`${API_URL}/course/${courseNo}/resources_question/${questionType}`);
}

export const exerciseAddService = (courseNo,exerciseData) => {
    return request.post(`${API_URL}/course/${courseNo}/resources_question/`,exerciseData);
}

export const exerciseDeleteService = (courseNo,id) => {
    return request.delete(`${API_URL}/course/${courseNo}/resources_question/`,{
        data:{
            id:id
        }
    })
}

export const paperListService = (courseNo) => {
    return request.get(`${API_URL}/course/${courseNo}/resources_test/`);
}

export const paperAddService = (courseNo,paperData) => {
    return request.post(`${API_URL}/course/${courseNo}/resources_test/`,paperData);
}

export const paperDeleteService = (courseNo, rno) => {
    return request.delete(`${API_URL}/course/${courseNo}/resources_test/`,{
        data:{
            rno:rno
        }
    })
}