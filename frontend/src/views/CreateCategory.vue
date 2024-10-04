<template>
    <div class="container mt-5">
        <h2>Create Category</h2>
        <form @submit.prevent="add_category">
            <div class="mb-3">
                <label for="name" class="form-label">Category Name</label>
                <input v-model="category.name" type="text" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="pdf" class="form-label">Upload category catalogue (in pdf)</label>
                <input type="file" class="form-control" id="pdf" accept=".pdf" @change="handlefilechange" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
export default {
    name: 'CreateCategory',
    data() {
        return {
            category : {
                name: '',
                pdf: null
            }
        }
    },
    methods: {
        handlefilechange(event) {
            this.category.pdf = event.target.files[0]
        },
        async add_category() {
            const formData = new FormData()
            formData.append('pdf', this.category.pdf)
            formData.append('name', this.category.name)
            const response = await fetch('http://127.0.0.1:5000/category', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            })
            const data = await response.json()
            console.log(data)
            if (!response.ok) {
                alert(data.error)
            }
            else {
                alert(data.message)
                // this.$router.push('/')
            }
        }
    }
}
</script>