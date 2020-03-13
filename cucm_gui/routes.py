from cucm_gui import app
from flask import render_template, flash, redirect, url_for, session
from cucm_gui.forms import LoginForm, Users, User, IncludeLDAPUsers

from cucm_gui import cucm
from ast import literal_eval


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
    ldap_form = IncludeLDAPUsers()
    if form.validate_on_submit():
        session['cucm_username'] = form.cucm_username.data
        session['cucm_password'] = form.cucm_password.data
        session['cucm_ip'] = form.cucm_ip.data
        session['include_ldap_users'] = ldap_form.include_ldap.data
        flash(f'Returned data from the CUCM at IP: {form.cucm_ip.data}')
        return redirect(url_for('select_user'))
    return render_template('cucm_login.html', title='CUCM Data', form=form, ldap_form=ldap_form)


@app.route('/select_user', methods=['GET', 'POST'])
def select_user():
    form = Users()
    if form.is_submitted():
        session['selected_user'] = form.user.data
        session['is_ldap_user'] = cucm.is_ldap_user()
        return redirect(url_for('update_user'))
    else:
        users = cucm.list_users()
        form.user.choices = users
        return render_template('select_user.html', title="Select User", form=form)


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    form = User()
    userid = session.get('selected_user')

    if form.is_submitted():
        data_to_update = form.data
        data_to_update.pop('csrf_token')
        data_to_update.pop('submit')
        data_to_update['userid'] = userid
        groups = data_to_update.pop('userGroup')
        if session.get('is_ldap_user'):
            # Can't update these fields if the users
            # is an LDAP user
            data_to_update.pop('firstName')
            data_to_update.pop('lastName')
            data_to_update.pop('displayName')

        dictified_groups = []
        for group in groups:
            # A way of converting a string representation of a dictionary
            # to a python dictionary
            dictified_groups.append(literal_eval(group))

        data_to_update['associatedGroups'] = {}
        data_to_update['associatedGroups']['userGroup'] = dictified_groups

        session['user_data_to_update'] = data_to_update

        try:
            cucm.update_user()
            flash(f'Updated User: {userid}')
        except Exception as e:
            print(e)
            print(dir(e))
            flash(f'User was not updated.  The error returned was: {str(e)}')

        return redirect(url_for('main_page'))
    else:
        user_data = cucm.get_user()
        session['user_data'] = user_data

        # Since the data in the form is a string version of a dictionary
        # Must make the existing selections match the data format
        if user_data['associatedGroups']:
            user_groups = [str({'name': group['name']}) for group in user_data['associatedGroups']['userGroup']]
        else:
            user_groups = []

        system_user_groups = cucm.list_user_groups()
        session['system_user_groups'] = system_user_groups

        form.firstName.data = user_data['firstName']
        form.lastName.data = user_data['lastName']
        form.displayName.data = user_data['displayName']

        form.userGroup.choices = system_user_groups
        form.userGroup.data = user_groups

        return render_template('update_user.html',
                               title="Update User",
                               form=form,
                               userid=userid,
                               is_ldap_user=session['is_ldap_user'])
