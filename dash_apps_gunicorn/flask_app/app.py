# app.py
from flask import Flask
import dashboard_for_yandex_afisha_app

app = Flask(__name__)

# Инициализация Dash-приложений
dashboard_for_yandex_afisha_app.init_dash(app)


# # Основная страница Flask-приложения
# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8050)
