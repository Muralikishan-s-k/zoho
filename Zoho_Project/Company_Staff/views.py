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
from docx import Document
from docx.shared import Pt
import os
from django.core.mail import send_mail
import requests
from io import BytesIO


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
                adjustment1=Inventory_adjustment.objects.all()
                adjustment2=Inventory_adjustment_items.objects.all()
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                        'adjustment1':adjustment1,
                        'adjustment2':adjustment2
                }
                
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
                accounts=Chart_of_Accounts.objects.all()
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,
                    'account':accounts,
                }
                
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

from django.http import JsonResponse

def get_item_stock(request):
    if request.method == 'GET':
        item_id = request.GET.get('id')
        item=Items.objects.get(id=item_id)
        stock = item.current_stock  # Implement this function as needed
        return JsonResponse({'stock': stock})
    return JsonResponse({'error': 'Invalid request'})     

def create_adjustment_value(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                accounts=Chart_of_Accounts.objects.all()
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company,activation_tag='active')
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                        'account':accounts,
                }
                
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

def get_item_price(request):
    if request.method == 'GET':
        item_id = request.GET.get('id')
        item=Items.objects.get(id=item_id) 
        print('item',item)      
        price = int(item.current_stock) * int(item.purchase_price)
        return JsonResponse({'price': price})
    return JsonResponse({'error': 'Invalid request'})

 

def generate_unique_reference_number():
    latest_id = Inventory_adjustment.objects.all().aggregate(Max('id'))['id__max']
    next_id = latest_id + 1 if latest_id is not None else 1
    return str(next_id)



def quantity(request):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':                
            dash_details = StaffDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                mode1=request.POST.get('mode1')
                ref1 = generate_unique_reference_number()
                date1=request.POST.get('date1')
                account1=request.POST.get('account1')
                reason1=request.POST.get('reason1')
                desc1=request.POST.get('desc1')
                items=tuple(request.POST.getlist('item1'))
                print(items) 
                                            
                currentstock=tuple(request.POST.getlist('current_stock'))                
                newquantity=tuple(request.POST.getlist('new-quantity'))
                quantityadjusted=tuple(request.POST.getlist('quantity-adjusted'))
                file1 = request.FILES.get('file1')
                company_details = dash_details.company
                if 'draft' in request.POST:
                    status = 'draft'
                else:
                    status = 'saved'
                adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                             Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=company_details,
                                             login_details=log_details)
                adjustment1.save()

                for item_id, stock_value in zip(items, newquantity):
                    item = Items.objects.get(id=item_id)
                    print(item,stock_value) 
                    item.current_stock = stock_value
                    item.save()
                
                for item_id, stock_value, changed_value, adjusted_value in zip(items, currentstock, newquantity, quantityadjusted):
                       item = Items.objects.get(id=item_id)
                       adjustment2 = Inventory_adjustment_items.objects.create(
                           items=item,
                           Quantity_available=stock_value,
                           New_quantity_inhand=changed_value,
                           Quantity_adjusted=adjusted_value,
                           company=company_details,
                           login_details=log_details,
                           inventory_adjustment=adjustment1
                           
                       )
                       adjustment2.save()
                
                adjustment3=Inventory_adjustment_history(company=company_details,Action='created',
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                                                             
                adjustment2.save()
                adjustment3.save()               
                return redirect('items_list')                  
        if log_details.user_type == 'Company':            
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                mode1=request.POST.get('mode1')
                ref1 = generate_unique_reference_number()
                date1=request.POST.get('date1')
                account1=request.POST.get('account1')
                reason1=request.POST.get('reason1')
                desc1=request.POST.get('desc1')
                items=tuple(request.POST.getlist('item1'))
                print(items)                              
                currentstock=tuple(request.POST.getlist('current_stock'))
                # print(currentstock)                
                newquantity=tuple(request.POST.getlist('new-quantity'))
                # print(newquantity)
                quantityadjusted=tuple(request.POST.getlist('quantity-adjusted'))
                # print(quantityadjusted)
                file1 = request.FILES.get('file1')
                
                if 'draft' in request.POST:
                    status = 'draft'
                else:
                    status = 'saved'
                adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                             Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=dash_details,
                                             login_details=log_details)
                adjustment1.save()

                for item_id, stock_value in zip(items, newquantity):
                    item = Items.objects.get(id=item_id)
                    print(item,stock_value) 
                    item.current_stock = stock_value
                    item.save()

                

                for item_id, stock_value, changed_value, adjusted_value in zip(items, currentstock, newquantity, quantityadjusted):
                       item = Items.objects.get(id=item_id)
                       adjustment2 = Inventory_adjustment_items.objects.create(
                           items=item,
                           Quantity_available=stock_value,
                           New_quantity_inhand=changed_value,
                           Quantity_adjusted=adjusted_value,
                           company=dash_details,
                           login_details=log_details,
                           inventory_adjustment=adjustment1
                           
                       )
                       adjustment2.save()
                
                adjustment3=Inventory_adjustment_history(company=dash_details,Action='created',
                                                   login_details=log_details,inventory_adjustment=adjustment1)
                                                             
                adjustment2.save()
                adjustment3.save()               
                return redirect('items_list')
            return render(request,"zohomodules/stock_adjustment/create_adjustment_itemquantity.html")
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
     
