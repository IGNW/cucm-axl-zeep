from cucm_gui import app
from flask import render_template, flash, redirect, url_for, session 
from cucm_gui.forms import LoginForm, DevicePool, Users, User

from cucm_gui.cucm import connect_to_cucm


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
    cucm = connect_to_cucm(username=session.get('cucm_username'), password=session.get('cucm_password'), cucm_ip=session.get('cucm_ip'))
    returned_data = cucm.listDevicePool(searchCriteria={'name': '%'}, returnedTags={'name': ''})
    device_pools = [x['name'] for x in returned_data['return']['devicePool']]
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
        cucm = connect_to_cucm(username=session.get('cucm_username'), password=session.get('cucm_password'), cucm_ip=session.get('cucm_ip'))
        returned_data = cucm.listUser(searchCriteria={'userid': '%'}, returnedTags={'userid': '', 'firstName': '', 'lastName': ''})
        users = [(f"{x['userid']}", f"{x['firstName']} {x['lastName']}")  for x in returned_data['return']['user']]
        form.user.choices = users
        return render_template('select_user.html', title="Select User", form=form)

@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    form = User()
    cucm = connect_to_cucm(username=session.get('cucm_username'), password=session.get('cucm_password'), cucm_ip=session.get('cucm_ip'))
    userid = session.get('selected_user')
    if form.validate_on_submit():
        print(form.data)
        flash(f'Updated User: {form.data}')
        return redirect(url_for('main_page'))
    else:
        returned_data = cucm.getUser(userid=userid)
        user_data = returned_data['return']['user']

        form.first_name.data = user_data['firstName']
        form.last_name.data = user_data['lastName']
        form.display_name.data = user_data['displayName']

        print(form.first_name.default)
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
    


