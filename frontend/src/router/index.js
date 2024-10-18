import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCategory from '@/views/CreateCategory.vue'
import AllCategories from '@/views/AllCategories.vue'
import UpdateCategory from '@/views/UpdateCategory.vue'
import CreateProduct from '@/views/CreateProduct.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import { checkUserRole } from '@/utils/checkRole'

async function checkAdmin(to, from, next) {
  const userRole = await checkUserRole();
  if (userRole !== 'admin') {
    alert("You don't have permission to access this page");
    next({ name: 'login' });
  } else {
    next();
  }
}


async function checkManager(to, from, next) {
  const userRole = await checkUserRole();
  if (userRole !== 'manager') {
    alert("You don't have permission to access this page");
    next({ name: 'login' });
  } else {
    next();
  }
}


const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage
  },
  {
    path: '/categories',
    name: 'categories',
    component: AllCategories
  },
  {
    path: '/create-category',
    name: 'createcategory',
    component: CreateCategory
  },
  {
    path: '/admin-dashboard',
    name: 'admindashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true },
    beforeEnter: checkAdmin,
  },
  {
    path: '/update-category/:id',
    name: 'updatecategory',
    component: UpdateCategory
  },
  {
    path: '/add-product/:id',
    name: 'createproduct',
    component: CreateProduct
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
