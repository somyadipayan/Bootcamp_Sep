<template>
    <div class="container mt-5">
        <h2>Create Product in {{ this.category.name }}</h2>
        <form @submit.prevent="add_product">
            <div class="mb-3">
                <label for="name" class="form-label">Name</label>
                <input v-model="product.name" type="text" class="form-control" required>
                <label for="unit" class="form-label">Unit</label>
                <input v-model="product.unit" type="text" class="form-control" required>
                <label for="price" class="form-label">Price</label>
                <input v-model="product.price" type="number" class="form-control" required>
                <label for="quantity" class="form-label">Quantity</label>
                <input v-model="product.quantity" type="number" class="form-control" required>

            </div>

            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
export default {
    name: 'CreateProduct',
    data() {
        return {
            category : {},
            product : {
                name: '',
                unit: '',
                price: '',
                quantity: '',
                category_id: ''
            }
        }
    },
    created() {
        this.product.category_id = this.$route.params.id
        this.getcategory(this.$route.params.id)
    },
    methods: {
        async add_product() {
            const response = await fetch('http://127.0.0.1:5000/product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(this.product)
            })
            const data = await response.json()
            console.log(data)
            if (!response.ok) {
                alert(data.error)
            }
            else {
                alert(data.message)
                this.$router.push('/categories')
            }
        },
        async getcategory(id) {
            const response = await fetch(`http://127.0.0.1:5000/category/${id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
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

    }
}
</script>