<template>
  <NavBar />
  <div v-if="user" class="home mt-5">
      <h1>Welcome {{ this.user.username }}</h1>
  </div>
</template>

<script>
import userMixin from '@/mixins/userMixin';
import NavBar from '@/components/NavBar.vue'
export default {
  name: 'HomeView',
  components: {
    NavBar
  },
  mixins: [userMixin],
}
</script>
