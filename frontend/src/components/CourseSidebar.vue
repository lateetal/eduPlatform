<template>
    <el-aside width="250px" class="sidebar">
        <el-menu
          :default-active="selectedTab"
          class="sidebar-menu"
          @select="handleSelect"
        >
            <el-sub-menu index="1">
                <template #title>
                    <el-icon><Location /></el-icon>
                    <span>课程信息</span>
                </template>
                <el-menu-item index="introduction">课程介绍</el-menu-item>
                <el-menu-item index="outline">教学大纲</el-menu-item>
                <el-menu-item index="calendar">教学日历</el-menu-item>
                <el-menu-item index="professor">教师信息</el-menu-item>
                <el-menu-item index="student">选课学生</el-menu-item>
            </el-sub-menu>

          <el-sub-menu index="2">
            <template #title>
              <el-icon><Folder /></el-icon>
              <span>课程资源</span>
            </template>
            <el-menu-item index="ppts">课件</el-menu-item>
            <el-menu-item index="papers">历年试题库</el-menu-item>
            <el-menu-item index="exercises">习题库</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="3">
            <template #title>
              <el-icon><DataBoard /></el-icon>
              <span>课程考核</span>
            </template>
            <el-menu-item index="homework">作业</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="4">
            <template #title>
              <el-icon><ChatDotRound /></el-icon>
              <span>答疑讨论</span>
            </template>
            <el-menu-item index="discussion">讨论区</el-menu-item>
            <el-menu-item index="AIhelper">AI问答</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="5">
            <template #title>
              <el-icon><Bell /></el-icon>
              <span>课程通知</span>
            </template>
            <el-menu-item index="notice">通知</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
  </template>
  
<script>
import { Location, Folder, ChatDotRound, DataBoard, Bell } from '@element-plus/icons-vue';
  
  export default {
    components: { 
        Location, 
        Folder, 
        ChatDotRound, 
        DataBoard, 
        Bell
    },
    props: ['selectedTab'],
    emits: ['select-tab'],
    setup(props, { emit }) {
      const handleSelect = (key) => {
        emit('select-tab', key);
      };
  
      return { handleSelect };
    },
  };
  </script>
  
  <style scoped>
  .sidebar {
    background-color: #fff;
    padding: 20px;
    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
  }
  </style>