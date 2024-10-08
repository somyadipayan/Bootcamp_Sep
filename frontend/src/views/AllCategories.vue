<template>
    <NavBar />
    <div class="container mt-5">
    <h1>All Categories</h1>
    <table class="table">
        <thead>
            <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Catalogue</th>
                <th v-if="role === 'admin'" scope="col">Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="category in categories" :key="category.id">
                <th scope="row">{{ category.id }}</th>
                <td>{{ category.name }}</td>
                <td><a :href="'http://127.0.0.1:5000/view-catalogue/' + category.id" target="_blank">{{ category.pdf }}</a></td>
                <td v-if="role === 'admin'" class="btn-group">
                    <button type="button" class="btn btn-light" @click="editCategory(category.id)">Edit</button>
                    <router-link type="button" class="btn btn-dark" to="/">View Products</router-link>
                    <router-link type="button" class="btn btn-dark" :to="`/add-product/${category.id}`">Add Products</router-link>
                    <button type="button" class="btn btn-light" @click="deleteCategory(category.id)">Delete</button>
                </td>
            </tr>
        </tbody>
    </table>
    <router-link v-if="role === 'admin'"  to="/create-category" class="btn btn-dark">Create Category</router-link>
    </div>
    <!-- <p> Just for testing purpose </p>
    <embed class="pdf mt-5" src="http://127.0.0.1:5000/view-catalogue/5#toolbar=0" height="1000px" width="100%" type="application/pdf"> -->
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import userMixin from '@/mixins/userMixin';
export default {
    name: 'AllCategories',
    mixins: [userMixin],
    components: {
        NavBar
    },
    data() {
        return {
            categories: [],
        }
    },
    async mounted() {
        await this.getCategories()
    },
    methods: {
        editCategory(id) {
            this.$router.push(`/update-category/${id}`)
        },
        async deleteCategory(id) {
            const response = await fetch(`http://127.0.0.1:5000/category/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                }
            })
            const data = await response.json()

            if (!response.ok) {
                alert(data.error)
            } else {
                alert(data.message)
                this.getCategories()
            }
        },
        async getCategories() {
            const response = await fetch('http://127.0.0.1:5000/categories', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            }) 

            const data = await response.json()

            if (!response.ok) {
                alert(data.error)
            } else {
                console.log("fETCHED     ", data)
                this.categories = data.categories
            }

        }
    }
}
</script>