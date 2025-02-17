import pdfplumber
import os
import pandas as pd
import re

class InvoiceGroup:

    def __init__(self, g):
        self.group = g
        self.invoiceMap = {}
        self.equipmentMap = {}

    def addInvoice(self, id, ojb):
        self.invoiceMap[id] = ojb

    def addEquipment(self, id, obj):
        self.equipmentMap[id] = obj

class Invoice:
    """
    invoice_num : str
        invoice number, unique to each invoice eg. 236784258-003

    invoice_group : str
        invoice group number, non-unique 236784258 (first part of invoice_num)

    invoice_group_num : str
        second part of invoice_num (003)

    invoice_date : date
        Invoice date which differs than billing dates

    billing_start : str
        Start date of billing period (usually 28 days)

    billing_end : str
        End date of billing period (usually 28 days)

    date_out : str
        first day of rental

    subtotal : float
        rental subtotal?
    tax : float
        tax

    total : float
        total invoice amount including service, fuel, tax

    service : float
        environmental service charge amount

    fuel : float
        total fuel charge including all types

    project : str
    date_out : str
    equipment_map : dict

    """
    a = ""
    def __init__(self, n, date, start, end):
        self.invoice_num = n
        self.invoice_date = date
        self.billing_start = start
        self.billing_end = end

        # from extractions
        self.subtotal = 0
        self.tax = 0
        self.total = 0
        self.service = 0
        self.fuel = 0
        self.invoice_group = ""
        self.invoice_group_num = ""
        self.project = "SGI"
        self.equipment_map = {} #key: ID, Value: Equipment object

    def setDateout(self, v):
        self.dateout = v

    def setSubtotal(self, v):
        self.subtotal = v

    def setTax(self, v):
        self.tax = v

    def setService(self,v):
        self.service = v

    def setTotal(self, v):
        self.total = v

    def setFuel(self, v):
        self.fuel = v

    def setInvoiceGroup(self, v):
        self.invoice_group = v

    def setInvoiceGroupNum(self, v):
        self.invoice_group_num = v

    def addEquipment(self, k, v):
        self.equipmentMap[k] = v
class Equipment:
    """
    id : str
        equipment id, unique.
        Identified pattern: UR (8 char) 10599785, N70-5614,
    name : str
        full name of equipment. e.g.: SKID STEER TRACK LOADER 2800-3399#

    daily_rate : float
        daily rate

    weekly_rate : float
        weekly rate

    four_week_rate : float
        4 week (28days) rate

    amount : total
        total amout including all rental, service, fuel

    dateout : str
        first date of rental

    first_date : str
        first date of rental (same as dateout)

    last_date : str
        last date of rental, same as "billing_end" of last invoice

    invoiceMap : dict
    """
    def __init__(self, id):
        # from invoice
        self.id = id #eg. 10973459
        self.name = "" # full name eg.EXCAVATOR 35000-39999#
        self.daily_rate = 0.0
        self.weekly_rate = 0.0
        self.four_week_rate = 0.0
        self.amount = 0.00 # amount charged
        self.invoiceMap = {}
        self.dateout = ""
        self.costMap = {} # key: invoice #, val: rental cost for each invoice

        # calculated
        self.first_date = ""
        self.last_date = ""

    # eg. EXCAVATOR 19000# REDUCED TAIL SWING
    def setName(self, v):
        self.name = v

    def setRate4week(self, v):
        self.rate_4week = v

    def setDailyRate(self, v):
        self.daily_rate = v

    def setWeeklyRate(self, v):
        self.weekly_rate = v

    def setFourWeekRate(self, v):
        self.four_week_rate = v

    def setAmount(self,v):
        self.amount = v

    def addInvoice(self, k, v):
        self.invoiceMap[k] = v

    def setDateout(self, v):
        self.dateout = v

    def setFirstdate(self, v):
        self.first_date = v

    def setLastdate(self, v):
        self.last_date = v

    def getLastdate(self):
        return self.last_date

    def setCost(self, k, v):
        self.costMap[k] = v

    def addCost(self, v):
        self.amount += v

class ServiceCharge:
    """
    total : float
        total amount of charge

    tpye : str
        type of service charge
        UR:
            environmental service charge
            fuel charge
            drop off
            pick up

        Sunbelt?

    InvoiceMap : dict
        reference to invoice_data

    """
    def __init__(self):
        self.total = 0
        self.InvoiceMap = {}

    def addCharge(self, v):
        self.total += v

    def addInvoice(self, k, v):
        self.InvoiceMap[k] = v