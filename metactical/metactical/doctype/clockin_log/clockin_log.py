# Copyright (c) 2023, Metactical and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class ClockinLog(Document):
	def after_insert(self):
		#Create employee Checkin
		#self.insert_employee_checkin()
		pass
	
	def before_save(self):
		# Validate total hours worked for clockin log
		if self.has_clocked_out:
			time1 = f'{self.date} {self.from_time}'
			time2 = f'{self.date} {self.to_time}'
			self.total_hours = time_difference(time1, time2)
			#self.update_user_pay_cycle_record()

	# def on_update(self):
	# 	if self.has_clocked_out:
	# 		self.update_user_pay_cycle_record()

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		self.update_user_pay_cycle_record()
		self.employee_checkin()

	""" def insert_employee_checkin(self):
		employee_exists = frappe.db.exists("Employee", {"user_id": self.user})

		if employee_exists:
			in_employee_checkin = frappe.get_doc({
				"doctype": "Employee Checkin",
				"log_type": "IN",
				"employee": employee_exists,
				"time": f'{self.date} {self.to_time}'
			})

			in_employee_checkin.insert()

			#Link employee checkin to clockin log doc
			self.in_employee_checkin_record = in_employee_checkin.name

		else:
			frappe.throw("Employee record not found") """
	
	#Manipulate Employee Checkin Log
	def employee_checkin(self):
		pass
		""" employee_exists = frappe.db.exists("Employee", {"user_id": self.user})

		if employee_exists:
			if not self.out_employee_checkin_record:
				#Create employee out checkin record
				out_employee_checkin = frappe.get_doc({
					"doctype": "Employee Checkin",
					"log_type": "OUT",
					"employee": employee_exists,
					"time": f'{self.date} {self.to_time}'
				})

				out_employee_checkin.insert()
				frappe.db.commit()

				#Link record
				self.out_employee_checkin_record = out_employee_checkin.name

			else:
				out_employee_checkin_record = frappe.get_doc("Employee Checkin", self.out_employee_checkin_record)
				out_employee_checkin_record.time = f"{self.date} {self.to_time}"
				out_employee_checkin_record.save()

		else:
			frappe.throw("Employee record not found") """
	
	def update_user_pay_cycle_record(self):
		clockin_logs = frappe.get_all("Clockin Log", filters={
			"user": self.user,
			"date": self.date,
			"has_clocked_out": 1,
			"name": ("!=", self.name)
		}, fields=['total_hours'])

		total_hours_worked = self.total_hours

		for clockin_log in clockin_logs:
			total_hours_worked += clockin_log.total_hours

		work_day = frappe.db.exists("Pay Cycle Log", {
			"owner": self.user,
			"date": self.date
		})

		#Get parent field for work day
		parent_field = frappe.db.get_value("Pay Cycle Log", work_day, "parent")

		frappe.errprint(work_day)

		#Update work day hours
		frappe.db.set_value("Pay Cycle Log", work_day, "hours_worked", total_hours_worked)
		frappe.db.commit()

		#Calculate total hours in pay cycle
		pay_cycle_record = frappe.get_doc("Pay Cycle", parent_field)
		pay_cycle_record.update_hours()
		pay_cycle_record.save()

def time_difference(time1, time2):
	# convert times to datetime objects
	time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
	time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
	
	# calculate the difference between times
	time_diff = abs(time1 - time2)
	
	# convert difference to hours
	time_diff_hours = time_diff.total_seconds() / 3600
	
	return time_diff_hours
