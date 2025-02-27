Vue.createApp({
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            Edit: false,
            Name: 'Ирина',
            Phone: '8 909 000-00-00',
            Email: 'nyam@gmail.com',
            Schema: {
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-я]+$/
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Недопустимые символы в имени';
                    }
                    return true;
                },
                phone_format: (value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                }
            }
        }
    },
    methods: {
        ApplyChanges() {
            this.Edit = false;
            fetch('/api/update-client-data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email,
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Client data updated successfully');
                    window.location.href = data.redirect_url;
                } else {
                    console.error('Error updating client data:', data.error);
                }
            })
            .catch(error => console.error('Error updating client data:', error));
        }
    },
    mounted() {
        // Fetch client data from the server
        fetch('/api/client-data')
            .then(response => response.json())
            .then(data => {
                this.Name = data.name;
                this.Phone = data.phone;
                this.Email = data.email;

                // Check if the URL has the 'edit' parameter
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('edit')) {
                    this.Edit = true;
                }
            })
            .catch(error => console.error('Error fetching client data:', error));
    }
}).mount('#LK')