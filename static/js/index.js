Vue.createApp({
    name: "App",
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            schema1: {
                lvls: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' количество уровней';
                },
                form: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' форму торта';
                },
                topping: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' топпинг';
                }
            },
            schema2: {
                name: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' имя';
                },
                phone: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' телефон';
                },
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-Я]+$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат имени нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                },
                phone_format:(value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                email: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' почту';
                },
                address: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' адрес';
                },
                date: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' дату доставки';
                },
                time: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' время доставки';
                }
            },
            DATA: {
                Levels: ['не выбрано', '1', '2', '3'],
                Forms: ['не выбрано', 'Квадрат','Круг' , 'Прямоугольник'],
                Toppings: ['не выбрано', 'Без', 'Белый соус', 'Карамельный', 'Кленовый', 'Черничный', 'Молочный шоколад', 'Клубничный'],
                Berries: ['нет', 'Ежевика', 'Малина', 'Голубика', 'Клубника'],
                Decors: [ 'нет', 'Фисташки', 'Безе', 'Фундук', 'Пекан', 'Маршмеллоу', 'Марципан']
            },
            Costs: {
                Levels: [0, 400, 750, 1100],
                Forms: [0, 600, 400, 1000],
                Toppings: [0, 0, 200, 180, 200, 300, 350, 200],
                Berries: [0, 400, 300, 450, 500],
                Decors: [0, 300, 400, 350, 300, 200, 280],
                Words: 500
            },
            Levels: 0,
            Form: 0,
            Topping: 0,
            Berries: 0,
            Decor: 0,
            Words: '',
            Comments: '',
            Designed: false,
            isUrgent: false,
            showStep3: false,

            Name: '',
            Phone: null,
            Email: null,
            Address: null,
            Dates: null,
            Time: null,
            DelivComments: '',
            client: null,
            last_order: null,
        }
    },
    methods: {
        handleHash() {
            if (window.location.hash === '#step3') {
                this.showStep3 = true;
                // После обновления DOM прокручиваем к элементу
                this.$nextTick(() => {
                    const element = document.getElementById('step3');
                    if (element) {
                        element.scrollIntoView({ behavior: 'smooth' });
                    }
                });
            }
        },
        showConstructor() {
            // Устанавливаем хэш и позволяем обработчику handleHash сделать остальную работу
            window.location.hash = 'step3';
        },
        ToStep4() {
            this.Designed = true
            setTimeout(() => {
                this.$refs.ToStep4.click();
            }, 0);
        },
        async submitOrder() {
            try {
                console.log('=== DEBUG: Starting form submission ===');
                console.log('Current client data:', {
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email
                });
                
                // Сначала отправляем форму
                await this.$refs.HiddenFormSubmit.click();
                console.log('Form submitted successfully');
                
                // Сохраняем текущие данные клиента
                const currentClientData = {
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email
                };
                console.log('Saved current client data:', currentClientData);
                
                // Очищаем форму
                this.resetForm();
                console.log('Form reset completed');
                
                // Используем history API для очистки URL без перезагрузки
                history.pushState({}, '', '/');
                console.log('URL cleaned');
                
                // Восстанавливаем данные клиента после очистки формы
                this.client = currentClientData;
                this.Name = currentClientData.name;
                this.Phone = currentClientData.phone;
                this.Email = currentClientData.email;
                console.log('Client data restored:', {
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email
                });
            } catch (error) {
                console.error('Error submitting form:', error);
            }
        },
        resetForm() {
            console.log('=== DEBUG: Starting form reset ===');
            console.log('Current form state:', {
                Levels: this.Levels,
                Form: this.Form,
                Topping: this.Topping,
                Name: this.Name,
                Phone: this.Phone,
                Email: this.Email
            });
            
            // Сброс всех полей формы
            this.Levels = 0;
            this.Form = 0;
            this.Topping = 0;
            this.Berries = 0;
            this.Decor = 0;
            this.Words = '';
            this.Comments = '';
            this.Name = '';
            this.Phone = null;
            this.Email = null;
            this.Address = null;
            this.Dates = null;
            this.Time = null;
            this.DelivComments = '';
            this.Designed = false;
            
            console.log('Form reset completed. New state:', {
                Levels: this.Levels,
                Form: this.Form,
                Topping: this.Topping,
                Name: this.Name,
                Phone: this.Phone,
                Email: this.Email
            });
        },
        getUrgentMarkup() {
            return 1.2; // Наценка 20%
        }
    },
    computed: {
        Cost() {
            let W = this.Words ? this.Costs.Words : 0
            let basePrice = this.Costs.Levels[this.Levels] + this.Costs.Forms[this.Form] +
                this.Costs.Toppings[this.Topping] + this.Costs.Berries[this.Berries] +
                this.Costs.Decors[this.Decor] + W
            
            return basePrice
        },
        TotalCost() {
            // Проверяем срочность заказа только если выбраны дата и время
            if (this.Dates && this.Time) {
                const orderDateTime = new Date(this.Dates + 'T' + this.Time)
                const now = new Date()
                const hoursDiff = (orderDateTime - now) / (1000 * 60 * 60)
                
                this.isUrgent = hoursDiff < 24;
            }
            
            if (this.isUrgent) {
                return Math.round(this.Cost * 1.2) // +20% за срочность
            }
            return this.Cost
        }
    },
    mounted() {
        // Проверяем, есть ли данные клиента в сессии
        if (this.client) {
            this.Name = this.client.name || '';
            this.Phone = this.client.phone || '';
            this.Email = this.client.email || '';
            this.Address = this.client.address || '';
        }

        // Проверяем, есть ли в URL якорь #step3 и показываем конструктор, если да
        this.handleHash();

        // Добавляем обработчик события для получения данных из сессии
        window.addEventListener('message', (event) => {
            if (event.data.type === 'clientData') {
                this.client = event.data.client;
                this.Name = this.client.name || '';
                this.Phone = this.client.phone || '';
                this.Email = this.client.email || '';
                this.Address = this.client.address || '';
            }
        });
        
        // Обработчик изменения хэша в URL
        window.addEventListener('hashchange', () => {
            this.handleHash();
        });
    }
}).mount('#VueApp')