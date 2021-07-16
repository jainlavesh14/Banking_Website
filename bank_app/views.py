from django.shortcuts import render, redirect
from smtplib import SMTPRecipientsRefused
from django.core.mail import EmailMultiAlternatives
from .models import Bank_Model, Transaction_Model
from datetime import datetime
from bank.settings import GOOGLE_RECAPTCHA_SECRET_KEY
from bank.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import urllib
import json
from xhtml2pdf import pisa
from io import BytesIO

# only render the about page, no functionality (Display)
def about(request):
	return render(request, "about.html")


# Adding Customer in our database via models created
def add_customer(request):

	# Getting details which user has filled in html page
	if request.method == "POST":
		n = request.POST.get('name')
		e = request.POST.get('email')
		m = request.POST.get('mobile_number')
		at = request.POST.get('account_type')
		b = request.POST.get('balance')
		a = request.POST.get('address')
	
		# Checking / Validation for Account type
		lst = ["Savings", "Current", "current", "savings", "saving", "Saving"]
		if (at not in lst):
			return render(request, 'add_customer.html', {'msg' : 'Please enter correct account type.'})
		
		# Checking whether the entered email already exists or not
		data = Bank_Model.objects.filter(email = e)
		print(data)		

		if data:
			return render(request, 'add_customer.html', {'msg' : 'User exists with same email Id.'})
		else:
			d = Bank_Model(name = n, email = e, mobile_number = m, account_type = at, balance = b, address = a)
			d.save()

			send_mail("Welcome to Jain Bhadrajun Bank", "Dear " + n + ",\n\nWe are delighted to add you as our customer.\nWe wish to advise you that balance in your account is Rs." + b + "\n\nThis is a system generated email, do not reply to this email id.\n\nThanks and Regards,\nJain Bhadrajun Bank.", EMAIL_HOST_USER, [e])

		return render(request, 'add_customer.html', {'msg' : 'Customer added'})
	else:
		return render(request, 'add_customer.html')


# get all the stored data from the models(database) and pass it to html page for displaying
def view_customers(request):
	data = Bank_Model.objects.all()
	return render(request, 'view_customers.html', {'data' : data})


# get information of particular customer via email
def more_info(request, email):
	data = Bank_Model.objects.get(pk = email)
	return render(request, 'more_info.html', {'data' : data})


# only render the about page, no functionality (Display)
def contact(request):
	return render(request, 'contact.html')


