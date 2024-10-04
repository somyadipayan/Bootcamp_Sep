<template>
    <NavBar />
    <div class="container mt-5">
        <h2>Login</h2>
        <form @submit.prevent="login">
            <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input v-model="email" type="email" class="form-control" id="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" id="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
export default {
    components: {
        NavBar
    }, 
    name: "LoginPage",
    data() {
        return {
            email: '',
            password: ''
        }
    },
    methods: {
        async login() {
            const response = await fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: this.email,
                    password: this.password
                })
                
            })
            const data = await response.json()
            console.log(data)
            if (!response.ok) {
                alert(data.error)
            }
            else {
                alert(data.message)
                // storing an item in local storage
                localStorage.setItem('access_token', data.access_token)
                // const token = localStorage.getItem('token')
                // console.log(token)
                this.$router.push('/')
            }
        }
    }
}

</script>