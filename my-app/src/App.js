// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './Register';
import Login from './Login';
import StudentHomePage from './StudentHomePage';
import TeacherHomePage from './TeacherHomePage';
import PrivateRoute from './PrivateRoute'; // 导入私有路由组件

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/login" element={<Login />} />
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
            </Routes>
        </Router>
    );
};

export default App;