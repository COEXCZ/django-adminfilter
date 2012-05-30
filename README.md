django-adminfilter
==================

The Django Admin Filter is a module for creating advanced filters in
Django Admin.

Installation and usage
======================
Requirements:

*    Django 1.3
*    django-mptt

#### settings.py ####

        TEMPLATE_CONTEXT_PROCESSORS += ('adminfilter.context_processors.filter_context_processor', )
        MIDDLEWARE_CLASSES += ('adminfilter.middleware.FilterMiddleware', )
        INSTALLED_APPS += ("admin_filter", )

#### templates/admin/change_list.html ####

The next step is to add the following line to the directory
'templates/admin/change_list.html' before the end tag </ form>
(there is only one </form> tag in the template)

        {% include "includes/filter_form_hidden.html" %}
        </ form>

#### forms.py ####
        import adminfilter

        ProductFilterForm class (adminfilter.FilterForm):
            """Product FilterForm for admin"""
            gender = admin_filter.ChoiceField(q='gender', choices=choices.GENDERS)
            city =  admin_filter.ChoiceField(q='feelings', choices=choices.CITY)

Parameter 'q' should contain name of the model attribute, where q='gender' q='city' creates the following query:

            Product.objects.filter(gender=value, city=value)

Another option is giving django.db.models.Q object to 'q' parameter:

            def custom_query (value):
                return Q(pub_date = value) | Q(pub_date = date (2005, 5, 6))

the query looks like this
            Product.objects.filter(
                Q(pub_date=value) | Q(pub_date=date(2005, 5, 6))
            )

List of available form fields:

*  Charfield
*  IntegerField
*  ChoiceField
*  DateField
*  TypedChoiceField
*  BooleanField
*  ModelChoiceField


#### admin.py ####

Change admin class to FilterAdmin:

        from adminfilter import FilterAdmin

        import project.product.forms ProductFilterForm

        class ProductAdmin(FilterAdmin):
            """
                Administration of Product Model
            """
            filter_form = ProductFilterForm