# transfer money from one customer to another
def transfer(request):
	if request.method == "POST":
	
		# getting captcha response
		recaptcha_response = request.POST.get('g-recaptcha-response')
		url = 'https://www.google.com/recaptcha/api/siteverify'
		values = {'secret': GOOGLE_RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
		data = urllib.parse.urlencode(values).encode()
		req =  urllib.request.Request(url, data=data)
		response = urllib.request.urlopen(req)
		result = json.loads(response.read().decode())

		# if captcha is found to be validated,
		if result['success']:
			data = Bank_Model.objects.all()
			print(data)

			# Getting sender's email from html
			sender_email = request.POST.get('account_sender')
			print(sender_email)

			# Getting receiver's email from html
			receiver_email = request.POST.get('account_receiver')
				
			# Getting transfer amount from html
			transfer_amount = (float)(request.POST.get('transfer_amount'))
		
			if(receiver_email == None or sender_email == None):
				return render(request, 'transfer.html', {'data' : data, 'msg' : 'Please select customer'})
			elif(sender_email == receiver_email):
				return render(request, 'transfer.html', {'data' : data, 'msg' : 'Please select different accounts'})
			elif(transfer_amount > (Bank_Model.objects.filter(email = sender_email).values('balance'))[0]['balance']):
				return render(request, 'transfer.html', {'data' : data, 'msg' : 'Insufficient Funds :('})
			else:	
				sender_balance = Bank_Model.objects.filter(email = sender_email).values('balance')
				sender_balance = sender_balance[0]['balance']

				receiver_balance = Bank_Model.objects.filter(email = receiver_email).values('balance')
				receiver_balance = receiver_balance[0]['balance']

				updated_sender = round((sender_balance - transfer_amount), 3)
				sub = Bank_Model.objects.filter(email = sender_email).update(balance = updated_sender)
				updated_receiver = round((receiver_balance + transfer_amount), 3)
				rub = Bank_Model.objects.filter(email = receiver_email).update(balance = updated_receiver)
	
				sender_name = Bank_Model.objects.filter(email = sender_email).values('name')
				sender_name = sender_name[0]['name']
				print(sender_name)	

				receiver_name = Bank_Model.objects.filter(email = receiver_email).values('name')
				receiver_name = receiver_name[0]['name']
				print(receiver_name)
	
				now = datetime.now()
				dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
				print("date and time =", dt_string)
	
				d = Transaction_Model(send = sender_name, receive = receiver_name, amount = transfer_amount, dt = dt_string)	
				d.save()

			
				send_mail("Transaction with Jain Bhadrajun Bank", "Dear " + sender_name + ",\n\nYour account has been debited by Rs." + str(transfer_amount) + " as on " + dt_string + " and available balance is Rs." + str(updated_sender) + "\n\nThanks and Regards,\nJain Bhadrajun Bank.", EMAIL_HOST_USER, [sender_email])

				send_mail("Transaction with Jain Bhadrajun Bank", "Dear " + receiver_name + ",\n\nYour account has been credited by Rs." + str(transfer_amount) + " as on " + dt_string + " and available balance is Rs." + str(updated_receiver) + "\n\nThanks and Regards,\nJain Bhadrajun Bank.", EMAIL_HOST_USER, [receiver_email])
				

				return render(request, 'transfer.html', {'data' : data, 'msg' : 'Transfer Completed'})
		else:
			data = Bank_Model.objects.all()
			return render(request, 'transfer.html', {'msg' : 'Please verify the captcha', 'data' : data})
	else:
		data = Bank_Model.objects.all()
		return render(request, 'transfer.html', {'data' : data})

def transaction_history(request):
	if request.method == "POST":
		data = Bank_Model.objects.all()
		email = request.POST.get('history')
		print(email)
		if (email == None):
			return render(request, 'transaction_history.html', {'msg' : 'Please select customer', 'data' : data})
		else:
			dum = Bank_Model.objects.filter(email = email).values('name')
			dum = dum[0]['name']
			
			dumm = Transaction_Model.objects.filter(send = dum)
			

			rdumm = Transaction_Model.objects.filter(receive = dum)	
			
			send_list = []
			
			#----------------------------------------------------------------------------------------
			senderr = Transaction_Model.objects.filter(send = dum).values('send')
			receiverr = Transaction_Model.objects.filter(send = dum).values('receive')
			amountt = Transaction_Model.objects.filter(send = dum).values('amount')
			dtt = Transaction_Model.objects.filter(send = dum).values('dt')
			print(senderr)

			receive_list = []
			amount_list = []
			dt_list = []
			for s in senderr:
				val = s['send']
				send_list.append(val)
			print(send_list)

			for s in receiverr:
				val = s['receive']
				receive_list.append(val)
			print(receive_list)

			for s in amountt:
				val = s['amount']
				amount_list.append(val)
			print(amount_list)

			for s in dtt:
				val = s['dt']
				dt_list.append(val)
			print(dt_list)


			html_content_complete = ""
			html_content = ""
			
			html_content_1 = f"<html><head><title>Transaction History</title></head><body style = 'font-size:20px;'><center><table>"


			if dumm is not None:

				html_content_2 = f"<h5><center><br><p style = 'font-size:30px;'>Jain Bhadrajun Bank</p><h2 style = 'font-size:25px;'>Bank Statement</h2><br>Debit Details </center></h5><tr><th> Sender </th><th> Receiver</th><th> Amount </th><th> Date and Time </th><th> Status </th></tr>"

				html_content_3 = ""
								
				for i in range(len(send_list)):
					html_content_a = f'<tr align = center><td>{ send_list[i] }</td><td>{ receive_list[i] }</td><td>{ amount_list[i] }</td><td >{ dt_list[i] }</td><td>Debited</td></tr>'

					html_content_3 = html_content_3 + html_content_a
	
				html_content_4 = f"</table><table><br></center></body></html>"
			
			html_content = html_content_1 + html_content_2 + html_content_3 + html_content_4

			print(html_content)
			#-----------------------------------------------------------------------------------------
			
			rsend_list = []
			
			#----------------------------------------------------------------------------------------

			rsenderr = Transaction_Model.objects.filter(receive = dum).values('send')
			rreceiverr = Transaction_Model.objects.filter(receive = dum).values('receive')
			ramountt = Transaction_Model.objects.filter(receive = dum).values('amount')
			rdtt = Transaction_Model.objects.filter(receive = dum).values('dt')
			print(rsenderr)

			rreceive_list = []
			ramount_list = []
			rdt_list = []

			for s in rsenderr:
				val = s['send']
				rsend_list.append(val)
			print(rsend_list)

			for s in rreceiverr:
				val = s['receive']
				rreceive_list.append(val)
			print(rreceive_list)

			for s in ramountt:
				val = s['amount']
				ramount_list.append(val)
			print(ramount_list)

			for s in rdtt:
				val = s['dt']
				rdt_list.append(val)
			print(rdt_list)


			rhtml_content = ""
			
			rhtml_content_1 = f"<html><head><title>Transaction History</title></head><body style = 'font-size:20px;'><center><table>"


			if rdumm is not None:

				rhtml_content_2 = f"<h5><center> Credit Details </center></h5><tr><th> Sender </th><th> Receiver</th><th> Amount </th><th> Date and Time </th><th> Status </th></tr>"

				rhtml_content_3 = ""
								
				for i in range(len(rsend_list)):
					rhtml_content_a = f'<tr align = center><td>{ rsend_list[i] }</td><td>{ rreceive_list[i] }</td><td>{ ramount_list[i] }</td><td >{ rdt_list[i] }</td><td>Credited</td></tr>'

					rhtml_content_3 = rhtml_content_3 + rhtml_content_a
	
				rhtml_content_4 = f"</table><table><br></center></body></html>"
			
			rhtml_content = rhtml_content_1 + rhtml_content_2 + rhtml_content_3 + rhtml_content_4
			html_content_complete = html_content + rhtml_content
		
			#---------------------------------------------------------------------------------------------
			result = BytesIO()
			pdf = pisa.pisaDocument(BytesIO(html_content_complete.encode('utf-8')), result)
			pdf = result.getvalue()
			filename = f'Bank_Statement' + '.pdf'
	
			msg = EmailMultiAlternatives("Bank Statement", "Dear " + dum + ", \nPlease find your bank statement.\n\nRegards,\nJain Bhadrajun Bank.", "tester.lavesh@gmail.com", [email])
			msg.attach(filename, pdf, 'application/pdf')
			msg.send()
		
			return render(request, 'transaction_history.html', {'data' : data, 'dumm' : dumm, 'rdumm' : rdumm})
	else:
		data = Bank_Model.objects.all()
		return render(request, 'transaction_history.html', {'data' : data})