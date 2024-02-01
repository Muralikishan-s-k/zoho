from django.shortcuts import render,redirect
from Register_Login.models import *
from Register_Login.views import logout
from django.contrib import messages
from django.conf import settings
from datetime import date
from datetime import datetime, timedelta
from Company_Staff.models import Items,Chart_of_Accounts,Inventory_adjustment,Inventory_adjustment_items,Inventory_adjustment_history
from openpyxl import Workbook
from django.http import HttpResponse
from openpyxl import load_workbook
from django.db.models import Max


# Create your views here.



# -------------------------------Company section--------------------------------

# company dashboard
def company_dashboard(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')

        # Calculate the date 20 days before the end date for payment term renew
        reminder_date = dash_details.End_date - timedelta(days=20)
        current_date = date.today()
        alert_message = current_date >= reminder_date

        # Calculate the number of days between the reminder date and end date
        days_left = (dash_details.End_date - current_date).days
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'alert_message':alert_message,
            'days_left':days_left,
        }
        return render(request, 'company/company_dash.html', context)
    else:
        return redirect('/')


# company staff request for login approval
def company_staff_request(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        staff_request=StaffDetails.objects.filter(company=dash_details.id, company_approval=0).order_by('-id')
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'requests':staff_request,
        }
        return render(request, 'company/staff_request.html', context)
    else:
        return redirect('/')

# company staff accept or reject
def staff_request_accept(request,pk):
    staff=StaffDetails.objects.get(id=pk)
    staff.company_approval=1
    staff.save()
    return redirect('company_staff_request')

def staff_request_reject(request,pk):
    staff=StaffDetails.objects.get(id=pk)
    login_details=LoginDetails.objects.get(id=staff.company.id)
    login_details.delete()
    staff.delete()
    return redirect('company_staff_request')


# All company staff view, cancel staff approval
def company_all_staff(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        all_staffs=StaffDetails.objects.filter(company=dash_details.id, company_approval=1).order_by('-id')
       
        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'staffs':all_staffs,
        }
        return render(request, 'company/all_staff_view.html', context)
    else:
        return redirect('/')

def staff_approval_cancel(request, pk):
    """
    Sets the company approval status to 2 for the specified staff member, effectively canceling staff approval.

    This function is designed to be used for canceling staff approval, and the company approval value is set to 2.
    This can be useful for identifying resigned staff under the company in the future.

    """
    staff = StaffDetails.objects.get(id=pk)
    staff.company_approval = 2
    staff.save()
    return redirect('company_all_staff')


# company profile, profile edit
def company_profile(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        terms=PaymentTerms.objects.all()

        # Calculate the date 20 days before the end date
        reminder_date = dash_details.End_date - timedelta(days=20)
        current_date = date.today()
        renew_button = current_date >= reminder_date

        context = {
            'details': dash_details,
            'allmodules': allmodules,
            'renew_button': renew_button,
            'terms':terms,
        }
        return render(request, 'company/company_profile.html', context)
    else:
        return redirect('/')

def company_profile_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'company/company_profile_editpage.html', context)
    else:
        return redirect('/')

def company_profile_basicdetails_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            log_details.first_name = request.POST.get('fname')
            log_details.last_name = request.POST.get('lname')
            log_details.email = request.POST.get('eid')
            log_details.username = request.POST.get('uname')
            log_details.save()
            messages.success(request,'Updated')
            return redirect('company_profile_editpage') 
        else:
            return redirect('company_profile_editpage') 

    else:
        return redirect('/')
    
