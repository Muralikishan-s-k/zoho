from django.db import models
from Register_Login.models import *

# Create your models here.

#---------------- models for zoho modules--------------------

class Unit(models.Model):
 
    unit_name=models.CharField(max_length=255)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)


class Items(models.Model):
   
    item_type=models.CharField(max_length=255)
    item_name=models.CharField(max_length=255)
   
    unit=models.ForeignKey(Unit,on_delete=models.CASCADE)
    hsn_code=models.IntegerField(null=True,blank=True)
    tax_reference=models.CharField(max_length=255,null=True)
    intrastate_tax=models.IntegerField(null=True,blank=True)
    interstate_tax=models.IntegerField(null=True,blank=True)

    selling_price=models.IntegerField(null=True,blank=True)
    sales_account=models.CharField(max_length=255)
    sales_description=models.CharField(max_length=255)

    purchase_price=models.IntegerField(null=True,blank=True)
    purchase_account=models.CharField(max_length=255)
    purchase_description=models.CharField(max_length=255)
   
    minimum_stock_to_maintain=models.IntegerField(blank=True,null=True)  
    activation_tag=models.CharField(max_length=255,default='active')
    inventory_account=models.CharField(max_length=255,null=True)

    date=models.DateTimeField(auto_now_add=True)                                       

    opening_stock=models.IntegerField(blank=True,null=True,default=0)
    current_stock=models.IntegerField(blank=True,null=True,default=0)
    opening_stock_per_unit=models.IntegerField(blank=True,null=True,)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    login_details=models.ForeignKey(LoginDetails,on_delete=models.CASCADE)

    type=models.CharField(max_length=255,blank=True,null=True,)

    track_inventory=models.IntegerField(blank=True,null=True)


class Inventory_adjustment(models.Model):
    Mode_of_adjustment=models.CharField(max_length=255,null=True)
    Reference_number=models.CharField(max_length=255,null=True)
    Adjusting_date=models.DateField(max_length=255,null=True,blank=True)  
    Account=models.CharField(max_length=100,null=True,blank=True)  
    Reason=models.CharField(max_length=255,null=True)
    Description=models.CharField(max_length=255,null=True)
    Attach_file = models.FileField(upload_to='inventory_attachments/', null=True, blank=True)
    Status=models.CharField(max_length=255,null=True)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    login_details=models.ForeignKey(LoginDetails,on_delete=models.CASCADE)

class Inventory_adjustment_items(models.Model):
    items=models.ForeignKey(Items,on_delete=models.CASCADE)  
    Quantity_available=models.IntegerField(blank=True,null=True,default=0)
    New_quantity_inhand=models.IntegerField(blank=True,null=True,default=0) 
    Quantity_adjusted=models.IntegerField(blank=True,null=True,default=0) 
    Current_value=models.IntegerField(blank=True,null=True,default=0)
    Changed_value=models.IntegerField(blank=True,null=True,default=0)
    Adjusted_value=models.IntegerField(blank=True,null=True,default=0)
    inventory_adjustment=models.ForeignKey(Inventory_adjustment,on_delete=models.CASCADE)
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    login_details=models.ForeignKey(LoginDetails,on_delete=models.CASCADE)


class Inventory_adjustment_history(models.Model):
    company=models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    login_details=models.ForeignKey(LoginDetails,on_delete=models.CASCADE)
    inventory_adjustment=models.ForeignKey(Inventory_adjustment,on_delete=models.CASCADE)
    Date=models.DateField(max_length=255,null=True,blank=True)
    Action=models.CharField(max_length=255,null=True)



    