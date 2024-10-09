import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {useNavigate} from "react-router-dom";
import './StudentHomePage.css'

const API_URL = 'http://localhost:8000/homepage/student/';
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';
const USERNAME_URL = 'http://localhost:8000/homepage/getusername/';

export default function BasicTable() {
    const [subjects, setSubjects] = useState([]); // 存储科目
    const [username,setUsername] = useState('');
    const [loading, setLoading] = useState(true); // 加载状态
    const [error, setError] = useState(null); // 错误状态
    const navigate = useNavigate();

    useEffect(() => {
        const fetchSubjects = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(API_URL, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                console.log('Fetched subjects:', response.data); // 调试输出

                if (response.data.code === 200) {
                    setSubjects(response.data.data || []);
                } else {
                    setError('获取科目失败');
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

    const fetchUsername = async () =>{
        try{
            const response = await axios.get(USERNAME_URL)
            if (response.status === 200){
                setUsername(response.data.username);
            } else {
                setError('获取用户名失败');
            }

        } catch (err) {
            setError(err.message);
        }

    }
        fetchSubjects();
        fetchUsername();
    }, []);

    const handleCourseClick = (courseNo) => {
      navigate(`/student/course/${courseNo}/`)
    };

    if (loading) {
        return <div>加载中...</div>;
    }

    if (error) {
        return <div>发生错误: {error}</div>;
    }

    return (
        <div>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"/>
            <h1>学生主页</h1>
            <h2>欢迎, {username} !</h2>

            {subjects.length > 0 ? (
                <div className="courseList">
                    {subjects.map((subject, index) => (
                        <div
                            className="courseItem"
                            key={index}
                        >
                            <img
                                className="courseImg"
                                src={`${BUCKET_URL}${subject.picAddr}`}
                                alt={subject.cname}
                            />
                            <div className="courseInfo">
                                <div className="courseInfoItem">
                                    <img
                                        className="courseImg"
                                        src="http://123.121.147.7:88/ve/back/coursePlatform/index/newPage/courseName.png"
                                        alt=""
                                    />
                                    <p className="course-text" title={subject.cname}>{subject.cname}</p>
                                </div>
                                <div className="courseInfoItem">
                                    <img
                                        className="courseImg"
                                        src="http://123.121.147.7:88/ve/back/coursePlatform/index/newPage/courseCode.png"
                                        alt=""
                                    />
                                    <p className="course-text" title={subject.course_no}>
                                        <span className="course-tit">课程号：</span>{subject.course_no}
                                    </p>
                                </div>
                                <div className="courseInfoItem">
                                    <img
                                        className="courseImg"
                                        src="http://123.121.147.7:88/ve/back/coursePlatform/index/newPage/courseCode.png"
                                        alt=""
                                    />
                                    <p className="course-text" title={subject.course_class}>
                                        <span className="course-tit">班级：</span>{subject.course_class}
                                    </p>
                                </div>
                                <button onClick={() => handleCourseClick(subject.cno)}>
                                    查看课程详情
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p>没有选修科目</p>
            )}
        </div>
    );
}