def company_password_change(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            password = request.POST.get('pass')
            cpassword = request.POST.get('cpass')
            if password == cpassword:
                log_details.password=password
                log_details.save()

            messages.success(request,'Password Changed')
            return redirect('company_profile_editpage') 
        else:
            return redirect('company_profile_editpage') 

    else:
        return redirect('/')
       
def company_profile_companydetails_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details = LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)

        if request.method == 'POST':
            # Get data from the form
            gstno = request.POST.get('gstno')
            profile_pic = request.FILES.get('image')

            # Update the CompanyDetails object with form data
            dash_details.company_name = request.POST.get('cname')
            dash_details.contact = request.POST.get('phone')
            dash_details.address = request.POST.get('address')
            dash_details.city = request.POST.get('city')
            dash_details.state = request.POST.get('state')
            dash_details.country = request.POST.get('country')
            dash_details.pincode = request.POST.get('pincode')
            dash_details.pan_number = request.POST.get('pannumber')

            if gstno:
                dash_details.gst_no = gstno

            if profile_pic:
                dash_details.profile_pic = profile_pic

            dash_details.save()

            messages.success(request, 'Updated')
            return redirect('company_profile_editpage')
        else:
            return redirect('company_profile_editpage')
    else:
        return redirect('/')    

# company modules editpage
def company_module_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'company/company_module_editpage.html', context)
    else:
        return redirect('/')

def company_module_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details,status='New')

        if request.method == 'POST':
            # Retrieve values
            items = request.POST.get('items', 0)
            price_list = request.POST.get('price_list', 0)
            stock_adjustment = request.POST.get('stock_adjustment', 0)
            godown = request.POST.get('godown', 0)

            cash_in_hand = request.POST.get('cash_in_hand', 0)
            offline_banking = request.POST.get('offline_banking', 0)
            upi = request.POST.get('upi', 0)
            bank_holders = request.POST.get('bank_holders', 0)
            cheque = request.POST.get('cheque', 0)
            loan_account = request.POST.get('loan_account', 0)

            customers = request.POST.get('customers', 0)
            invoice = request.POST.get('invoice', 0)
            estimate = request.POST.get('estimate', 0)
            sales_order = request.POST.get('sales_order', 0)
            recurring_invoice = request.POST.get('recurring_invoice', 0)
            retainer_invoice = request.POST.get('retainer_invoice', 0)
            credit_note = request.POST.get('credit_note', 0)
            payment_received = request.POST.get('payment_received', 0)
            delivery_challan = request.POST.get('delivery_challan', 0)

            vendors = request.POST.get('vendors', 0)
            bills = request.POST.get('bills', 0)
            recurring_bills = request.POST.get('recurring_bills', 0)
            vendor_credit = request.POST.get('vendor_credit', 0)
            purchase_order = request.POST.get('purchase_order', 0)
            expenses = request.POST.get('expenses', 0)
            recurring_expenses = request.POST.get('recurring_expenses', 0)
            payment_made = request.POST.get('payment_made', 0)

            projects = request.POST.get('projects', 0)

            chart_of_accounts = request.POST.get('chart_of_accounts', 0)
            manual_journal = request.POST.get('manual_journal', 0)

            eway_bill = request.POST.get('ewaybill', 0)

            employees = request.POST.get('employees', 0)
            employees_loan = request.POST.get('employees_loan', 0)
            holiday = request.POST.get('holiday', 0)
            attendance = request.POST.get('attendance', 0)
            salary_details = request.POST.get('salary_details', 0)

            reports = request.POST.get('reports', 0)

            update_action=1
            status='Pending'

            # Create a new ZohoModules instance and save it to the database
            data = ZohoModules(
                company=dash_details,
                items=items, price_list=price_list, stock_adjustment=stock_adjustment, godown=godown,
                cash_in_hand=cash_in_hand, offline_banking=offline_banking, upi=upi, bank_holders=bank_holders,
                cheque=cheque, loan_account=loan_account,
                customers=customers, invoice=invoice, estimate=estimate, sales_order=sales_order,
                recurring_invoice=recurring_invoice, retainer_invoice=retainer_invoice, credit_note=credit_note,
                payment_received=payment_received, delivery_challan=delivery_challan,
                vendors=vendors, bills=bills, recurring_bills=recurring_bills, vendor_credit=vendor_credit,
                purchase_order=purchase_order, expenses=expenses, recurring_expenses=recurring_expenses,
                payment_made=payment_made,
                projects=projects,
                chart_of_accounts=chart_of_accounts, manual_journal=manual_journal,
                eway_bill=eway_bill,
                employees=employees, employees_loan=employees_loan, holiday=holiday,
                attendance=attendance, salary_details=salary_details,
                reports=reports,update_action=update_action,status=status    
            )
            data.save()
            messages.info(request,"Request sent successfully. Please wait for approval.")
            return redirect('company_module_editpage')
        else:
            return redirect('company_module_editpage')  
    else:
        return redirect('/')


