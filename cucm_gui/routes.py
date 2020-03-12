from cucm_gui import app
from flask import render_template, flash, redirect, url_for, session
from cucm_gui.forms import LoginForm, DevicePool, Users, User

from cucm_gui import cucm


@app.route('/')
def main_page():
    return render_template('base.html')


@app.route('/list_cucm_device_pools', methods=['GET', 'POST'])
def cucm_list_device_pools():
    form = LoginForm()
    if form.validate_on_submit():
        session['cucm_username'] = form.cucm_username.data
        session['cucm_password'] = form.cucm_password.data
        session['cucm_ip'] = form.cucm_ip.data
        flash(f'Returned data from the CUCM at IP: {form.cucm_ip.data}')
        return redirect(url_for('cucm_device_pools'))
    return render_template('cucm_login.html', title='CUCM Data', form=form)


@app.route('/cucm_device_pools', methods=['GET', 'POST'])
def cucm_device_pools():
    device_pools = cucm.list_device_pools()
    return render_template('cucm_device_pools.html', title='CUCM Device Pools', device_pools=device_pools)


@app.route('/list_users', methods=['GET', 'POST'])
def list_users():
    form = LoginForm()
    if form.validate_on_submit():
        session['cucm_username'] = form.cucm_username.data
        session['cucm_password'] = form.cucm_password.data
        session['cucm_ip'] = form.cucm_ip.data
        flash(f'Returned data from the CUCM at IP: {form.cucm_ip.data}')
        return redirect(url_for('select_user'))
    return render_template('cucm_login.html', title='CUCM Data', form=form)


@app.route('/select_user', methods=['GET', 'POST'])
def select_user():
    form = Users()
    if form.is_submitted():
        session['selected_user'] = form.user.data
        return redirect(url_for('update_user'))
    else:
        users = cucm.list_users()
        form.user.choices = users
        return render_template('select_user.html', title="Select User", form=form)


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    form = User()
    userid = session.get('selected_user')
    if form.validate_on_submit():
        data_to_update = dict(form.data)
        data_to_update.pop('csrf_token')
        data_to_update.pop('submit')
        data_to_update['userid'] = userid

        session['user_data_to_update'] = data_to_update

        try:
            results = cucm.update_user()
            print(results)
            flash(f'Updated User: {userid}')
        except Exception as e:
            print(dir(e))
            print(e)
            flash(f'User was not updated.  The error returned was: {str(e)}')

        return redirect(url_for('main_page'))
    else:
        user_data = cucm.get_user()
        session['user_data'] = user_data
        form.firstName.data = user_data['firstName']
        form.lastName.data = user_data['lastName']
        form.displayName.data = user_data['displayName']

        return render_template('update_user.html', title="Update User", form=form)


@app.route('/test', methods=['GET', 'POST'])
def test():
    info = [
        ('thing44', 'Thing 44'),
        ('thing1', 'Thing 1'),
        ('thing2', 'Thing 2'),
        ('thing3', 'Thing 3')
    ]
    form = DevicePool()
    form.dp.choices = info
    return render_template('test.html', title='test', form=form)
