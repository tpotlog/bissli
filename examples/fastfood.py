##################################################
#Written by Tal Potlog 24-oct-2012               #
#                                                #
#This Example will demonstrate how to create a   #
#menus and a wizard                              #
##################################################

import snack
import bissli


screen=snack.SnackScreen()

HANBURGERS=(('160g','160g'),('250g','250g'),('300g','300g'))
LEVEL=(('Well Done','Well Done'),('Medium Well','Medium Well'),('rare','rare'))
SIDES=(('French Fries','French Fries'),('Curly Fries','Curly Fries'))
DRINKS=(('Cola','Cola'),('Diet Cola','Diet Cola'),('Orange Juice','Orange Juice'),('Grape Juice','Grape Juice'),('Water','Water'))
SIZE=(('Normal','Normal'),('Large','Large'),('Super Size','Super Size'))

Burger_Menu=bissli.WizardMenuForm(screen=screen,options=HANBURGERS,title='Select Hamburger Size')
Wellness_Menu=bissli.WizardMenuForm(screen=screen,options=LEVEL,title='Burger Welness')
SideDish_Menu=bissli.WizardMenuForm(screen=screen,options=SIDES,title='Side Dish')
Drinks_Menu=bissli.WizardMenuForm(screen=screen,options=DRINKS,title='Select A drink')
Size_Menu=bissli.WizardMenuForm(screen=screen,options=SIZE,title='Meal Size')


my_wizard=bissli.FormFlow([Burger_Menu,Wellness_Menu,SideDish_Menu,Drinks_Menu,Size_Menu])
for f in my_wizard:
    f.run()
screen.finish()

for f in my_wizard.FormsList:
    print '%s:%s' %(f.title,f.getData())