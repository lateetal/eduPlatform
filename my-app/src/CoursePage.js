import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import { Document, Page, pdfjs} from 'react-pdf';
import './coursePage.css';
import './PdfViewer.css';
import PdfViewer from './PdfViewer.jsx';


// import '@/styles/report.less';
// import pdfPath from '@/lib/demo.pdf';


const API_URL = 'http://localhost:8000/homepage/student/';
const BUCKET_URL = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com';

const CoursePage = () => {

    const { courseNo } = useParams();
    const [courseData, setCourseData] = useState(null);
    const [selectedTab, setSelectedTab] = useState('introduction');
    const [pdfUrl, setPdfUrl] = useState(null);
    const [filePath, setFilePath] = useState(null);

    useEffect(() => {
        // pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
        // pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
        pdfjs.GlobalWorkerOptions.workerSrc = `/pdf.worker.mjs`;

        const fetchCourseData = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get(`${API_URL}course/${courseNo}/`, {
                    headers: { Authorization: `Bearer ${token}` },
                    maxRedirects: 0,
                });
                if (response.status === 200) {
                    // console.log('Fetched data:', response.data);
                    setCourseData(response.data);
                    setPdfUrl(`${BUCKET_URL}${courseData.data.coutline}`);
                    console.log(pdfUrl)

                    // //  // 在这里调用 getData
                    // await getData(); // 确保在数据获取后调用
                }
            } catch (error) {
                console.error('Error fetching course data:', error);
            }
        };


        fetchCourseData();
        getData();
    }, [courseNo]);

    /* 获取报告文件流数据 */
        const getData = async () => {
    // 阿里云 OSS 存储的 PDF 文件的 URL
    const ossPdfUrl = 'https://edu-platform-2024.oss-cn-beijing.aliyuncs.com/course/outline/0001-outline.pdf';

    try {
        // 使用 Axios 发送 GET 请求到阿里云 OSS
        const res = await axios.get(ossPdfUrl, { responseType: 'blob' });

        // 创建一个 Blob 对象，包含从OSS返回的数据
        const blob = new Blob([res.data], { type: res.headers["content-type"] || 'application/pdf' });

        // 获取浏览器支持的 URL 对象
        const url = window.URL.createObjectURL(blob);

        // 调用 setFilePath 函数，将生成的 URL 传递给它
        setFilePath(url);
    } catch (error) {
        console.error('Error fetching PDF from OSS:', error);
    }
};

    if (!courseData) {
        return <div>加载中...</div>;
    }


    const renderContent = () => {
        switch (selectedTab) {
            case 'introduction':
                return (
                    <div>
                        <h3>课程信息</h3>
                        <p>课程名: {courseData.data.cname}</p>
                        <p>课程编号: {courseData.data.course_no}</p>
                        <p>课序号: {courseData.data.course_class}</p>
                        <p>课程介绍: {courseData.data.cintro}</p>
                    </div>
                );
            case 'teacher':
                return (
                    <div>
                        <h3>教师信息</h3>
                        <p>姓名: {courseData.data.teacher.tname}</p>
                        <p>邮箱地址: {courseData.data.teacher.tmail}</p>
                        <p>办公室: {courseData.data.teacher.toffice}</p>
                        <p>联系方式: {courseData.data.teacher.tphone}</p>
                        <p>教师介绍: {courseData.data.teacher.tintro}</p>
                    </div>
                );
            case 'outline':

                return (
                    <div className="page-fjhScreenReport">
                        <div className="con-wrapper">
                            <PdfViewer filePath={filePath}/>
                        </div>
                    </div>
                );
            case 'resources':
                return (
                    <div>
                        <h3>课程资源</h3>
                        <ul>
                            {courseData.resources.map((resource, index) => (
                                <li key={index}>
                                    <a href={resource.url} target="_blank" rel="noopener noreferrer">
                                        {resource.title}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>
                );
            case 'discussion':
                return (
                    <div>
                        <h3>讨论区</h3>
                        {/* 在这里可以添加讨论区的实现 */}
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="course-page">
            <div className="sidebar">
                <h2>课程导航</h2>
                <ul>
                    <li onClick={() => setSelectedTab('introduction')}>课程介绍</li>
                    <li onClick={() => setSelectedTab('teacher')}>教师信息</li>
                    <li onClick={() => setSelectedTab('outline')}>课程大纲</li>
                    <li onClick={() => setSelectedTab('resources')}>课程资源</li>
                    <li onClick={() => setSelectedTab('discussion')}>讨论区</li>
                </ul>
            </div>
            <div className="content">
                {renderContent()}
            </div>
        </div>
    );
};

export default CoursePage;