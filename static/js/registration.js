Vue.createApp({
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            RegSchema: {
                reg: (value) => {
                    if (value) {
                        return true;
                    }
                    return 'Поле не заполнено';
                },
                phone_format: (value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                code_format: (value) => {
                    const regex = /^[a-zA-Z0-9]+$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат кода нарушен';
                    }
                    return true;
                }
            },
            Step: 'Number',
            RegInput: '',
            EnteredNumber: ''
        }
    },
    methods: {
        RegSubmit() {
            if (this.Step === 'Number') {
                // Отправляем номер телефона на сервер для запроса кода
                fetch('/request_code/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken') // Получаем CSRF-токен
                    },
                    body: JSON.stringify({ phone: this.RegInput })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.Step = 'Code';
                        this.EnteredNumber = this.RegInput;
                        this.RegInput = '';
                    } else {
                        alert('Ошибка при запросе кода.');
                    }
                });
            } else {
                // Отправляем код и номер телефона на сервер для проверки
                fetch('/verify_code/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify({ phone: this.EnteredNumber, code: this.RegInput })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        this.Step = 'Finish';
                        this.RegInput = 'Регистрация успешна';
                        // Перезагружаем страницу для обновления состояния авторизации
                        window.location.reload();
                    } else {
                        alert('Неверный код.');
                    }
                });
            }
        },
        ToRegStep1() {
            this.Step = 'Number'
            this.RegInput = this.EnteredNumber
        },
        Reset() {
            this.Step = 'Number'
            this.RegInput = ''
            EnteredNumber = ''
        }
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }
}).mount('#RegModal');
