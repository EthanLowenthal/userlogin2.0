# TODO: check to see if we really need to send a list of users
@app.route("/register", methods=["GET"])
def register():
	users = userEngine.execute('SELECT * FROM users')
	u = []
	for _r in users:
		u.append(_r)
	return render_template('register.html', users=u)

@app.route('/check', methods=['POST'])
def check():

	POST_USERNAME = str(request.form['username'])
	POST_PASSWORD = str(request.form['password'])

	s = userSession()

	query = s.query(User).filter(User.username.in_([POST_USERNAME]))
	result = query.first()
	if result is not None:
		if check_password_hash(result.password, POST_PASSWORD):
			session['logged_in'] = True
			user = userEngine.execute('SELECT * FROM users WHERE username = ?', (POST_USERNAME))
			for p in user: session['user'] = tuple(p)
		else:
			flash('wrong')
	else:
			flash('wrong')
	s.close()


@app.route('/accounts/delete', methods=['POST'])
def deleteAccount():
	if not session.get('logged_in'):
		return redirect('login')
	user_id = request.form['id']
	username = request.form['name']

	s = userSession()
	s.query(User).filter_by(id=user_id).delete()
	s.commit()
	s.commit()
	s.close()
	flash('Account "{}" deleted!'.format(username))
	if username == session.get('user')[1]:
		return redirect('logout')
	return redirect('accounts')

@app.route('/accounts/add', methods=['POST'])
def add():
	s = userSession()
	try:
		user = User(request.form['username'], request.form['password'],isAdmin=True if request.form['isAdmin'] == 'on' else False)
	except:
		user = User(request.form['username'], request.form['password'],
					isAdmin=False)
	s.add(user)
	s.commit()
	s.commit()
	s.close()
	flash('Account "{}" created!'.format(request.form['username']))
	return redirect('accounts')


@app.route('/accounts/update', methods=['POST'])
def update():
	if not session.get('logged_in'):
		return redirect('login')
	field = str(request.form['field'])
	value = str(request.form[field])
	user_id = request.form['id']
	s = userSession()
	if field == 'password':
		s.query(User).filter_by(id=user_id).update({field: generate_password_hash(value)})
	else:
		s.query(User).filter_by(id=user_id).update({field: value})
	s.commit()
	s.commit()
	s.close()
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	flash(field.capitalize()+' updated!')
	return redirect('accounts')

@app.route('/accounts/addAdmin', methods=['POST'])
def addAdmin():
	if not session.get('logged_in'):
		return redirect('login')
	if not session.get('user')[3]:
		return redirect('')
	user_id = request.form['id']

	s = userSession()
	s.query(User).filter_by(id=user_id).update({"isAdmin": True})
	s.commit()
	s.commit()
	s.close()
	flash('Admin privileges added!')
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
	return redirect('accounts')


@app.route('/accounts/revokeAdmin', methods=['POST'])
def revokeAdmin():
	user_id = request.form['id']

	s = userSession()
	s.query(User).filter_by(id=user_id).update({"isAdmin": False})
	s.commit()
	s.commit()
	s.close()
	flash('Admin privileges revoked!')
	if user_id == str(session.get('user')[0]):
		user = userEngine.execute('SELECT * FROM users WHERE id = ?', (user_id))
		for p in user: session['user'] = tuple(p)
		return redirect('')

	return redirect('accounts')


@app.route('/userExists', methods=["POST"])
def user():
	s = userSession()
	query = s.query(User).filter(User.username.in_([request.form['username']]))
	result = query.first()
	s.close()
	if result:
		return Response('true')
	return Response('false')

@app.route('/accounts', methods=["GET"])
@app.route('/accounts/', methods=["GET"])
def manage():
	if not session.get('logged_in'):
		return redirect('login')
	if not session.get('user')[3]:
		return redirect('')
	users = userEngine.execute('SELECT * FROM users')
	u = []
	for _r in users:
		u.append(_r)
	return render_template("manage.html", name=session.get('user')[1], isAdmin=session.get('user')[3], users=u)

