import pandas as pd

class Allocator:
	@staticmethod
	def _import_data_fillna (file_name):
		file_data = pd.read_csv(file_name)
		file_data = file_data.fillna(0)
		return file_data

	@classmethod
	def _import_payroll_data (cls, file_name):
		data = cls._import_data_fillna(file_name)
		names = data.iloc[:, 5].values
		pay = data.iloc[:, 6].values
		return names, pay

	@classmethod
	def _missing_name_for_prepaid_seat (cls, file_name):
		names, payment = cls._import_payroll_data(file_name)
		i = 0
		prepaid_seat_individuals = []
		for name in names:
			if payment[i] == 49:
				prepaid_seat_individuals.append(name)
			i += 1
		i = 0
		for pay in payment:
			if pay == -49:
				names[i] = prepaid_seat_individuals[0]
			i += 1
		return names, payment
	
	@staticmethod
	def _pay_tally (names, pay):
		total_pay = {}
		i = 0
		for name in names:
			if name in total_pay:
				total_pay[name] += pay[i]
			else:
				total_pay[name] = pay[i]
			i += 1
		return total_pay

	@staticmethod
	def _hours_tally (names, hours):
		total_hours = {}
		for name in names:
			if names[0] != name:
				total_hours[name] = 0
		for hour in hours:
			i = 1
			for hour_per_name in hour[1:]:
				total_hours[names[i]] += hour_per_name
				i += 1
				
		return total_hours

	@classmethod
	def _import_timesheet_data (cls, file_name):
		data = cls._import_data_fillna(file_name)
		names = data.columns.values
		hours = data.iloc[:, :].values
		return names, hours

	@staticmethod
	def _format_names (total_pay, total_hours):
		correct_format = total_hours.keys()
		correct_format = [name for name in correct_format]
		temp_format = [name.split(' ')[-1] for name in correct_format]
		temp_pay = {}
		for name in total_pay.keys():
			last_name = name.split(',')[0]
			idx = temp_format.index(last_name)
			temp_pay[correct_format[idx]] = total_pay[name]
		return temp_pay
	
	@classmethod
	def allocate (cls, file1, file2):
		ts_names, ts_hours = cls._import_timesheet_data(file1)
		pr_names, pr_pay = cls._missing_name_for_prepaid_seat(file2)
		total_pay = cls._pay_tally(pr_names, pr_pay)
		total_hours = cls._hours_tally(ts_names, ts_hours)
		total_pay = cls._format_names(total_pay, total_hours)
		df = cls._allocate(total_pay, total_hours, ts_names, ts_hours)
		df.to_csv('allocation.csv', index=False)

	@staticmethod
	def _allocate (total_pay, total_hours, ts_names, ts_hours):
		new_allocation = []
		i = 0
		for hour in ts_hours:
			j = 1
			new_allocation.append([])
			for hour_per_name in hour[1:]:
				curr_name = ts_names[j]
				if curr_name in total_pay:
					allocation = hour_per_name / total_hours[curr_name] * total_pay[curr_name]
					new_allocation[i].append(allocation)
				j += 1
			i += 1
		x_lab = [name for name in ts_names if name in total_pay]
		x_lab.insert(0, '')
		y_lab = ts_hours[:,0]
		i = 0
		while i < len(y_lab):
			temp = new_allocation[i]
			temp.insert(0, y_lab[i])
			new_allocation[i] = temp
			i += 1
		df = pd.DataFrame(new_allocation, columns = x_lab)
		return df
