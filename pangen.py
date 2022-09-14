# programmer: Temi
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter.font import Font
import luhn
import sys
import numpy
import re

# Create instance
win = tk.Tk()

# Add a title
win.title("PAN GENERATOR")
#win.iconbitmap("C:\Users\Tello\Desktop\PAN.icon")
win.iconbitmap("/Users/temi/Downloads")
tabControl = ttk.Notebook(win)  # Create Tab Control

tab1 = ttk.Frame(tabControl)  # Create a tab
tabControl.add(tab1, text='PANS')  # Add the tab

tabControl.pack(expand=1, fill="both")  # Pack to make visible

# LabelFrame using tab1 as the parent
mighty = ttk.LabelFrame(tab1, text=' Generate PAN(s)')
mighty.grid(column=0, row=0, padx=8, pady=4)

# Modify adding a Label using mighty as the parent instead of win
a_label = ttk.Label(mighty, text="Input BIN, use '?' to complete the unknown number(s):")
a_label.grid(column=0, row=0, sticky='W')

# Modified Button to generate credit card numbers

def showData():
    scr.delete(0.0, 'end')
    credit_card = name_entered.get()
    def IIN_Ranges_List():

        IIN_tuple_ranges = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        # IIN_tuple_ranges = ('4','5','51', '52', '53', '54', '55', '36', '37', '38', '6011', '65', '35', '34', '37')

        IIN_tuple_ranges = sorted(IIN_tuple_ranges, reverse=True)
        return IIN_tuple_ranges

    def LuhnChk(credit_card):
        sum = 0
        numLength = len(credit_card)
        oddeven = numLength & 1
        for count in range(0, numLength):
            digit = int(credit_card[count])
            if not ((count & 1) ^ oddeven):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum = sum + digit
        return ((sum % 10) == 0)

    def IIN_Ranges(credit_card, IIN_tuple_ranges):
        for iin in IIN_tuple_ranges:
            if credit_card[0:len(iin)] == str(iin):
                return True
                break
        return False

    if credit_card.count("?") > 0 and len(credit_card) <= 16:
        possibilities = numpy.uint64(10 ** credit_card.count("?"))
        #scr.insert(0.0, "Attempting to generate PAN combinations for: " + str(credit_card))
        counter = 0

        IIN_tuple_ranges = IIN_Ranges_List()

        PANasList = list(credit_card)  # Convert the PAN number into a List

        L = []  # A list with the indexes of the ? characters as found in given PAN
        for m in re.finditer('\?', credit_card):
            L.append(m.start())

        TotalPANs = 0  # Count the number of valid generated PAN combinations
        STR_LIST = []  # A list for the generated combinations of digits
        while (counter < possibilities):
            if len(str(counter)) < credit_card.count("?") + 1:
                m = credit_card.count("?") - len(str(counter))
                STR = "0" * m + str(counter)

            else:
                STR = str(counter)

            STR_LIST = STR
            counter = counter + 1

            c = 0
            for item in L:
                c = c + 1
                PANasList[item] = STR_LIST[c - 1]

            tempPAN = "".join(PANasList)

            if LuhnChk(tempPAN) == True and IIN_Ranges(tempPAN, IIN_tuple_ranges) == True:  # Check Luhn and validate only the ones that belong to IIN Ranges
                # print("[+] Valid PAN ", tempPAN)
                #scr.insert(tk.INSERT, "[+] Valid PAN ", tempPAN)
                TotalPANs = TotalPANs + 1

        #print IIN_tuple_ranges
        "\nTotal valid PAN generated: " + str(TotalPANs)
        #scr.insert(tk.INSERT, return + "\nTotal valid PAN generated: " + str(TotalPANs))

    IIN_tuple_ranges = IIN_Ranges_List()
    IIN_Ranges_List()
    if len(sys.argv) != 2:
        if credit_card.count("?") > 0 and len(credit_card) <= 16:
            # calculate the number of combinations
            possibilities = numpy.uint64(10 ** credit_card.count("?"))
            print("Attempting to generate PAN combinations for: " + str(credit_card))
            scr.insert(tk.INSERT, "Attempting to generate PAN combinations for: " + str(credit_card))
            counter = 0

            PANasList = list(credit_card)

            L = []  # A list with the indexes of the ? characters as found in given PAN
            for m in re.finditer('\?', credit_card):
                L.append(m.start())

            # Count the number of valid generated PAN combinations
            TotalPANs = 0

            # A list for the generated combinations of digits
            STR_LIST = []
            while (counter < possibilities):
                if len(str(counter)) < credit_card.count("?") + 1:
                    m = credit_card.count("?") - len(str(counter))
                    STR = "0" * m + str(counter)

                else:
                    STR = str(counter)

                STR_LIST = STR
                counter = counter + 1

                c = 0
                for item in L:
                    c = c + 1
                    PANasList[item] = STR_LIST[c - 1]

                tempPAN = "".join(PANasList)

                # Check Luhn and validate only the ones that belong to IIN Ranges
                if LuhnChk(tempPAN) == True and IIN_Ranges(tempPAN, IIN_tuple_ranges) == True:
                    print("[+] Valid PAN ", tempPAN)
                    scr.insert(tk.INSERT, "\n Valid PAN = ", tempPAN)
                    scr.insert(tk.INSERT, tempPAN)
                    TotalPANs = TotalPANs + 1
            # print IIN_tuple_ranges
            print("Total valid PAN generated: " + str(TotalPANs))
            scr.insert(tk.INSERT, "\nTotal valid PAN generated: " + str(TotalPANs))
        else:
            if LuhnChk(credit_card):
                print("")
                scr.insert(tk.INSERT, "\n Use validate button to validate Card")
                #scr.insert(tk.INSERT, "\nYour card is Valid")
            if (LuhnChk(credit_card)):
                print("")
                #scr.insert(tk.INSERT, "\nThe last digit of the your card is {}".format(credit_card[-1]))
    #    Always make sure the 'IIN Ranges List' is Ordered, as it simplifies the IIN check
    IIN_tuple_ranges = IIN_Ranges_List()
    # print IIN_Ranges_tuple
    # Validate a PAN with Luhn
    if len(credit_card[1]) <= 16 and credit_card[1].isdigit():
        if LuhnChk(credit_card[1]):
            print("Use Validate button to validate Card")
            scr.insert(tk.INSERT, "\n Use Validate button to validate Card")

    # Generate PANs
    else:
        if len(credit_card[1]) <= 16 and re.match("^[0-9\?]*$", credit_card[1]):
            print(credit_card[1].strip(), IIN_tuple_ranges)
            scr.insert(tk.INSERT, credit_card[1].strip(), IIN_tuple_ranges)


