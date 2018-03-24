from flask import Flask, render_template,request
import os

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html') 

@app.route('/tvon', methods=['POST'])
def tvon():
	authorise()
	os.system('../remote_control/tvon')
	return 'OK'

@app.route('/tvinput/hdmi', methods=['POST'])
def tvinhdmi():
	authorise()
	os.system('../remote_control/hdmi_input')
	return 'OK'

@app.route('/tvinput/tv', methods=['POST'])
def tvintv():
	authorise()
	os.system('../remote_control/tv_input')
	return 'OK'

@app.route('/soundbaron', methods=['POST'])
def sbon():
	authorise()
	os.system('../remote_control/soundbar_on')
	return 'OK'

@app.route('/soundbarinput', methods=['POST'])
def sbin():
	authorise()
	os.system('../remote_control/soundbar_switch')
	return 'OK'

def authorise():
	print(request.form.get('SECRET'))
	if request.form.get('SECRET') != os.environ['SECRET']:
		raise ValueError("Secrets don't match, provided" + request.form.get('SECRET'))

if __name__ == '__main__':
	print (os.environ['SECRET'])
	app.run(debug=True, host='0.0.0.0')
