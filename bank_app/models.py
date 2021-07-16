from django.db import models

class Bank_Model(models.Model):
	name = models.CharField(max_length = 90)
	email = models.EmailField(max_length = 100, primary_key = True)
	mobile_number = models.CharField(max_length = 100)
	account_type = models.CharField(max_length = 90)
	balance = models.FloatField(max_length = 30)
	address = models.CharField(max_length = 200)

	def __str__(self):
		return self.name

class Transaction_Model(models.Model):
	send = models.CharField(max_length = 100)
	receive = models.CharField(max_length = 100)
	amount = models.FloatField(max_length = 40)
	dt = models.CharField(max_length = 50)
	
	def __str__(self):
		return self.send + " to " + self.receive
