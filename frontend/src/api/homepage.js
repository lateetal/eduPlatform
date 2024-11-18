import request from '@/utils/request.js'

export const getUsernameService = ()=>{
    return request.get('http://localhost:8000/homepage/getusername/')
}