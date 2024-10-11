<template>
  <NavBar />
  <div class="container mt-3">
    <h2>Welcome to store!</h2>
    <div class="form-group">
      <input 
        type="text" 
        v-model="searchQuery" 
        class="form-control" 
        placeholder="Search for products">
    </div>
    <div v-for="category in filteredCategories" :key="category.id" class="mt-3">
      <h4>{{ category.name }}</h4>
      <div class="row">
        <div v-for="product in category.products" :key="product.id" class="col-md-3 mb-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ product.name }}</h5>
              <p class="card-text">Rs.{{ product.price }}/{{ product.unit }}</p>
              <input type="number" v-model="quantities[product.id]" class="form-control mb-2" placeholder="Quantity">
              <button @click="addToCart(product.id, quantities[product.id] || 1)" class="btn btn-primary btn-block">
                Add to Cart
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';

export default {
  components: {
    NavBar
  },
  data() {
    return {
      categories: [],
      searchQuery: '',
      quantities: {}
    }
  },
  async created() {
    this.getdata()
  },
  computed: {
      filteredCategories() {
      const searchTerm = this.searchQuery.toLowerCase();
      return this.categories.map(category => {
        const filteredProducts = category.products.filter(product => 
          product.name.toLowerCase().includes(searchTerm)
        );
        return { ...category, products: filteredProducts };
      }).filter(category => category.products.length > 0);
    }
  },
  methods: {
    async getdata() {
      try {
        const response = await fetch('http://localhost:5000/products', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        if (response.ok) {
          this.categories = data;
          console.log(this.categories)
          console.log("data fetched");
        } else {
          console.log("data not fetched");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
    async addToCart(productId, quantity) {
      console.log(productId, quantity);
      try {
        const response = await fetch('http://localhost:5000/add-to-cart', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            product_id: productId,
            quantity: quantity
          })
        });
        const data = await response.json();
        if (response.ok) {
          alert(data.message);
          this.quantities = {};
        } else {
          alert(data.error);
        }
      } catch (error) {
        console.error("Error adding product to cart:", error);
      }
    }
  }
}
</script>


<style scoped></style>
