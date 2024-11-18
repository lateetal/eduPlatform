import {createWebHistory, createRouter} from "vue-router";
import TeacherHome from "@/views/TeacherHome.vue";
import StudentHome from "@/views/StudentHome.vue";
import LoginPage from "@/views/LoginPage.vue";
import CoursePage from "@/views/CoursePage.vue";
import Review from "@/components/Review.vue"
import PersonalHome from "@/views/PersonalHome.vue";
import UserView from "@/views/UserView.vue";
import TopicPage from "@/views/TopicPage.vue";


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
      path:"/course/:courseNo",
      name:"CoursePage",
      component: CoursePage
    },
    {
      path:"/course/:courseNo/discussion/:dno",
      name:"Review",
      component: Review
    },
    {
      path:"/home",
      name:"PersonalHome",
      component: PersonalHome
    },
    {
      path:"/user/:userId",
      name:"UserView",
      component:UserView
    },
    {
      path:"/:courseNo/showtopic/:topicTitle",
      name:"TopicPage",
      component:TopicPage,
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