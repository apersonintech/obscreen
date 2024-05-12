import json

from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_login import login_user, logout_user, current_user
from src.service.ModelStore import ModelStore
from src.model.entity.User import User
from src.interface.ObController import ObController


class AuthController(ObController):

    def register(self):
        self._app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self._app.add_url_rule('/logout', 'logout', self.logout, methods=['GET'])
        self._app.add_url_rule('/auth/user/list', 'auth_user_list', self._auth(self.auth_user_list), methods=['GET'])
        self._app.add_url_rule('/auth/user/add', 'auth_user_add', self._auth(self.auth_user_add), methods=['POST'])
        self._app.add_url_rule('/auth/user/edit', 'auth_user_edit', self._auth(self.auth_user_edit), methods=['POST'])
        self._app.add_url_rule('/auth/user/toggle', 'auth_user_toggle', self._auth(self.auth_user_toggle), methods=['POST'])
        self._app.add_url_rule('/auth/user/delete', 'auth_user_delete', self._auth(self.auth_user_delete), methods=['DELETE'])

    def login(self):
        login_error = None

        if current_user.is_authenticated:
            return redirect(url_for('slideshow_slide_list'))

        if len(request.form):
            user = self._model_store.user().get_one_by_username(request.form['username'], enabled=True)
            if user:
                if user.password == self._model_store.user().encode_password(request.form['password']):
                    login_user(user)
                    return redirect(url_for('slideshow_slide_list'))
                else:
                    login_error = 'bad_credentials'
            else:
                login_error = 'not_found'

        return render_template(
            'auth/login.jinja.html',
            login_error=login_error
        )

    def logout(self):
        logout_user()
        return redirect(url_for('login'))

    def auth_user_list(self):
        return render_template(
            'auth/list.jinja.html',
            enabled_users=self._model_store.user().get_enabled_users(),
            disabled_users=self._model_store.user().get_disabled_users(),
        )

    def auth_user_add(self):
        self._model_store.user().add_form(User(
            username=request.form['username'],
            password=request.form['password'],
            enabled=True,
        ))
        return redirect(url_for('auth_user_list'))

    def auth_user_edit(self):
        self._model_store.user().update_form(
            id=request.form['id'],
            username=request.form['username'],
            password=request.form['password'] if 'password' in request.form else None
        )
        return redirect(url_for('auth_user_list'))

    def auth_user_toggle(self):
        data = request.get_json()
        self._model_store.user().update_enabled(data.get('id'), data.get('enabled'))
        return jsonify({'status': 'ok'})

    def auth_user_delete(self):
        if self._model_store.user().count_all_enabled() == 1:
            return jsonify({'status': 'error', 'message': self.t('auth_user_delete_at_least_one_account')}), 400
        data = request.get_json()
        self._model_store.user().delete(data.get('id'))
        return jsonify({'status': 'ok'})