def generate_reference_number():
    latest_id = Inventory_adjustment.objects.all().aggregate(Max('id'))['id__max']
    next_id = latest_id + 1 if latest_id is not None else 1
    return str(next_id)
     

def value(request):
        if 'login_id' in request.session:
           log_id = request.session['login_id']
           if 'login_id' not in request.session:
               return redirect('/')
           log_details= LoginDetails.objects.get(id=log_id)
           if log_details.user_type == 'Staff':                
                dash_details = StaffDetails.objects.get(login_details=log_details)
                if request.method =='POST':
                   mode1=request.POST.get('mode2')
                   print(mode1)
                   ref1=generate_reference_number()
                   date1=request.POST.get('date2')
                   account1=request.POST.get('account2')
                   reason1=request.POST.get('reason2')
                   desc1=request.POST.get('desc2')                   
                   items  = tuple(request.POST.getlist("item2"))                                                   
                   currentstock = tuple(request.POST.getlist("stock_value"))                                    
                   newquantity = tuple(request.POST.getlist("changedvalue"))                   
                   quantityadjusted = tuple(request.POST.getlist("adjustedvalue"))
                   file1 = request.FILES.get('file2')
                   company_details = dash_details.company
                   if 'draft' in request.POST:
                       status = 'draft'
                   else:
                       status = 'saved'
                   adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                                Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=company_details,
                                                login_details=log_details)
                   adjustment1.save()
                   for item_id, stock_value, changed_value, adjusted_value in zip(items, currentstock, newquantity, quantityadjusted):
                       item = Items.objects.get(id=item_id)
                       adjustment2 = Inventory_adjustment_items.objects.create(
                           items=item,
                           Current_value=stock_value,
                           Changed_value=changed_value,
                           Adjusted_value=adjusted_value,
                           company=company_details,
                           login_details=log_details,
                           inventory_adjustment=adjustment1                           
                       )
                       adjustment2.save()    
                   adjustment3=Inventory_adjustment_history(company=company_details,Action='created',
                                                      login_details=log_details,inventory_adjustment=adjustment1)                                       
                   adjustment3.save()            
                   return redirect('items_list')                       
           if log_details.user_type == 'Company':            
               dash_details = CompanyDetails.objects.get(login_details=log_details)
               if request.method =='POST':
                   mode1=request.POST.get('mode2')                 
                   ref1=generate_reference_number()
                   date1=request.POST.get('date2')
                   account1=request.POST.get('account2')
                   reason1=request.POST.get('reason2')
                   desc1=request.POST.get('desc2')                   
                   items  = tuple(request.POST.getlist("item2"))                                                   
                   currentstock = tuple(request.POST.getlist("stock_value"))                                    
                   newquantity = tuple(request.POST.getlist("changedvalue"))                   
                   quantityadjusted = tuple(request.POST.getlist("adjustedvalue"))
                   file1 = request.FILES.get('file2')
                   if 'draft' in request.POST:
                       status = 'draft'
                   else:
                       status = 'saved'
                   adjustment1=Inventory_adjustment(Mode_of_adjustment=mode1,Reference_number=ref1,Adjusting_date=date1,Account=account1,
                                                Reason=reason1,Description=desc1,Attach_file=file1,Status=status,company=dash_details,
                                                login_details=log_details)
                   adjustment1.save()
                   for item_id, stock_value, changed_value, adjusted_value in zip(items, currentstock, newquantity, quantityadjusted):
                       item = Items.objects.get(id=item_id)
                       adjustment2 = Inventory_adjustment_items.objects.create(
                           items=item,
                           Current_value=stock_value,
                           Changed_value=changed_value,
                           Adjusted_value=adjusted_value,
                           company=dash_details,
                           login_details=log_details,
                           inventory_adjustment=adjustment1                           
                       )
                       adjustment2.save()    
                   adjustment3=Inventory_adjustment_history(company=dash_details,Action='created',
                                                      login_details=log_details,inventory_adjustment=adjustment1)                                       
                   adjustment3.save()            
                   return redirect('items_list')
               return render(request,"zohomodules/stock_adjustment/create_adjustment_itemvalue.html")
           return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
          
     

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
                adjustment1=Inventory_adjustment.objects.all()
                adjustment2=Inventory_adjustment_items.objects.all()
                context = {
                        'details': dash_details,
                        'item':item,
                        'allmodules': allmodules,
                        'adjustment2':adjustment1,
                        'adjustment':adjustment2
                }
                
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
                    'adjustment2':adjustment1,
                    'adjustment':adjustment2
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
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
            
                context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,                                      
                    'adjustment':adjustment2,
                    'adjustment2':adjust,
                    'adjustment3':adjustment_history_entry

                }
                
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')                     
            adjustment2=Inventory_adjustment.objects.get(id=pk)
            adjust=Inventory_adjustment.objects.all()                      
            adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
            
            context = {
                    'details': dash_details,
                    'item': item,
                    'allmodules': allmodules,                                       
                    'adjustment':adjustment2,
                    'adjustment2':adjust,
                    'adjustment3':adjustment_history_entry

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
                adjustment2 = Inventory_adjustment.objects.get(id=pk)
                adjust = Inventory_adjustment_items.objects.filter(inventory_adjustment=adjustment2)          
                itemz=Items.objects.filter(activation_tag='active')
                # stock_value = adjust.items.current_stock * adjust.items.purchase_price
                accounts=Chart_of_Accounts.objects.all()              
                context = {
                        'details': dash_details,
                        'item':item,
                        'itemz':itemz,
                        'allmodules': allmodules,                       
                        'adjustment2':adjustment2,
                        'adjust':adjust,
                        'account':accounts,
                        # 'stock_value': stock_value,
                }
                if adjustment2.Mode_of_adjustment == 'Quantity adjustment':
                    return render(request, 'zohomodules/stock_adjustment/quantityedit.html', context)
                elif adjustment2.Mode_of_adjustment == 'Value adjustment':
                    return render(request, 'zohomodules/stock_adjustment/valueedit.html', context)
                
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')           
            adjustment2 = Inventory_adjustment.objects.get(id=pk)
            adjust = Inventory_adjustment_items.objects.filter(inventory_adjustment=adjustment2)          
            itemz=Items.objects.filter(activation_tag='active')
            # stock_value = adjust.items.current_stock * adjust.items.purchase_price
            accounts=Chart_of_Accounts.objects.all()
            context = {
                    'details': dash_details,
                    'item': item,
                    'itemz':itemz,
                    'allmodules': allmodules,                  
                    'adjustment2':adjustment2,
                    'adjust':adjust,
                    'account':accounts,
                    # 'stock_value': stock_value,
            }
            if adjustment2.Mode_of_adjustment == 'Quantity adjustment':
                return render(request, 'zohomodules/stock_adjustment/quantityedit.html', context)
            elif adjustment2.Mode_of_adjustment == 'Value adjustment':
                return render(request, 'zohomodules/stock_adjustment/valueedit.html', context)
            
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')
     
def stockdelete(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company' or log_details.user_type == 'Staff':                                  
            adjustment2=Inventory_adjustment.objects.get(id=pk)            
            adjustment2.delete()           
            return redirect('adjustment_overview')
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html') 

def convert(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)        
        if log_details.user_type == 'Company' or log_details.user_type == 'Staff':                                  
            adjustment2=Inventory_adjustment.objects.get(id=pk)            
            adjustment2.Status='saved'
            adjustment2.save()           
            return redirect('itemdetail',pk=adjustment2.id)
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')         


def add_comment(request, pk):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details = LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
            if request.method == 'POST':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')               
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()
                adjustments=Inventory_adjustment_items.objects.get(inventory_adjustment=adjustment2)                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustments':adjustments,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                comment = request.POST.get('commentText')
                adjustments.Comment = comment
                adjustments.save()               
                return render(request,'zohomodules/stock_adjustment/adjustment_overview.html',context)
        if log_details.user_type == 'Company':            
            if request.method == 'POST':
                dash_details = CompanyDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details)
                allmodules= ZohoModules.objects.get(company=dash_details,status='New')               
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()
                adjustments=Inventory_adjustment_items.objects.get(inventory_adjustment=adjustment2)                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustments':adjustments,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                comment = request.POST.get('commentText')
                adjustments.Comment = comment
                adjustments.save()               
                return render(request,'zohomodules/stock_adjustment/adjustment_overview.html',context)           
            return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')
    return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')
     

def quantityedit(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':           
            if request.method =='POST':
                log_details= LoginDetails.objects.get(id=log_id)
                edit2=Inventory_adjustment.objects.get(id=pk)
                edit=Inventory_adjustment_items.objects.filter(inventory_adjustment=edit2)
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')         
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                edit3 = Inventory_adjustment_history.objects.get(inventory_adjustment=edit2)                                                   
                edit2.Mode_of_adjustment=request.POST.get('mode')
                edit2.Reason=request.POST.get('reason')
                edit2.Account=request.POST.get('account')
                edit2.Description=request.POST.get('description')
                edit2.Reference_number=request.POST.get('refno')
                edit2.Adjusting_date=request.POST.get('date')
                edit3.Date=request.POST.get('date')
                edit3.Action='edited'
                if 'draft' in request.POST:
                    edit2.Status = 'draft'
                else:
                    edit2.Status = 'saved'  
                edit2.save()
                edit3.save()
                edit.delete() 

                items=request.POST.getlist('item') 
                                                             
                quantity_available=tuple(request.POST.getlist('quantity-available'))
                                
                new_quantity_inhand=tuple(request.POST.getlist('quantity-inhand'))
                 
                quantity_adjusted=tuple(request.POST.getlist('quantity-adjusted'))

                for item_id, stock_value in zip(items, new_quantity_inhand):
                    item = Items.objects.get(id=item_id)                  
                    item.current_stock = stock_value
                    item.save()
                                
                                                                                     
                for item_id, quantityavailable, newquantity_inhand, quantityadjusted in zip(items, quantity_available,new_quantity_inhand, quantity_adjusted):
                       item = Items.objects.get(id=item_id)
                       adjust2 = Inventory_adjustment_items.objects.create(
                        items=item,
                        company=dash_details,
                        login_details=log_details,
                        inventory_adjustment=edit2,
                        Quantity_available=quantityavailable,
                        New_quantity_inhand=newquantity_inhand,
                        Quantity_adjusted=quantityadjusted                       
                       )                
                       adjust2.save()                                                                                                                  
                                            
                return redirect('itemdetail',pk=edit2.id)                    
        if log_details.user_type == 'Company':                                  
            if request.method =='POST':
                
                edit2=Inventory_adjustment.objects.get(id=pk)
                edit=Inventory_adjustment_items.objects.filter(inventory_adjustment=edit2)
                dash_details = CompanyDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details)
                allmodules= ZohoModules.objects.get(company=dash_details,status='New')          
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                edit3 = Inventory_adjustment_history.objects.get(inventory_adjustment=edit2)                                                   
                edit2.Mode_of_adjustment=request.POST.get('mode')
                edit2.Reason=request.POST.get('reason')
                edit2.Account=request.POST.get('account')
                edit2.Description=request.POST.get('description')
                edit2.Reference_number=request.POST.get('refno')
                edit2.Adjusting_date=request.POST.get('date')
                edit3.Date=request.POST.get('date')
                edit3.Action='edited'
                if 'draft' in request.POST:
                    edit2.Status = 'draft'
                else:
                    edit2.Status = 'saved'  
                edit2.save()
                edit3.save()
                edit.delete() 

                items=request.POST.getlist('item') 

                quantity_available=tuple(request.POST.getlist('quantity-available'))
                                
                new_quantity_inhand=tuple(request.POST.getlist('quantity-inhand'))
                 
                quantity_adjusted=tuple(request.POST.getlist('quantity-adjusted'))

                for item_id, stock_value in zip(items, new_quantity_inhand):
                    item = Items.objects.get(id=item_id)                  
                    item.current_stock = stock_value
                    item.save()
                                
                                                                                     
                for item_id, quantityavailable, newquantity_inhand, quantityadjusted in zip(items, quantity_available,new_quantity_inhand, quantity_adjusted):
                       item = Items.objects.get(id=item_id)
                       adjust2 = Inventory_adjustment_items.objects.create(
                        items=item,
                        company=dash_details,
                        login_details=log_details,
                        inventory_adjustment=edit2,
                        Quantity_available=quantityavailable,
                        New_quantity_inhand=newquantity_inhand,
                        Quantity_adjusted=quantityadjusted                       
                       )                
                       adjust2.save()                                                                                                                                
                
                                            
                return redirect('itemdetail',pk=edit2.id)
            return render(request,"zohomodules/stock_adjustment/adjustment_overview.html",context)
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
     
def valueedit(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
            log_details= LoginDetails.objects.get(id=log_id)
            if request.method =='POST':
                edit2=Inventory_adjustment.objects.get(id=pk)
                edit=Inventory_adjustment_items.objects.filter(inventory_adjustment=edit2)
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                edit3 = Inventory_adjustment_history.objects.get(inventory_adjustment=edit2)                                          
                edit2.Mode_of_adjustment=request.POST.get('mode')
                edit2.Reason=request.POST.get('reason')
                edit2.Account=request.POST.get('account')
                edit2.Description=request.POST.get('description')
                edit2.Reference_number=request.POST.get('refno') 
                edit2.Adjusting_date=request.POST.get('date')
                edit3.Date=request.POST.get('date')
                edit3.Action='edited'
                if 'draft' in request.POST:
                    edit2.Status = 'draft'
                else:
                    edit2.Status = 'saved'  
                edit2.save()
                edit3.save()
                edit.delete()                                                               
                current_value=tuple(request.POST.getlist('currentvalue'))
                changed_value=tuple(request.POST.getlist('changedvalue'))
                adjusted_value=tuple(request.POST.getlist('adjustedvalue'))
                items=tuple(request.POST.getlist('item'))                                
                for item_id,currentvalue,changedvalue,adjustedvalue in zip(items,current_value,changed_value,adjusted_value):
                       item = Items.objects.get(id=item_id)
                       adjust2 = Inventory_adjustment_items.objects.create(
                            items=item,
                            company=dash_details,
                            login_details=log_details,
                            inventory_adjustment=edit2,                       
                            Current_value=currentvalue,
                            Changed_value=changedvalue,
                            Adjusted_value=adjustedvalue,                      
                       )                
                       adjust2.save()                                                                                                       
                
                                            
                return redirect('itemdetail',pk=edit2.id)                    
        if log_details.user_type == 'Company':                       
            if request.method =='POST':
                edit2=Inventory_adjustment.objects.get(id=pk)
                edit=Inventory_adjustment_items.objects.filter(inventory_adjustment=edit2)
                dash_details = CompanyDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details)
                allmodules= ZohoModules.objects.get(company=dash_details,status='New')              
                adjustment2=Inventory_adjustment.objects.get(id=pk)
                adjust=Inventory_adjustment.objects.all()                      
                adjustment_history_entry = Inventory_adjustment_history.objects.get(inventory_adjustment=adjustment2)
                
                context = {
                        'details': dash_details,
                        'item': item,
                        'allmodules': allmodules,                                       
                        'adjustment':adjustment2,
                        'adjustment2':adjust,
                        'adjustment3':adjustment_history_entry

                }
                edit3 = Inventory_adjustment_history.objects.get(inventory_adjustment=edit2)                             
                edit2.Mode_of_adjustment=request.POST.get('mode')
                edit2.Reason=request.POST.get('reason')
                edit2.Account=request.POST.get('account')
                edit2.Description=request.POST.get('description')
                edit2.Reference_number=request.POST.get('refno') 
                edit2.Adjusting_date=request.POST.get('date')
                edit3.Date=request.POST.get('date')
                edit3.Action='edited' 
                if 'draft' in request.POST:
                    edit2.Status = 'draft'
                else:
                    edit2.Status = 'saved'  
                edit2.save()
                edit3.save()
                edit.delete()                                                              
                current_value=tuple(request.POST.getlist('currentvalue'))
                print(current_value)
                changed_value=tuple(request.POST.getlist('changedvalue'))
                print(changed_value)
                adjusted_value=tuple(request.POST.getlist('adjustedvalue'))
                print(adjusted_value)
                items=tuple(request.POST.getlist('item'))                                
                for item_id,currentvalue,changedvalue,adjustedvalue in zip(items,current_value,changed_value,adjusted_value):
                       item = Items.objects.get(id=item_id)
                       adjust2 = Inventory_adjustment_items.objects.create(
                            items=item,
                            company=dash_details,
                            login_details=log_details,
                            inventory_adjustment=edit2,                       
                            Current_value=currentvalue,
                            Changed_value=changedvalue,
                            Adjusted_value=adjustedvalue,                      
                       )                
                       adjust2.save()                                                                                                       
               
                                            
                return redirect('itemdetail',pk=edit2.id)
            return render(request,"zohomodules/stock_adjustment/adjustment_overview.html",context)
        return render(request,'zohomodules/stock_adjustment/create_adjustment.html')
     

def send_whatsapp_message(request):
    if request.method == 'POST':
        # Extract details from the request
        mode_of_adjustment = request.POST.get('value1')
        reference_number = request.POST.get('value2')
        adjusting_date = request.POST.get('value3')
        account = request.POST.get('value4')
        reason = request.POST.get('value5')

        # Generate the PDF file
        pdf_filename = 'adjustment_details.pdf'
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

        # Example: Use reportlab or any library to generate the PDF file
        # Replace this with your own PDF generation logic
        # GeneratePDF(pdf_path, mode_of_adjustment, reference_number, adjusting_date, account, reason)

        # Compose the message with a link to download the PDF
        pdf_url = f"{request.scheme}://{request.get_host()}/{settings.MEDIA_URL}{pdf_filename}"
        message = f"Mode of Adjustment: {mode_of_adjustment}\n"
        message += f"Reference Number: {reference_number}\n"
        message += f"Adjusting Date: {adjusting_date}\n"
        message += f"Account: {account}\n"
        message += f"Reason: {reason}\n"
        message += f"Download PDF: {pdf_url}"

        # Send message via WhatsApp using your configured API
        whatsapp_api_url = 'https://api.whatsapp.com/send'
        response = requests.post(whatsapp_api_url, data={'message': message})

        if response.status_code == 200:
            return JsonResponse({'status': 'Message sent successfully'})
        else:
            return JsonResponse({'status': 'Failed to send message'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
     
     
def itemadd(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
            log_details= LoginDetails.objects.get(id=log_id)
            dash_details = StaffDetails.objects.get(login_details=log_details)
            companyid=dash_details.company
            if request.method =='POST':
                itemadd = request.POST.get('items')                              
                adjustment4 = Items(item_name=itemadd,current_stock=0,purchase_price=0, unit_id=2, company=companyid, login_details=log_details)                              
                adjustment4.save()  

                # Return the newly added item data
                return JsonResponse({'success': True, 'item_id': adjustment4.id, 'item_name': adjustment4.item_name})
            
                    
        if log_details.user_type == 'Company':            
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                itemadd = request.POST.get('items')                                             
                adjustment4 = Items(item_name=itemadd,current_stock=0,purchase_price=0, unit_id=2, company=dash_details, login_details=log_details)                              
                adjustment4.save()  

                # Return the newly added item data
                return JsonResponse({'success': True, 'item_id': adjustment4.id, 'item_name': adjustment4.item_name})
            
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        return JsonResponse({'error': 'User is not a company'}, status=403)
    
    return JsonResponse({'error': 'Login session not found'}, status=401)

def itemadd1(request):
    if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
            log_details= LoginDetails.objects.get(id=log_id)
            dash_details = StaffDetails.objects.get(login_details=log_details)
            companyid=dash_details.company
            if request.method =='POST':
                itemadd = request.POST.get('items')                              
                adjustment4 = Items(item_name=itemadd,current_stock=0,purchase_price=0, unit_id=2, company=companyid, login_details=log_details)                              
                adjustment4.save()  

                # Return the newly added item data
                return JsonResponse({'success': True, 'item_id': adjustment4.id, 'item_name': adjustment4.item_name})
                               
        if log_details.user_type == 'Company':            
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            if request.method =='POST':
                itemadd = request.POST.get('items')                              
                adjustment4 = Items(item_name=itemadd,current_stock=0,purchase_price=0, unit_id=2, company=dash_details, login_details=log_details)                              
                adjustment4.save()  

                # Return the newly added item data
                return JsonResponse({'success': True, 'item_id': adjustment4.id, 'item_name': adjustment4.item_name})
            
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
        return JsonResponse({'error': 'User is not a company'}, status=403)
    
    return JsonResponse({'error': 'Login session not found'}, status=401)   




def attach(request, pk):
    if 'login_id' in request.session:
        log_id = request.session.get('login_id')
        if not log_id:
            return JsonResponse({'error': 'Invalid request'})
        
        log_details = LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
            log_details= LoginDetails.objects.get(id=log_id)
            if request.method == 'POST':             
                adjustment2 = Inventory_adjustment.objects.get(id=pk)  
                if request.FILES:
                    file_obj = request.FILES['file1']
                    if adjustment2.Attach_file:
                        os.remove(adjustment2.Attach_file.path)
                    adjustment2.Attach_file = file_obj
                    adjustment2.save()
                    return JsonResponse({'success': 'File attached successfully'})
                else:
                    return JsonResponse({'error': 'No file provided'})
        if log_details.user_type == 'Company':
            if request.method == 'POST':               
                adjustment2 = Inventory_adjustment.objects.get(id=pk)              
                if request.FILES:
                    file_obj = request.FILES['file1']
                    if adjustment2.Attach_file:
                        os.remove(adjustment2.Attach_file.path)
                    adjustment2.Attach_file = file_obj
                    adjustment2.save()
                    return JsonResponse({'success': 'File attached successfully'})
                else:
                    return JsonResponse({'error': 'No file provided'})
            else:
                return JsonResponse({'error': 'Invalid request'})
        else:
            return JsonResponse({'error': 'Unauthorized access'})
    else:
        return JsonResponse({'error': 'User not logged in'})    


def email(request,pk):
     if 'login_id' in request.session:
        log_id = request.session['login_id']
        if 'login_id' not in request.session:
            return redirect('/')
        log_details= LoginDetails.objects.get(id=log_id)
        if log_details.user_type == 'Staff':
                dash_details = StaffDetails.objects.get(login_details=log_details)
                item=Items.objects.filter(company=dash_details.company)
                allmodules= ZohoModules.objects.get(company=dash_details.company,status='New')
                if request.method == 'POST':
                # Retrieve form data
                    subject = request.POST.get('subject')
                    email = request.POST.get('email')
                    adjustment2 = Inventory_adjustment.objects.get(id=pk) 
                    message = f'Mode of adjustment: {adjustment2.Mode_of_adjustment}\nReference number: {adjustment2.Reference_number}\nAdjusting date: {adjustment2.Adjusting_date}\nAccount: {adjustment2.Account}\nReason: {adjustment2.Reason}\n'
        
                # Send email
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

                # Return JSON response
                    return JsonResponse({'message': 'Email sent successfully!'})
                else:
                # Handle GET request if needed
                    pass               
        if log_details.user_type == 'Company':
            dash_details = CompanyDetails.objects.get(login_details=log_details)
            item=Items.objects.filter(company=dash_details)
            allmodules= ZohoModules.objects.get(company=dash_details,status='New')            
            if request.method == 'POST':
        # Retrieve form data
                subject = request.POST.get('subject')
                email = request.POST.get('email')
                adjustment2 = Inventory_adjustment.objects.get(id=pk) 
                message = f'Mode of adjustment: {adjustment2.Mode_of_adjustment}\nReference number: {adjustment2.Reference_number}\nAdjusting date: {adjustment2.Adjusting_date}\nAccount: {adjustment2.Account}\nReason: {adjustment2.Reason}\n'
        
        # Send email
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        # Return JSON response
                return JsonResponse({'message': 'Email sent successfully!'})
            else:
        # Handle GET request if needed
                pass
        return render(request,'zohomodules/stock_adjustment/adjustment_overview.html')                   