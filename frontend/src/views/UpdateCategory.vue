<template>
    <div class="container mt-5">
        <h2>Create Category</h2>
        <form @submit.prevent="update_category">
            <div class="mb-3">
                <label for="name" class="form-label">Category Name</label>
                <input v-model="category.name" type="text" class="form-control" id="username">
            </div>
            <div class="mb-3">
                <label for="pdf" class="form-label">Upload category catalogue (in pdf)</label>
                <input type="file" class="form-control" id="pdf" accept=".pdf" @change="handlefilechange" aria-describedby="pdfHelp">
                <div id="pdfHelp" class="form-text">Current pdf: {{ category.pdf }}</div>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
export default {
    name: 'UpdateCategory',
    data() {
        return {
            category: {
                name: '',
                pdf: '',
            }
        }
    },
    async mounted() {
        const id = this.$route.params.id;
        this.getcategory(id);
    },
    methods: {
        handlefilechange(event) {
            const file = event.target.files[0];
            this.category.pdf = file;
        },
        async update_category() {
            const id = this.$route.params.id;
            const formData = new FormData();
            formData.append('pdf', this.category.pdf);
            formData.append('name', this.category.name);
            const response = await fetch(`http://127.0.0.1:5000/category/${id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            });
            const data = await response.json();
            console.log(data);
            if (!response.ok) {
                alert(data.error);
            } else {
                alert(data.message);
                this.$router.push('/categories');
            }
        },
        async getcategory(id) {
            const response = await fetch(`http://127.0.0.1:5000/category/${id}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            const data = await response.json();
            console.log(data);
            if (!response.ok) {
                alert(data.error);
            } else {
                this.category = data.category;
            }
        }
    },
}
</script>    