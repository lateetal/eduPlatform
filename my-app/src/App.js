// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './Register';
import Login from './Login';
import StudentHomePage from './StudentHomePage';
import TeacherHomePage from './TeacherHomePage';
import PrivateRoute from './PrivateRoute'; // 导入私有路由组件
import CoursePage from './CoursePage';


const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Login />} />

                {/*下面是添加登录保护的写法*/}
                <Route
                    path="/student"
                    element={
                        <PrivateRoute>
                            <StudentHomePage />
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/teacher"
                    element={
                        <PrivateRoute>
                            <TeacherHomePage />
                        </PrivateRoute>
                    }
                />


                <Route path="/student/course/:courseNo" element={<CoursePage />} />
            </Routes>
        </Router>
    );
};

export default App;