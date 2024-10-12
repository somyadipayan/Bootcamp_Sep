<template>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <h4>Order History Report</h4>
            </div>
        </div>
        <div v-if="report" class="row mt-4">
            <div class="col-md-12">
                <div class="row">
                    <p class="card col-md-4">Total Orders: {{ report.total_orders }}</p>
                    <p class="card col-md-4">Total Amount: Rs.{{ report.total_amount }}</p>
                    <p class="card col-md-4">Total Items: {{ report.total_items }}</p>
                </div>
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h5>Orders per Day</h5>
                        <img :src="'http://localhost:5000/order-history-report-graph'" alt="Orders per Day"
                            class="img-fluid">
                    </div>
                    <div class="col-md-6">
                        <h5>Orders from diff Categories</h5>
                        <img :src="'http://localhost:5000/order-category-pie-chart'" alt="Orders per Day"
                            class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
        <a href="http://localhost:5000/download-order-csv" class="btn btn-dark mt-4">Download Report</a>
    </div>
</template>

<script>
export default {
    data() {
        return {
            report: null
        };
    },
    mounted() {
        this.fetchReport();
    },
    methods: {
        async fetchReport() {
            const response = await fetch('http://localhost:5000/order-history-report', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                this.report = data;
            } else {
                console.error('Failed to fetch report');
            }
        }
    }
};
</script>

<style scoped>

</style>