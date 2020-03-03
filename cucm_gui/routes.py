from cucm_gui import app
from flask import render_template, flash, redirect, url_for
from cucm_gui.forms import LoginForm

@app.route('/')
def main_page():
    return render_template('base.html') 

@app.route('/cucm_login', methods=['GET', 'POST'])
def cucm_login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}'.format(form.username.data))
        return redirect(url_for('cucm_device_pools'))
    return render_template('cucm_login.html', title='CUCM Data', form=form)

@app.route('/cucm_device_pools', methods=['GET, 'POST'])
def cucm_device_pools():
    device_pools = ['one', 'two', 'three']
    return render_template('cucm_device_pools.html', title= 'CUCM Device Pools', device_pools=device_pools)
