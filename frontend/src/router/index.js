import {createWebHistory, createRouter} from "vue-router";
import TeacherHome from "@/views/TeacherHome.vue";
import StudentHome from "@/views/StudentHome.vue";
import LoginPage from "@/views/LoginPage.vue";
import CoursePage from "@/views/CoursePage.vue";
import DiscussionBoard from "@/views/DiscussionBoard.vue";
import Review from "@/components/Review.vue"
import PdfViewer from "@/components/PdfViewer.vue"
import CoursePageTeacher from "@/views/CoursePageTeacher.vue";
import DiscussionStu from "@/views/DiscussionStu.vue";
import PersonalHome from "@/views/PersonalHome.vue";


const routes = [
    {
        path:'/',
        redirect: '/login',
    },
    {
        path: "/teacher",
        name: "TeacherHome",
        component: TeacherHome,
    },
    {
        path: "/student",
        name: "StudentHome",
        component: StudentHome,
    },
    {
        path: "/login",
        name: "LoginPage",
        component: LoginPage
    },
    {
      path:"/student/course/:courseNo",
      name:"CoursePage",
      component: CoursePage
    },
    {
      path:"/teacher/course/:courseNo",
      name:"CoursePageTeacher",
      component: CoursePageTeacher
    },
    {
      path:"/teacher/course/:courseNo/discussion/",
      name:"DiscussionBoard",
      component: DiscussionBoard
    },
    {
      path:"/student/course/:courseNo/discussion/",
      name:"DiscussionStu",
      component: DiscussionStu
    },
    {
      path:"/teacher/course/:courseNo/discussion/:dno",
      name:"Review",
      component: Review
    },
    {
      path:"/student/course/0001/outline",
      name:"PdfViewer",
      component: PdfViewer
    },
    {
      path:"/home",
      name:"PersonalHome",
      component: PersonalHome
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!localStorage.getItem('token')) {
        next('/login')
      } else {
        next()
      }
    } else {
      next()
    }
  })

export default router;