def company_renew_terms(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = CompanyDetails.objects.get(login_details=log_details,superadmin_approval=1,Distributor_approval=1)
        if request.method == 'POST':
            select=request.POST['select']
            terms=PaymentTerms.objects.get(id=select)
            update_action=1
            status='Pending'
            newterms=PaymentTermsUpdates(
               company=dash_details,
               payment_term=terms,
               update_action=update_action,
               status=status 
            )
            newterms.save()
            messages.success(request,'Successfully requested an extension of payment terms. Please wait for approval.')
            return redirect('company_profile')
    else:
        return redirect('/')









# -------------------------------Staff section--------------------------------

# staff dashboard
def staff_dashboard(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context={
            'details':dash_details,
            'allmodules': allmodules,
        }
        return render(request,'staff/staff_dash.html',context)
    else:
        return redirect('/')


# staff profile
def staff_profile(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context={
            'details':dash_details,
            'allmodules': allmodules,
        }
        return render(request,'staff/staff_profile.html',context)
    else:
        return redirect('/')


def staff_profile_editpage(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
        context = {
            'details': dash_details,
            'allmodules': allmodules
        }
        return render(request, 'staff/staff_profile_editpage.html', context)
    else:
        return redirect('/')

def staff_profile_details_edit(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        dash_details = StaffDetails.objects.get(login_details=log_details,company_approval=1)
        if request.method == 'POST':
            # Get data from the form
            log_details.first_name = request.POST.get('fname')
            log_details.last_name = request.POST.get('lname')
            log_details.email = request.POST.get('eid')
            log_details.username = request.POST.get('uname')
            log_details.save()
            dash_details.contact = request.POST.get('phone')
            old=dash_details.image
            new=request.FILES.get('profile_pic')
            print(new,old)
            if old!=None and new==None:
                dash_details.image=old
            else:
                print(new)
                dash_details.image=new
            dash_details.save()
            messages.success(request,'Updated')
            return redirect('staff_profile_editpage') 
        else:
            return redirect('staff_profile_editpage') 

    else:
        return redirect('/')

def staff_password_change(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')

        log_details= LoginDetails.objects.get(id=log_id)
        if request.method == 'POST':
            # Get data from the form
            password = request.POST.get('pass')
            cpassword = request.POST.get('cpass')
            if password == cpassword:
                log_details.password=password
                log_details.save()

            messages.success(request,'Password Changed')
            return redirect('staff_profile_editpage') 
        else:
            return redirect('staff_profile_editpage') 

    else:
        return redirect('/')






# -------------------------------Zoho Modules section--------------------------------
    
def items_list(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            adjustment1=Inventory_adjustment.objects.all()
            adjustment2=Inventory_adjustment_items.objects.all()
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'adjustment1':adjustment1,
                    'adjustment2':adjustment2
            }
        return render(request,'zohomodules/stock_adjustment/items_list.html',context) 


def create_adjustment(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':            
            accounts=Chart_of_Accounts.objects.all()
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(activation_tag='active')
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'account':accounts,
            }
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html',context)
     

def create_adjustment_value(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company,activation_tag='active')
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            accounts=Chart_of_Accounts.objects.all()
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(activation_tag='active')
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'account':accounts,
            }
        return render(request,'zohomodules/stock_adjustment/create_adjustment_value.html',context)


def create_adjustment_itemvalue(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company,activation_tag='active')
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            accounts=Chart_of_Accounts.objects.all()
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item_instance = Items.objects.get(id=pk)

            # Calculate stock value
            stock_value = item_instance.current_stock * item_instance.purchase_price
            
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            context = {
                    'details': dash_details,
                    'item': item_instance,
                    'allmodules': allmodules,
                    'account':accounts,
                    'stock_value': stock_value,
                    
            }
        return render(request,'zohomodules/stock_adjustment/create_adjustment_itemvalue.html',context) 


def create_adjustment_itemquantity(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company,activation_tag='active')
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            accounts=Chart_of_Accounts.objects.all()
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.get(id=pk)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'account':accounts,
            }
        return render(request,'zohomodules/stock_adjustment/create_adjustment_itemquantity.html',context)


def generate_unique_reference_number():
    latest_reference_number = Inventory_adjustment.objects.all().aggregate(Max('Reference_number'))['Reference_number__max']
    if latest_reference_number:
        return str(int(latest_reference_number) + 1)
    else:
        return '1'

def quantity(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company':            
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                mode1=request.POST.get('mode1')
                ref1 = generate_unique_reference_number()
                date1=request.POST.get('date1')
                account1=request.POST.get('account1')
                reason1=request.POST.get('reason1')
                desc1=request.POST.get('desc1')
                item=request.POST.get('item1')
                item1=Items.objects.get(id=item)                
                currentstock=request.POST.get('current_stock')
                newquantity=request.POST.get('new-quantity')
                quantityadjusted=request.POST.get('quantity-adjusted')
                file1 = request.FILES.get('file1')
                if 'draft' in request.POST:
                    status = 'draft'
                else:
                    status = 'adjusted'
                adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                             Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=dash_details,
                                             login_details=log_details)
                adjustment2=Inventory_adjustment_items(items=item1,Quantity_available=currentstock,New_quantity_inhand=newquantity,
                                                   Quantity_adjusted=quantityadjusted,company=dash_details,
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                adjustment3=Inventory_adjustment_history(company=dash_details,Action='created',
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                adjustment1.save()
                
                adjustment2.save()
                adjustment3.save()               
                return redirect('items_list')
            return render(request,"zohomodules/stock_adjustment/create_adjustment_itemquantity.html")
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
     

def value(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company':            
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                mode1=request.POST.get('mode2')
                ref1=generate_unique_reference_number()
                date1=request.POST.get('date2')
                account1=request.POST.get('account2')
                reason1=request.POST.get('reason2')
                desc1=request.POST.get('desc2')
                item=request.POST.get('item2')
                item1=Items.objects.get(id=item)               
                currentstock=request.POST.get('stock_value')
                newquantity=request.POST.get('changedvalue')
                quantityadjusted=request.POST.get('adjustedvalue')
                file1 = request.FILES.get('file2')
                if 'draft' in request.POST:
                    status = 'draft'
                else:
                    status = 'adjusted'
                adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                             Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=dash_details,
                                             login_details=log_details)
                adjustment2=Inventory_adjustment_items(items=item1,Current_value=currentstock,Changed_value=newquantity,
                                                   Adjusted_value=quantityadjusted,company=dash_details,
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                adjustment3=Inventory_adjustment_history(company=dash_details,Action='created',
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                adjustment1.save()
                adjustment2.save()   
                adjustment3.save()            
                return redirect('items_list')
            return render(request,"zohomodules/stock_adjustment/create_adjustment_itemvalue.html")
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
          

def export_to_excel(request):
    adjustment_data = Inventory_adjustment.objects.all()  # Adjust this based on your actual model
    workbook = Workbook()
    sheet = workbook.active

    # Write headers
    headers = ["Sl.No", "Date", "Reason", "Description", "Ref.No", "Type", "Status"]
    sheet.append(headers)

    # Write data
    for index, s in enumerate(adjustment_data, start=1):
        row_data = [index, s.Adjusting_date, s.Reason, s.Description, s.Reference_number, s.Mode_of_adjustment, s.Status]
        sheet.append(row_data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=adjustment_data.xlsx'
    workbook.save(response)

    return response
     
def import_from_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        workbook = load_workbook(excel_file)
        sheet = workbook.active

        # Assuming the structure is the same as the export
        for row in sheet.iter_rows(min_row=2, values_only=True):
            _, adjusting_date, reason, description, reference_number, mode_of_adjustment, status = row

            # Create or update your model instance here
            adjustment_instance, created = Inventory_adjustment.objects.update_or_create(
                adjusting_date=adjusting_date,
                reason=reason,
                description=description,
                reference_number=reference_number,
                mode_of_adjustment=mode_of_adjustment,
                status=status,
            )

        return redirect('items_list')

    return render(request, 'zohomodules/stock_adjustment/items_list.html')

def adjustment_overview(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            adjustment1=Inventory_adjustment.objects.all()
            adjustment2=Inventory_adjustment_items.objects.all()
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'adjustment1':adjustment1,
                    'adjustment2':adjustment2
            }
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html',context)

def itemdetail(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            adjustment1=Inventory_adjustment.objects.all()
            adjustment2=Inventory_adjustment_items.objects.all()
            adjustments=Inventory_adjustment_items.objects.get(id=pk)           
            adjustment3 = Inventory_adjustment_history.objects.all()
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'adjustment1':adjustment1,
                    'adjustments':adjustments,
                    'adjustment2':adjustment2,
                    'adjustment3':adjustment3

            }
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html',context)  


def stockedit(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')
            adjustment1=Inventory_adjustment.objects.all()
            adjustment2=Inventory_adjustment_items.objects.get(id=pk)
            itemz=Items.objects.filter(activation_tag='active')
            stock_value = adjustment2.items.current_stock * adjustment2.items.purchase_price
            accounts=Chart_of_Accounts.objects.all()
            context = {
                    'details': dash_details,
                    'item': item,
                    'itemz':itemz,
                    'allmodules': allmodules,
                    'adjustment1':adjustment1,
                    'adjustment2':adjustment2,
                    'account':accounts,
                    'stock_value': stock_value,
            }
        return render(request,'zohomodules/stock_adjustment/stockedit.html',context)
     
def stockdelete(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                }
                return render(request,'zohomodules/items/items_list.html',context)
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')            
            adjustment2=Inventory_adjustment_items.objects.get(id=pk)            
            if adjustment2.inventory_adjustment:
                adjustment2.inventory_adjustment.delete()
            adjustment2.delete()           
            return redirect('adjustment_overview')
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')     


def add_comment(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company':
            adjustment2=Inventory_adjustment_items.objects.get(id=pk)                       
            if request.method =='POST':
                comment=request.POST.get('commentText')
                adjustment2.Comment=comment
                adjustment2.save()                                                  
                return redirect('adjustment_overview')
            return render(request,"zohomodules/stock_adjustment/adjustment_overview.html")
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
     

def stockeditdb(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company':            
            
            if request.method =='POST':
                edit=Inventory_adjustment_items.objects.get(id=pk)
                edit2 = edit.inventory_adjustment
                item=request.POST.get('item')
                item1=Items.objects.get(id=item)
                edit.items=item1             
                edit2.Mode_of_adjustment=request.POST.get('mode')
                edit2.Reason=request.POST.get('reason')
                edit2.Account=request.POST.get('account')
                edit2.Description=request.POST.get('description')                                               
                edit.Quantity_available=request.POST.get('quantity-available')
                edit.New_quantity_inhand=request.POST.get('quantity-inhand')
                edit.Quantity_adjusted=request.POST.get('quantity-adjusted')
                edit.Current_value=request.POST.get('currentvalue')
                edit.Changed_value=request.POST.get('changedvalue')
                edit.Adjusted_value=request.POST.get('adjustedvalue')
                edit2.Status=request.POST.get('status')             
                                
                edit.save()
                edit2.save()
                                            
                return redirect('adjustment_overview')
            return render(request,"zohomodules/stock_adjustment/adjustment_overview.html")
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
               