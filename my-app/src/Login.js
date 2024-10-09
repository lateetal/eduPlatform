import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/login/api/token/', {
                username,
                password,
            });

            const token = response.data.access; // 获取token
            localStorage.setItem('token', token); // 存储token

            // 设置Axios默认请求头
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

            const userType = response.data.userType;
            // 跳转
            if (userType === 'student') {
                navigate('/student');
            } else if (userType === 'teacher') {
                navigate('/teacher');
            }

        } catch (error) {
            setMessage('Invalid credentials');
        }
    };

    return (
        <div>
            <h2>用户登录</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>学号/工号:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>密码:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">登录</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
};

export default Login;