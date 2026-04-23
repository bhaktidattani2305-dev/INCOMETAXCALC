import streamlit as st

st.set_page_config(page_title="Income Tax Calculator FY 2025-26", layout="wide")

st.title("💰 Income Tax Calculator FY 2025-26 (AY 2026-27)")
st.write("Compare Old vs New Tax Regime")

# -------------------------
# INPUTS
# -------------------------
st.sidebar.header("📥 Enter Income Details")

assessee_type = st.sidebar.selectbox("Assessee Type", ["Individual", "Senior Citizen (60+)", "Super Senior (80+)"])

salary = st.sidebar.number_input("Salary Income", min_value=0.0, value=0.0)
house_property = st.sidebar.number_input("Income from House Property", value=0.0)
business = st.sidebar.number_input("Business/Profession Income", value=0.0)
capital_gains = st.sidebar.number_input("Capital Gains", value=0.0)
other_sources = st.sidebar.number_input("Other Income", value=0.0)

deductions_old = st.sidebar.number_input("Deductions (80C, 80D etc - Old Regime only)", value=0.0)

# -------------------------
# TOTAL INCOME
# -------------------------
gross_income = salary + house_property + business + capital_gains + other_sources

# -------------------------
# STANDARD DEDUCTION (ONLY SALARY)
# -------------------------
std_deduction_new = 75000 if salary > 0 else 0
std_deduction_old = 50000 if salary > 0 else 0

# -------------------------
# TAXABLE INCOME
# -------------------------
taxable_new = max(0, gross_income - std_deduction_new)
taxable_old = max(0, gross_income - std_deduction_old - deductions_old)

# -------------------------
# TAX CALC FUNCTIONS
# -------------------------
def calc_tax_new(income):
    tax = 0
    slabs = [
        (400000, 0),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float('inf'), 0.30)
    ]

    prev = 0
    for limit, rate in slabs:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break
    return tax

def calc_tax_old(income):
    tax = 0

    if assessee_type == "Individual":
        basic_exemption = 250000
    elif assessee_type == "Senior Citizen (60+)":
        basic_exemption = 300000
    else:
        basic_exemption = 500000

    if income <= basic_exemption:
        return 0

    if income <= 500000:
        tax += (income - basic_exemption) * 0.05
    elif income <= 1000000:
        tax += (500000 - basic_exemption) * 0.05
        tax += (income - 500000) * 0.20
    else:
        tax += (500000 - basic_exemption) * 0.05
        tax += (1000000 - 500000) * 0.20
        tax += (income - 1000000) * 0.30

    return tax

# -------------------------
# REBATE 87A
# -------------------------
def rebate_new(tax, income):
    if income <= 1200000:
        return min(tax, 60000)
    return 0

def rebate_old(tax, income):
    if income <= 500000:
        return min(tax, 12500)
    return 0

# -------------------------
# SURCHARGE
# -------------------------
def surcharge(tax, income):
    if income > 50000000:
        return tax * 0.37
    elif income > 20000000:
        return tax * 0.25
    elif income > 10000000:
        return tax * 0.15
    elif income > 5000000:
        return tax * 0.10
    return 0

# -------------------------
# FINAL TAX CALC
# -------------------------
def final_tax(income, regime):
    if regime == "new":
        tax = calc_tax_new(income)
        rebate = rebate_new(tax, income)
    else:
        tax = calc_tax_old(income)
        rebate = rebate_old(tax, income)

    tax -= rebate

    sc = surcharge(tax, income)
    tax += sc

    cess = tax * 0.04
    tax += cess

    return round(tax, 0)

def slabwise_tax_new(income):
    slabs = [
        (400000, 0, "0-4L"),
        (800000, 0.05, "4L-8L"),
        (1200000, 0.10, "8L-12L"),
        (1600000, 0.15, "12L-16L"),
        (2000000, 0.20, "16L-20L"),
        (2400000, 0.25, "20L-24L"),
        (float('inf'), 0.30, "24L+")
    ]

    prev = 0
    slab_labels = []
    slab_tax = []

    for limit, rate, label in slabs:
        if income > limit:
            taxable = limit - prev
        else:
            taxable = max(0, income - prev)

        tax = taxable * rate

        slab_labels.append(label)
        slab_tax.append(tax)

        prev = limit
        if income <= limit:
            break

    return slab_labels, slab_tax


def slabwise_tax_old(income, assessee_type):
    if assessee_type == "Individual":
        basic = 250000
    elif assessee_type == "Senior Citizen (60+)":
        basic = 300000
    else:
        basic = 500000

    slabs = [
        (basic, 0, f"0-{basic/100000}L"),
        (500000, 0.05, "Next 2.5L"),
        (1000000, 0.20, "Next 5L"),
        (float('inf'), 0.30, "Above 10L")
    ]

    prev = 0
    slab_labels = []
    slab_tax = []

    for limit, rate, label in slabs:
        if income > limit:
            taxable = limit - prev
        else:
            taxable = max(0, income - prev)

        tax = taxable * rate

        slab_labels.append(label)
        slab_tax.append(tax)

        prev = limit
        if income <= limit:
            break

    return slab_labels, slab_tax

# -------------------------
# OUTPUT
# -------------------------
st.header("📊 Tax Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 New Regime")
    st.write(f"Taxable Income: ₹{taxable_new:,.0f}")
    tax_new = final_tax(taxable_new, "new")
    st.success(f"Total Tax: ₹{tax_new:,.0f}")

with col2:
    st.subheader("🔵 Old Regime")
    st.write(f"Taxable Income: ₹{taxable_old:,.0f}")
    tax_old = final_tax(taxable_old, "old")
    st.success(f"Total Tax: ₹{tax_old:,.0f}")

import matplotlib.pyplot as plt

st.header("📊 Slab-wise Tax Distribution")

col3, col4 = st.columns(2)

with col3:
    st.subheader("🟢 New Regime Breakdown")
    labels_new, tax_new_slabs = slabwise_tax_new(taxable_new)

    fig1, ax1 = plt.subplots()
    ax1.barh(labels_new, tax_new_slabs)
    ax1.set_xlabel("Tax Amount (₹)")
    ax1.set_ylabel("Slabs")
    ax1.set_title("New Regime Slab-wise Tax")

    st.pyplot(fig1)


with col4:
    st.subheader("🔵 Old Regime Breakdown")
    labels_old, tax_old_slabs = slabwise_tax_old(taxable_old, assessee_type)

    fig2, ax2 = plt.subplots()
    ax2.barh(labels_old, tax_old_slabs)
    ax2.set_xlabel("Tax Amount (₹)")
    ax2.set_ylabel("Slabs")
    ax2.set_title("Old Regime Slab-wise Tax")

    st.pyplot(fig2)
# -------------------------
# RESULT
# -------------------------
st.header("🏆 Recommendation")

if tax_new < tax_old:
    st.success("New Regime is better for you ✅")
elif tax_old < tax_new:
    st.success("Old Regime is better for you ✅")
else:
    st.info("Both regimes result in same tax 🤝")