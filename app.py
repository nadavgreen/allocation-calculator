from allocator_module.allocator import Allocator

new_allocation = Allocator().allocate
new_allocation('timesheets.csv', 'payroll.csv')
