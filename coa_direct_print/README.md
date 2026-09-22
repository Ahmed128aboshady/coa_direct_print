# COA Direct Print - SO / Invoice / Customer Statement (`coa_direct_print`)

## 📌 الوصف العام (Overview)
One-click direct printing (browser print dialog, no download) for Sale Orders, Customer Invoices, and Customer Statement (Partner Ledger style). Sales users can print without Accounting access.

### التفاصيل الوظيفية:

COA Direct Print
================
One click = print dialog opens immediately. No download, no extra steps.

Buttons added:
--------------
* Sale Order form:
    - Print Order      : the Quotation / Order PDF
    - Print Invoice    : all posted invoices of this SO (merged in one PDF)
    - Customer Statement : full receivable statement of the SO customer
* Invoice form (customer invoices):
    - Direct Print     : the invoice PDF
    - Customer Statement
* Partner form:
    - Customer Statement

Customer Statement (كشف حساب العميل):
-------------------------------------
Custom QWeb statement built from posted receivable journal items,
with running balance and total due. Works on Community & Enterprise.

Permissions:
------------
Access is validated on the source record (SO / Invoice / Partner).
Rendering then runs with elevated rights limited to that record's
data only - Sales users can print invoices & statements without
being granted Accounting access.

Printing technique:
-------------------
The PDF is fetched as a blob and loaded into a hidden iframe, then
the browser print dialog is triggered (same technique as print.js -
reliable on Chrome/Edge). A visible preview + manual Print button
are always available as fallback.

Developed by Community of Accountants (COA)
WhatsApp: +20 101 390 7174
    

---

## 🛠️ معلومات الموديول (Module Metadata)
- **الاسم الفني (Technical Name):** `coa_direct_print`
- **التصنيف (Category):** `Sales`
- **الإصدار (Version):** `18.0.1.0.0`
- **الاعتماديات (Dependencies):** `sale`, `account`

---

## 📦 النماذج البرمجية (Models & Backend)
- **الملف:** `models\account_move.py`
  - **النماذج المعدلة (`_inherit`):** `account.move`
- **الملف:** `models\account_payment.py`
  - **النماذج المعدلة (`_inherit`):** `account.payment`
- **الملف:** `models\res_partner.py`
  - **النماذج المعدلة (`_inherit`):** `res.partner`
- **الملف:** `models\sale_order.py`
  - **النماذج المعدلة (`_inherit`):** `sale.order`

---

## 🖥️ الواجهات والتقارير (Views & Reports)
- **ملفات الواجهات (`Views`):** `report\partner_statement_report.xml`, `report\partner_statement_templates.xml`, `report\payment_receipt_report.xml`, `report\payment_receipt_templates.xml`, `views\account_move_views.xml`, `views\account_payment_views.xml`, `views\res_partner_views.xml`, `views\sale_order_views.xml`
- **ملفات التقارير (`Reports`):** `report\partner_statement_report.xml`, `report\payment_receipt_report.xml`

---

## 🚀 كيفية الاستخدام والتثبيت (Installation & Usage)
1. قُم بإضافة مجلد الموديول إلى مسار `addons_path` الخاص بالسيرفر.
2. قُم بتحديث قائمة الموديولات في أودو (Update Apps List).
3. البحث عن `COA Direct Print - SO / Invoice / Customer Statement` أو `coa_direct_print` والضغط على **تثبيت (Install)**.