# index.html
# {% if isAdmin %}
# 	<li class="nav-item">
# 	<a class="nav-link" href="http://localhost:5000/accounts">Manage Accounts</a>
#   </li>
#   {% endif %}

# user.html
# {% include 'head.html' %}
#
# <form action="/update" method="POST">
# 			<div style="text-align: center;">
# 				    <div class="form-group">
# 				      <p>Update: <select class="form-control" name="field">
# 				        <option>Username</option>
# 				        <option>Password</option>
# 				      </select> </p>
# 				    </div>
#
# 				  <label class="col-form-label col-form-label-lg" for="login-pass"></label>
# 				  <input class="form-control form-control" type="password" name="password" placeholder="password">
#
#
#
# 				</div>
#
#                 <input type="submit" value="Update" class="btn btn-primary btn-block">
# 			    <br>
# 	</div>
# </form>

# register.html
# { % include
# 'head.html' %}
#
# < div
# align = "left" >
# < a
# href = "login"
#
#
# class ="btn btn-light" style="margin-top: 25px; margin-left: 20px" > Login < / a >
#
# < / div >
#
# < div
#
#
# class ="container" style="margin-top: 50px" >
#
# < div
#
#
# class ="jumbotron" style="margin: 20px auto; width: 800px;" >
#
# < h1
#
#
# class ="display-4" style="text-align: center;" > Register < / h1 >
#
# < hr
#
#
# class ="my-4" >
#
# < form
# action = "accounts/add"
# method = "post" >
# < div
#
#
# class ="input-group mb-3" >
#
# < div
#
#
# class ="input-group-prepend" >
#
# < span
#
#
# class ="input-group-text" id="basic-addon3" > Username:<
#
# 	/ span >
# < / div >
# < input
# type = "text"
#
#
# class ="form-control" onkeyup="checkUsername()" name="username" id="user" >
#
# < / div >
#
# < div
#
#
# class ="input-group mb-3" >
#
# < div
#
#
# class ="input-group-prepend" >
#
# < span
#
#
# class ="input-group-text" id="basic-addon3" > Password:<
#
# 	/ span >
# < / div >
# < input
# type = "password"
#
#
# class ="form-control" onkeyup="checkPasswords()" name="password" id="pass" >
#
# < / div >
#
# < div
#
#
# class ="input-group mb-3" >
#
# < div
#
#
# class ="input-group-prepend" >
#
# < span
#
#
# class ="input-group-text" id="basic-addon3" > Repeat Password:<
#
# 	/ span >
# < / div >
# < input
# type = "password"
#
#
# class ="form-control" onkeyup="checkPasswords()" name="password1" id="pass_" >
#
# < / div >
#
# < input
# type = "hidden"
# value = "off"
# id = "adminCheck"
# name = "isAdmin" >
#
# < div
# id = "errorDiv"
# style = "margin-bottom: 10px" >
# < div
# style = "display: none;"
# id = "invalidPassFeedback"
#
#
# class ="invalid-feedback" > Passwords don't match!</div>
#
# < div
# style = "display: none;"
# id = "invalidUserFeedback"
#
#
# class ="invalid-feedback" > Username is already taken! < / div >
#
# < div
# style = "display: none;"
# id = "invalidUserBlank"
#
#
# class ="invalid-feedback" > Username cannot be blank! < / div >
#
# < / div >
#
# < button
# type = "submit"
# id = "submitAddAccount"
#
#
# class ="btn btn-primary btn-block" > Register < / button >
#
# < / form >
# < / div >
# < / div >
#
# < script
# type = "text/javascript" >
# function
# checkPasswords()
# {
#
# if ($("#pass").val() != $("#pass_").val()) {
# $('#invalidPassFeedback').show();
# $("#submitAddAccount").attr("disabled", "disabled");
# $("#pass").addClass("is-invalid");
# $("#pass_").addClass("is-invalid");
# }
# else {
# $('#invalidPassFeedback').hide();
# $("#submitAddAccount").removeAttr("disabled");
# $("#pass").removeClass("is-invalid");
# $("#pass_").removeClass("is-invalid");
# }
# }
#
# function
# checkUsername()
# {
# if ($( "#user").val() == "") {
# $('#invalidUserBlank').show();
# $("#submitAddAccount").attr("disabled", "disabled");
# $("#user").addClass("is-invalid");
# } else {
# $('#invalidUserBlank').hide();
# $("#submitAddAccount").removeAttr("disabled");
# $("#user").removeClass("is-invalid");
#
# }
#
# $.ajax({
# 	url     : 'userExists',
# 	dataType: 'json',
# 	data    : {"username": $("#user").val()},
# type: 'POST',
# success: function(data)
# {
# if (data)
# {
# $('#invalidUserFeedback').show();
# $("#submitAddAccount").attr("disabled", "disabled");
# $("#user").addClass("is-invalid");
# } else {
# if ($( "#user").val() != "") {
# $("#user").removeClass("is-invalid");
# $("#submitAddAccount").removeAttr("disabled");
# }
# $('#invalidUserFeedback').hide();
#
# }
#
# }
# });
#
# }
#
# < / script >


