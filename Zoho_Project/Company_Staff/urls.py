from django.urls import path
from . import views


urlpatterns = [
    # -------------------------------Company section--------------------------------
    path('Company/Dashboard',views.company_dashboard,name='company_dashboard'),
    path('Company/Staff-Request',views.company_staff_request,name='company_staff_request'),
    path('Company/Staff-Request/Accept/<int:pk>',views.staff_request_accept,name='staff_request_accept'),
    path('Company/Staff-Request/Reject/<int:pk>',views.staff_request_reject,name='staff_request_reject'),
    path('Company/All-Staffs',views.company_all_staff,name='company_all_staff'),
    path('Company/Staff-Approval/Cancel/<int:pk>',views.staff_approval_cancel,name='staff_approval_cancel'),
    path('Company/Profile',views.company_profile,name='company_profile'),
    path('Company/Profile-Editpage',views.company_profile_editpage,name='company_profile_editpage'),
    path('Company/Profile/Edit/Basicdetails',views.company_profile_basicdetails_edit,name='company_profile_basicdetails_edit'),
    path('Company/Password_Change',views.company_password_change,name='company_password_change'),
    path('Company/Profile/Edit/Companydetails',views.company_profile_companydetails_edit,name='company_profile_companydetails_edit'),
    path('Company/Module-Editpage',views.company_module_editpage,name='company_module_editpage'),
    path('Company/Module-Edit',views.company_module_edit,name='company_module_edit'),
    path('Company/Renew/Payment_terms',views.company_renew_terms,name='company_renew_terms'),







    # -------------------------------Staff section--------------------------------
    path('Staff/Dashboard',views.staff_dashboard,name='staff_dashboard'),
    path('Staff/Profile',views.staff_profile,name='staff_profile'),
    path('Staff/Profile-Editpage',views.staff_profile_editpage,name='staff_profile_editpage'),
    path('Staff/Profile/Edit/details',views.staff_profile_details_edit,name='staff_profile_details_edit'),
    path('Staff/Password_Change',views.staff_password_change,name='staff_password_change'),



    # -------------------------------Zoho Modules section--------------------------------
    path('zohomodules/stock_adjustment/items_list',views.items_list,name='items_list'),
    path('zohomodules/stock_adjustment/create_adjustment',views.create_adjustment,name='create_adjustment'),
    path('get-item-stock/', views.get_item_stock, name='get_item_stock'),
    path('zohomodules/stock_adjustment/create_adjustment_value',views.create_adjustment_value,name='create_adjustment_value'),
    path('get-item-price/', views.get_item_price, name='get_item_price'),    
    path('zohomodules/stock_adjustment/quantity',views.quantity,name='quantity'),
    path('zohomodules/stock_adjustment/value',views.value,name='value'),   
    path('zohomodules/stock_adjustment/items_list/adjustment_overview',views.adjustment_overview,name='adjustment_overview'),
    path('itemdetail/<int:pk>',views.itemdetail,name='itemdetail'),
    path('stockedit/<int:pk>',views.stockedit,name='stockedit'),
    path('stockdelete/<int:pk>',views.stockdelete,name='stockdelete'),
    path('add_comment/<int:pk>',views.add_comment,name='add_comment'),
    path('stockeditdb/<int:pk>',views.stockeditdb,name='stockeditdb'),
    path('itemadd',views.itemadd,name='itemadd'),
    path('itemadd1',views.itemadd1,name='itemadd1'),
    path('attach/<int:pk>',views.attach,name='attach')
    
    
  
    
]