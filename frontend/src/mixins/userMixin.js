export default {
  data() {
    return {
      user: null,
      role: null,
      isLoggedin: false,
    };
  },
  async created() {
    await this.checkAuth();
  },
  methods: {
    async checkAuth(){
        const access_token = localStorage.getItem("access_token");
        if (!access_token) {
          this.isLoggedin = false;
          this.user = null;
          this.role = null;
          return;
        }
          try {
            this.user = await this.getUserDetails();
            console.log(this.user)
 
          } catch (error) {
            console.log(error);
          }       
    },
    async getUserDetails() {
      const response = await fetch("http://127.0.0.1:5000/getuserdata", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("access_token"),
        },
      });
      const data = await response.json();
      if (!response.ok) {
        console.log(data.error);
        return null;
      } else {
        console.log(data.message);
        this.isLoggedin = true;
        this.role = data.user.role;
        return data.user;
      }
    },
    async logout() {
      const response = await fetch("http://127.0.0.1:5000/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("access_token"),
        },
      })
      const data = await response.json();
      if (!response.ok) {
        alert(data.error);
      }
      else{
        alert(data.message);
        localStorage.removeItem("access_token");
        this.isLoggedin = false;
        this.user = null;
        this.role = null;
        this.$router.push("/login");
      }

    },
  },
};
