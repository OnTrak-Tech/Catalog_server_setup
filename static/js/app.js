// E-Commerce Catalog Vue Application
new Vue({
    el: '#app',
    data: {
        // Authentication
        isAuthenticated: false,
        token: '',
        username: '',
        showLoginForm: false,
        loginForm: {
            username: '',
            password: ''
        },
        loginError: '',
        
        // Products
        products: [],
        loading: true,
        
        // Add Product Form
        showAddProductForm: false,
        newProduct: {
            name: '',
            description: '',
            price: ''
        },
        productImage: null,
        imagePreview: null
    },
    created() {
        // Check if user is already logged in (token in localStorage)
        const token = localStorage.getItem('token');
        if (token) {
            this.token = token;
            this.username = localStorage.getItem('username');
            this.isAuthenticated = true;
            this.setupAxiosInterceptors();
        }
        
        // Load products on page load
        this.fetchProducts();
    },
    methods: {
        // Authentication methods
        login() {
            this.loginError = '';
            console.log('Attempting login with:', this.loginForm.username);
            
            axios.post('/login', this.loginForm, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => {
                    console.log('Login successful:', response.data);
                    this.token = response.data.access_token;
                    this.username = this.loginForm.username;
                    this.isAuthenticated = true;
                    
                    // Save to localStorage
                    localStorage.setItem('token', this.token);
                    localStorage.setItem('username', this.username);
                    
                    // Setup axios interceptors for JWT
                    this.setupAxiosInterceptors();
                    
                    // Reset form and close modal
                    this.loginForm.username = '';
                    this.loginForm.password = '';
                    this.showLoginForm = false;
                })
                .catch(error => {
                    console.error('Login failed:', error);
                    this.loginError = error.response?.data?.msg || 'Login failed. Please try again.';
                });
        },
        logout() {
            this.isAuthenticated = false;
            this.token = '';
            this.username = '';
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            this.showAddProductForm = false;
        },
        setupAxiosInterceptors() {
            // Remove any existing interceptors
            axios.interceptors.request.eject(this.interceptor);
            
            // Add JWT token to all requests
            this.interceptor = axios.interceptors.request.use(config => {
                if (this.token) {
                    config.headers['Authorization'] = `Bearer ${this.token}`;
                }
                return config;
            }, error => {
                return Promise.reject(error);
            });
        },
        
        // Product methods
        fetchProducts() {
            this.loading = true;
            axios.get('/products')
                .then(response => {
                    console.log('Products fetched:', response.data);
                    this.products = response.data;
                    this.loading = false;
                })
                .catch(error => {
                    console.error('Error fetching products:', error);
                    this.loading = false;
                });
        },
        
        // Handle image upload
        handleImageUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            this.productImage = file;
            
            // Create image preview
            const reader = new FileReader();
            reader.onload = e => {
                this.imagePreview = e.target.result;
            };
            reader.readAsDataURL(file);
        },
        
        // Add product with image
        addProduct() {
            if (!this.isAuthenticated) {
                alert('You must be logged in to add products');
                return;
            }
            
            // Create form data for multipart/form-data request
            const formData = new FormData();
            formData.append('name', this.newProduct.name);
            formData.append('description', this.newProduct.description || '');
            formData.append('price', this.newProduct.price);
            
            if (this.productImage) {
                formData.append('image', this.productImage);
            }
            
            console.log('Adding product with image');
            
            axios.post('/admin/products', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
                .then(response => {
                    console.log('Product added:', response.data);
                    
                    // Add the new product to the list
                    const newProductWithId = {
                        id: response.data.id,
                        name: this.newProduct.name,
                        description: this.newProduct.description || '',
                        price: parseFloat(this.newProduct.price),
                        image_url: response.data.image_url
                    };
                    
                    this.products.push(newProductWithId);
                    
                    // Reset form
                    this.newProduct = {
                        name: '',
                        description: '',
                        price: ''
                    };
                    this.productImage = null;
                    this.imagePreview = null;
                    if (this.$refs.productImage) {
                        this.$refs.productImage.value = '';
                    }
                    this.showAddProductForm = false;
                })
                .catch(error => {
                    console.error('Error adding product:', error);
                    alert('Failed to add product. Please try again.');
                });
        }
    }
});