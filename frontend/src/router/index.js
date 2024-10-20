import {createWebHistory, createRouter} from "vue-router";
import TeacherHome from "@/views/TeacherHome.vue";
import StudentHome from "@/views/StudentHome.vue";
import LoginPage from "@/views/LoginPage.vue";
import CoursePage from "@/views/CoursePage.vue";


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