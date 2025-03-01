Vue.createApp({
    name: "LK",
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            Schema: {
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-Я]+$/
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if (!regex.test(value)) {
                        return '⚠ Формат имени нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if (!regex.test(value)) {
                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                },
                phone_format: (value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return '⚠ Поле не может быть пустым';
                    }
                    if (!regex.test(value)) {
                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                }
            },
            Name: '',
            Phone: '',
            Email: '',
            Edit: true,
            client: null
        }
    },
    methods: {
        async ApplyChanges() {
            try {
                console.log('Отправка данных на сервер:', {
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email
                });
                
                // Отправляем данные на сервер
                const response = await fetch('/api/update-client-data/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: this.Name,
                        phone: this.Phone,
                        email: this.Email
                    })
                });

                const data = await response.json();
                console.log('Ответ от сервера:', data);
                
                if (data.status === 'success') {
                    console.log('Данные успешно обновлены, перенаправление на:', data.redirect_url);
                    // Перенаправляем на URL, указанный сервером
                    window.location.href = data.redirect_url;
                } else {
                    console.error('Error updating client data:', data.error);
                }
            } catch (error) {
                console.error('Error applying changes:', error);
            }
        }
    },
    mounted() {
        // Обработчик события для получения данных из сессии
        window.addEventListener('message', (event) => {
            if (event.data.type === 'clientData') {
                this.client = event.data.client;
                this.Name = this.client.name || '';
                this.Phone = this.client.phone || '';
                this.Email = this.client.email || '';
            }
        });
    }
}).mount('#LK')