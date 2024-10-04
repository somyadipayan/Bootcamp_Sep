<template>
<nav class="navbar navbar-expand-lg bg-body-tertiary sticky-top">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Grocery Store</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarText" aria-controls="navbarText" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarText">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <router-link class="nav-link" to="/">Home</router-link>
        </li>
        <div class="navbar-nav me-auto mb-2 mb-lg-0" v-if="!this.isLoggedin">
        <li class="nav-item">
          <router-link class="nav-link" to="/login">Login</router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/register">Register</router-link>
        </li>
        </div>
        <div v-else>
        <li class="nav-item">
          <a class="nav-link" @click="logout">Logout</a>
        </li>
        </div>
      </ul>
    </div>
  </div>
</nav>
</template>

<script>
import userMixin from '@/mixins/userMixin';
export default {
  name: 'NavBar',
  mixins: [userMixin],
}
</script>