<template>
<NavBar />
    <div class="container mt-5">
        <h2>Register</h2>
        <form @submit.prevent="register">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input v-model="username" type="text" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input v-model="email" type="email" class="form-control" id="email" aria-describedby="emailHelp">
                <div id="emailHelp" class="form-text">We'll never share your email with anyone else.</div>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" id="password">
            </div>
            <div class="mb-3 form-check">
                <input v-model="isManager" type="checkbox" class="form-check-input" id="isManager">
                <label class="form-check-label" for="isManager">Want to register as Manager?</label>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>


<script>
import NavBar from '@/components/NavBar.vue'
export default {
    name: "RegisterPage",
    components: {
        NavBar
    },
    data() {
        return {
            username: '',
            email: '',
            password: '',
            isManager: false
        }
    },
    methods: {
        async register() {
            try {
                // Making an API call from frontend
                const response = await fetch('http://127.0.0.1:5000/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: this.username,
                        email: this.email,
                        password: this.password,
                        role: this.isManager ? 'manager' : 'user'
                    })
                })
                // Parsing the response JSON
                const data = await response.json()
                if (!response.ok) {
                    alert(data.error)
                }
                else {
                    alert(data.message)
                    // Push to login page
                    this.$router.push('/')
                }
            } catch (error) {
                console.log(error)
            }
        }
    }
}

</script>

<style scoped></style>