# login.html
# <div align="right">
# <a href="register" class="btn btn-light" style="margin-top: 25px; margin-right: 20px">New? Register</a>
# </div>

# manage.html
# {% include 'head.html' %}
# <html>
#     <head>
#         <title>Manage Users</title>
#     </head>
#     <body style="background-color: #222">
#         {% with messages = get_flashed_messages() %}
#         {% if messages %}
#         <div class="container" style="margin-top: 30px; z-index:2; position:absolute; margin-left: auto; margin-right: auto; left: 0; right: 0;">
#             {% for message in messages %}
#             <div class="alert alert-dismissible alert-success fade in" id="alert">
#                 <button type="button" class="close" data-dismiss="alert">&times;</button>
#                 {{ message }}
#             </div>
#             {% endfor %}
#         </div>
#         {% endif %}
#         {% endwith %}
#         {% include 'nav.html' %}
#         <div class="container" style="margin-top: 30px">
#             <div class="card border-secondary mb-3">
#                 <div class="card-header">
#                     <h4>Accounts</h4>
#                 </div>
#                 <table class="table table-hover" id="userTable">
#                     <thead>
#                         <tr class="table-active">
#                             <th scope="col">ID</th>
#                             <th scope="col">Username</th>
#                             <th scope="col">Password Hash</th>
#                             <th scope="col">Is Admin</th>
#                             <th scope="col"><a class="btn btn-outline-secondary btn-sm" data-toggle="modal" data-target="#modalAddAccount" href="#">Add Account</a></th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         {% for user in users %}
#                         <tr class=" {% if user[1] == name %} table-secondary {% endif %}">
#                             <th scope="row">{{ user[0] }}</th>
#                             <td>{{ user[1] }}</td>
#                             <td>{{ user[2].replace("pbkdf2:sha256:50000$", "")[:15] + ' [...] ' + user[2][-15:] }} </td>
#                             <td>{{ True if user[3] else False }}</td>
#                             <td><a class="btn {% if user[1] == name %} btn-light {% else %} btn-secondary {% endif %} btn-sm" data-toggle="modal" data-target="#modal{{ user[0] }}" href="#">manage</a></td>
#                         </tr>
#             {% endfor %}
#                     </tbody>
#                 </table>
#                         </div>
#
#
#         </div>
#
#     </body>
#     {% for user in users %}
#     <div class="modal fade" id="modal{{ user[0] }}" tabindex="-1" role="dialog" aria-hidden="true">
#         <div class="modal-dialog" role="document">
#             <div class="modal-content">
#                 <div class="modal-header">
#                     <h5 class="modal-title" id="exampleModalLabel">{{ user[1] }}</h5>
#                     <button type="button" class="close" data-dismiss="modal" aria-label="Close">
#                     <span aria-hidden="true">&times;</span>
#                     </button>
#                 </div>
#                 <form id="updateform{{ user[0] }}" method="post">
#                     <input type="hidden" name="id" value="{{ user[0] }}">
#                     <div class="modal-body">
#                         <div class="input-group mb-3">
#                             <div class="input-group-prepend">
#                                 <label class="input-group-text" for="inputGroupSelect{{ user[0] }}">Update:</label>
#                             </div>
#                             <select class="custom-select" name="field" onChange="checkManage('{{ user[0] }}')" id="inputGroupSelect{{ user[0] }}">
#                                 <option value="username" selected>Username</option>
#                                 <option value="password">Password</option>
#                             </select>
#                         </div>
#                         <div id="inputGroupSelectUsername{{ user[0] }}">
#                             <div class="input-group mb-3" >
#                                 <div class="input-group-prepend">
#                                     <span class="input-group-text">Username:</span>
#                                 </div>
#                                 <input type="text" class="form-control" name="username" onkeyup="checkManageUsername('{{ user[0] }}')" id="user{{ user[0] }}">
#                             </div>
#                         </div>
#                         <div id="inputGroupSelectPassword{{ user[0] }}" style="display: none">
#                             <div class="input-group mb-3">
#                                 <div class="input-group-prepend">
#                                     <span class="input-group-text">Password:</span>
#                                 </div>
#                                 <input type="password" class="form-control" name="password" onkeyup="checkManagePasswords('{{ user[0] }}')"  id="pass{{ user[0] }}">
#                             </div>
#                             <div class="input-group mb-3">
#                                 <div class="input-group-prepend">
#                                     <span class="input-group-text">Repeat password:</span>
#                                 </div>
#                                 <input type="password" class="form-control" onkeyup="checkManagePasswords('{{ user[0] }}')" id="pass_{{ user[0] }}">
#                             </div>
#                         </div>
#                         <div id="errorDiv" style="margin-bottom: 10px">
#                             <div style="display: none;" id="invalidPassFeedback{{ user[0] }}" class="invalid-feedback">Passwords don't match!</div>
#                             <div style="display: none;" id="invalidUserFeedback{{ user[0] }}" class="invalid-feedback">Username is already taken!</div>
#                             <div style="display: none;" id="invalidUserBlank{{ user[0] }}" class="invalid-feedback">Username cannot be blank!</div>
#                         </div>
#                     </div>
#                     <div class="modal-footer">
#                         <a class="btn btn-danger" data-toggle="modal" data-target="#delete{{ user[0] }}">Delete</a>
#                         {% if user[3] %}
#                         <button onclick="submitForm('accounts/revokeAdmin', '{{ user[0] }}')" class="btn btn-danger">Revoke Admin</button>
#                         {% else %}
#                         <button onclick="submitForm('accounts/addAdmin', '{{ user[0] }}')" class="btn btn-success">Make Admin</button>
#                         {% endif %}
#                         <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
#                         <button onclick="submitForm('accounts/update', '{{ user[0] }}')" id="submitManageAccount{{ user[0] }}"  class="btn btn-primary">Save changes</button>
#                     </div>
#                 </form>
#             </div>
#         </div>
#     </div>
#     <div class="modal fade" id="delete{{ user[0] }}" tabindex="-1" role="dialog" aria-hidden="true">
#         <div class="modal-dialog" role="document">
#             <div class="modal-content">
#                 <div class="modal-header">
#                     <h5 class="modal-title" id="exampleModalLabel">Are you sure you want to delete {{ user[1] }}?</h5>
#                     <button type="button" class="close" data-dismiss="modal" aria-label="Close">
#                     <span aria-hidden="true">&times;</span>
#                     </button>
#                 </div>
#                 <form action="http://localhost:5000/accounts/delete" method="post">
#                     <input type="hidden" name="id" value="{{ user[0] }}">
#                     <input type="hidden" name="name" value="{{ user[1] }}">
#                     <div class="modal-footer">
#                         <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
#                         <button type="submit" class="btn btn-danger">Delete</button>
#                     </div>
#                 </form>
#             </div>
#         </div>
#     </div>
#     </div>
#     {% endfor %}
#     <div class="modal fade" id="modalAddAccount" tabindex="-1" role="dialog" aria-hidden="true">
#         <div class="modal-dialog" role="document">
#             <div class="modal-content">
#                 <div class="modal-header">
#                     <h5 class="modal-title" id="exampleModalLabel">Add Account</h5>
#                     <button type="button" class="close" data-dismiss="modal" aria-label="Close">
#                     <span aria-hidden="true">&times;</span>
#                     </button>
#                 </div>
#                 <form action="http://localhost:5000/accounts/add" method="post">
#                     <div class="modal-body">
#                         <div class="input-group mb-3">
#                             <div class="input-group-prepend">
#                                 <span class="input-group-text" id="basic-addon3">Username:</span>
#                             </div>
#                             <input type="text" class="form-control" onkeyup="checkUsername()" name="username" id="user">
#                         </div>
#                         <div class="input-group mb-3">
#                             <div class="input-group-prepend">
#                                 <span class="input-group-text" id="basic-addon3">Password:</span>
#                             </div>
#                             <input type="password" class="form-control" onkeyup="checkPasswords()" name="password" id="pass">
#                         </div>
#                         <div class="input-group mb-3">
#                             <div class="input-group-prepend">
#                                 <span class="input-group-text" id="basic-addon3">Repeat Password:</span>
#                             </div>
#                             <input type="password" class="form-control" onkeyup="checkPasswords()" name="password1" id="pass_">
#                         </div>
#                         <div class="custom-control custom-checkbox">
#                             <input type="checkbox" class="custom-control-input" id="adminCheck" name="isAdmin">
#                             <label class="custom-control-label" for="adminCheck">Is Admin</label>
#                         </div>
#                         <div id="errorDiv" style="margin-bottom: 10px">
#                             <div style="display: none;" id="invalidPassFeedback" class="invalid-feedback">Passwords don't match!</div>
#                             <div style="display: none;" id="invalidUserFeedback" class="invalid-feedback">Username is already taken!</div>
#                             <div style="display: none;" id="invalidUserBlank" class="invalid-feedback">Username cannot be blank!</div>
#                         </div>
#                     </div>
#                     <div class="modal-footer">
#                         <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
#                         <button type="submit" id="submitAddAccount" class="btn btn-primary">Add Account</button>
#                     </div>
#                 </form>
#             </div>
#         </div>
#     </div>
#     <script type="text/javascript">
#         function checkPasswords() {
#
#           if ($("#pass").val() != $("#pass_").val()) {
#             $('#invalidPassFeedback').show();
#             $("#submitAddAccount").attr("disabled", "disabled");
#             $("#pass").addClass("is-invalid");
#             $("#pass_").addClass("is-invalid");
#           }
#           else {
#             $('#invalidPassFeedback').hide();
#             $("#submitAddAccount").removeAttr("disabled");
#             $("#pass").removeClass("is-invalid");
#             $("#pass_").removeClass("is-invalid");
#           }
#         }
#
#         function checkUsername() {
#           if ($( "#user" ).val() == "") {
#               $('#invalidUserBlank').show();
#               $("#submitAddAccount").attr("disabled", "disabled");
#               $("#user").addClass("is-invalid");
#           } else {
#               $('#invalidUserBlank').hide();
#               $("#submitAddAccount").removeAttr("disabled");
#               $("#user").removeClass("is-invalid");
#           }
#
#           $.ajax({
#               url: 'userExists',
#               dataType: 'json',
#               data: {"username": $( "#user" ).val()},
#               type: 'POST',
#               success: function(data) {
#                   if (data) {
#                       $('#invalidUserFeedback').show();
#                       $("#submitAddAccount").attr("disabled", "disabled");
#                       $("#user").addClass("is-invalid");
#                   } else {
#                       if ($( "#user" ).val() != "") {
#                       $("#user").removeClass("is-invalid");
#                       $("#submitAddAccount").removeAttr("disabled");
#
#                   }
#                       $('#invalidUserFeedback').hide();
#               }
#
#               }
#           });
#
#         }
#
#         function checkManage(id) {
#
#           var x = "#inputGroupSelect"+id
#           if ($(x).val() == "username") {
#             $("#inputGroupSelectUsername"+id).show();
#             $("#inputGroupSelectPassword"+id).hide();
#
#             $('#invalidPassFeedback'+id).hide();
#             $("submitManageAccount"+id).removeAttr("disabled");
#             $("#pass"+id).removeClass("is-invalid");
#             $("#pass_"+id).removeClass("is-invalid");
#
#             checkManageUsername(id);
#
#           } else {
#             $("#inputGroupSelectUsername"+id).hide();
#             $("#inputGroupSelectPassword"+id).show();
#
#             checkManagePasswords(id);
#
#             $('#invalidUserFeedback'+id).hide();
#             $("#submitManageAccount"+id).removeAttr("disabled");
#             $("#user"+id).removeClass("is-invalid");
#
#           }
#
#         }
#
#         function checkManageUsername(id) {
#           if ($( "#user"+id ).val() == "") {
#               $('#invalidUserBlank'+id).show();
#               $("#submitAddAccount"+id).attr("disabled", "disabled");
#               $("#user"+id).addClass("is-invalid");
#           } else {
#               $('#invalidUserBlank'+id).hide();
#               $("#submitAddAccount"+id).removeAttr("disabled");
#               $("#user"+id).removeClass("is-invalid");
#           }
#
#           $.ajax({
#               url: 'userExists',
#               dataType: 'json',
#               data: {"username": $( "#user"+id ).val()},
#               type: 'POST',
#               success: function(data) {
#                   if (data) {
#                       $('#invalidUserFeedback'+id).show();
#                       $("#submitAddAccount"+id).attr("disabled", "disabled");
#                       $("#user"+id).addClass("is-invalid");
#                   } else {
#                       if ($( "#user" ).val() != "") {
#                       $("#user"+id).removeClass("is-invalid");
#                       $("#submitAddAccount"+id).removeAttr("disabled");
#
#                   }
#                       $('#invalidUserFeedback'+id).hide();
#               }
#
#               }
#           });
#         }
#
#           function checkManagePasswords(id) {
#           if ($("#pass"+id).val() != $("#pass_"+id).val()) {
#             $('#invalidPassFeedback'+id).show();
#             $("#submitManageAccount"+id).attr("disabled", "disabled");
#             $("#pass"+id).addClass("is-invalid");
#             $("#pass_"+id).addClass("is-invalid");
#           }
#           else {
#             $('#invalidPassFeedback'+id).hide();
#             $("#submitManageAccount"+id).removeAttr("disabled");
#             $("#pass"+id).removeClass("is-invalid");
#             $("#pass_"+id).removeClass("is-invalid");
#           }
#         }
#
#         function submitForm(action, id) {
#               document.getElementById('updateform'+id).action = "http://localhost:5000/"+action;
#               document.getElementById('updateform'+id).submit();
#         }
#
#         $("#alert").fadeTo(5000, 500).slideUp(500, function(){
#           $("#alert").slideUp(500);
#         });
#
#     </script>
# </html>