def validate():
    scr.delete(0.0, 'end')
    credit_card = name_entered.get()

    def IIN_Ranges_List():

        IIN_tuple_ranges = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        # IIN_tuple_ranges = ('4','5','51', '52', '53', '54', '55', '36', '37', '38', '6011', '65', '35', '34', '37')

        IIN_tuple_ranges = sorted(IIN_tuple_ranges, reverse=True)
        return IIN_tuple_ranges

    def LuhnChk(credit_card):
        sum = 0
        numLength = len(credit_card)
        oddeven = numLength & 1
        for count in range(0, numLength):
            digit = int(credit_card[count])
            if not ((count & 1) ^ oddeven):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9
            sum = sum + digit
        return ((sum % 10) == 0)

    def IIN_Ranges(credit_card, IIN_tuple_ranges):
        for iin in IIN_tuple_ranges:
            if credit_card[0:len(iin)] == str(iin):
                return True
                break
        return False

    IIN_tuple_ranges = IIN_Ranges_List()
    IIN_Ranges_List()
    if len(sys.argv) != 2:
        if LuhnChk(credit_card):
            print("Your card is Valid")
            scr.insert(tk.INSERT, "\nYour card is Valid")
        if (LuhnChk(credit_card)):
            print("The last digit of the your card is {}".format(credit_card[-1]))
            scr.insert(tk.INSERT, "\nThe last digit of the your card is {}".format(credit_card[-1]))
        else:
            print("This card is not valid")
            scr.insert(tk.INSERT, "\nThis card is not valid")

    #    Always make sure the 'IIN Ranges List' is Ordered, as it simplifies the IIN check
    #IIN_tuple_ranges = IIN_Ranges_List()
    # print IIN_Ranges_tuple
    # Validate a PAN with Luhn
    # if len(credit_card[1]) <= 16 and credit_card[1].isdigit():
    #     if LuhnChk(credit_card[1]):
    #         print("[+] Valid PAN ", LuhnChk(credit_card[1]))
    #         scr.insert(tk.INSERT, "\n Valid PAN ", LuhnChk(credit_card[1]))
    #     else:
    #         print("[-] Invalid PAN ", LuhnChk(credit_card[1]))
    #         scr.insert(tk.INSERT, "\n Invalid PAN ", LuhnChk(credit_card[1]))
    #
    # # Generate PANs
    # else:
    #     if len(credit_card[1]) <= 16 and re.match("^[0-9\?]*$", credit_card[1]):
    #         print(credit_card[1].strip(), IIN_tuple_ranges)
    #         scr.insert(tk.INSERT, credit_card[1].strip(), IIN_tuple_ranges)


# Adding a Textbox Entry widget
name = tk.StringVar()
name_entered = ttk.Entry(mighty, width=80, textvariable=name)
name_entered.grid(column=0, row=1, sticky='W')  # align left/West
# Fonts

myFont = Font(family="Helvetica", size=16)
# Adding a Button
action = ttk.Button(mighty, text="Generate", command=showData)
action.grid(column=2, row=1)

action = ttk.Button(mighty, text="Validate", command=validate)
action.grid(column=1, row=1)

# Using a scrolled Text control
scrol_w = 80
scrol_h = 20
scr = scrolledtext.ScrolledText(mighty, width=scrol_w, height=scrol_h, wrap=tk.WORD, font=("Helvetica", 15))
scr.grid(column=0, row=5, sticky='WE', columnspan=3)

# create three Radiobuttons using one variable
radVar = tk.IntVar()

# Next we are selecting a non-existing index value for radVar
radVar.set(99)

# Exit GUI cleanly
def _quit():
    win.quit()
    win.destroy()
    exit()

# Creating a Menu Bar
menu_bar = Menu(win)
win.config(menu=menu_bar)

# Add menu items
file_menu = Menu(menu_bar, tearoff=0)
#file_menu.add_command(label="New")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=_quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add another Menu to the Menu Bar and an item
help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About")
menu_bar.add_cascade(label="Help", menu=help_menu)

name_entered.focus()  # Place cursor into name Entry
# ======================
# Starting GUI
# ======================
win.mainloop()
input()