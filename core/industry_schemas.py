"""Canonical column definitions and alias pools for each industry.

Each industry schema contains:
- ``columns``: dict mapping canonical_name -> {type, aliases, description}
  * type: "identifier", "numeric", "categorical", or "date"
  * aliases: set of lowercase alternative column names found in real datasets
  * description: short human-readable purpose
- ``required_columns``: list of canonical names that must be present (at least N of them)
  for the dataset to be recognised as belonging to this industry
- ``min_required``: minimum number of required_columns that must match
"""

from __future__ import annotations

from typing import Any, Dict

IndustrySchema = Dict[str, Any]

# ---------------------------------------------------------------------------
# HR
# ---------------------------------------------------------------------------
HR_SCHEMA: IndustrySchema = {
    "industry": "HR",
    "min_required": 4,
    "required_columns": [
        "Employee_ID", "Employee_Name", "Gender", "Age",
        "Salary", "Department", "Performance_Rating", "Overtime_Hours",
    ],
    "columns": {
        # Identifiers
        "Employee_ID": {
            "type": "identifier",
            "aliases": {"employee_id", "emp_id", "staff_id", "worker_id", "id"},
            "description": "Unique employee identifier.",
        },
        "Manager_ID": {
            "type": "identifier",
            "aliases": {"manager_id", "mgr_id", "supervisor_id"},
            "description": "Manager/supervisor reference.",
        },
        # Numeric
        "Age": {
            "type": "numeric",
            "aliases": {"age", "employee_age", "umur"},
            "description": "Employee age in years.",
            "valid_range": (16, 75),
        },
        "Salary": {
            "type": "numeric",
            "aliases": {"salary", "gaji", "salary_amount", "monthly_salary", "income", "wage"},
            "description": "Monthly salary amount.",
            "valid_range": (0, 99999),
        },
        "Bonus_Amount": {
            "type": "numeric",
            "aliases": {"bonus_amount", "bonus", "incentive"},
            "description": "Bonus or incentive payout.",
        },
        "Overtime_Hours": {
            "type": "numeric",
            "aliases": {"overtime_hours", "overtime hours", "ot_hours", "ot hours", "overtime", "lembur"},
            "description": "Monthly overtime hours worked.",
            "valid_range": (0, 200),
        },
        "Tenure_Years": {
            "type": "numeric",
            "aliases": {"tenure_years", "tenure", "years_at_company", "experience"},
            "description": "Years of service.",
        },
        "Performance_Rating": {
            "type": "numeric",
            "aliases": {
                "performance_rating", "performance rating", "rating",
                "performance_score", "performance score",
            },
            "description": "Performance review score.",
            "valid_range": (1, 5),
        },
        # Categorical
        "Employee_Name": {
            "type": "categorical",
            "aliases": {"employee_name", "name", "full_name", "employee name", "full name"},
            "description": "Employee full name.",
        },
        "Gender": {
            "type": "categorical",
            "aliases": {"gender", "sex", "jenis_kelamin"},
            "description": "Employee gender.",
        },
        "Department": {
            "type": "categorical",
            "aliases": {"department", "dept", "division", "jabatan"},
            "description": "Department or division name.",
        },
        "Job_Title": {
            "type": "categorical",
            "aliases": {"job_title", "position", "role", "designation", "jawatan"},
            "description": "Job title or position.",
        },
        "Employment_Status": {
            "type": "categorical",
            "aliases": {"employment_status", "status", "emp_status"},
            "description": "Active / Resigned / Terminated.",
        },
        "Employment_Type": {
            "type": "categorical",
            "aliases": {"employment_type", "emp_type", "contract_type"},
            "description": "Full-time / Part-time / Contract.",
        },
        "Location": {
            "type": "categorical",
            "aliases": {"location", "office", "branch", "site"},
            "description": "Work location or branch.",
        },
        # Dates
        "Hire_Date": {
            "type": "date",
            "aliases": {"hire_date", "hire date", "joining_date", "start_date", "tgl_masuk"},
            "description": "Date of employment start.",
        },
        "Birth_Date": {
            "type": "date",
            "aliases": {"birth_date", "dob", "date_of_birth", "birthday"},
            "description": "Date of birth.",
        },
        "Termination_Date": {
            "type": "date",
            "aliases": {"termination_date", "end_date", "resign_date", "exit_date"},
            "description": "Employment end date.",
        },
        "Review_Date": {
            "type": "date",
            "aliases": {"review_date", "appraisal_date", "evaluation_date"},
            "description": "Performance review date.",
        },
    },
}

# ---------------------------------------------------------------------------
# Sales
# ---------------------------------------------------------------------------
SALES_SCHEMA: IndustrySchema = {
    "industry": "Sales",
    "min_required": 4,
    "required_columns": [
        "Sales_ID", "Order_ID", "Customer_ID", "Revenue",
        "Quantity_Sold", "Product_Category", "Order_Date",
    ],
    "columns": {
        # Identifiers
        "Sales_ID": {
            "type": "identifier",
            "aliases": {"sales_id", "sale_id", "transaction_id", "txn_id"},
            "description": "Unique sales transaction identifier.",
        },
        "Order_ID": {
            "type": "identifier",
            "aliases": {"order_id", "order_no", "order_number", "po_number"},
            "description": "Order reference number.",
        },
        "Customer_ID": {
            "type": "identifier",
            "aliases": {"customer_id", "cust_id", "client_id", "buyer_id"},
            "description": "Customer identifier.",
        },
        "Product_ID": {
            "type": "identifier",
            "aliases": {"product_id", "prod_id", "item_id", "sku"},
            "description": "Product or SKU identifier.",
        },
        "Sales_Rep_ID": {
            "type": "identifier",
            "aliases": {"sales_rep_id", "rep_id", "agent_id", "salesperson_id"},
            "description": "Sales representative identifier.",
        },
        # Numeric
        "Quantity_Sold": {
            "type": "numeric",
            "aliases": {"quantity_sold", "quantity", "qty", "units_sold", "qty_sold"},
            "description": "Number of units sold.",
            "valid_range": (1, 100000),
        },
        "Unit_Price": {
            "type": "numeric",
            "aliases": {"unit_price", "price", "item_price", "selling_price"},
            "description": "Price per unit.",
            "valid_range": (0, None),
        },
        "Discount_Amount": {
            "type": "numeric",
            "aliases": {"discount_amount", "discount", "discount_value"},
            "description": "Discount applied to the sale.",
        },
        "Revenue": {
            "type": "numeric",
            "aliases": {"revenue", "total_revenue", "sales_amount", "total_sales", "amount", "total_amount"},
            "description": "Total revenue from the sale.",
            "valid_range": (0, None),
        },
        "COGS": {
            "type": "numeric",
            "aliases": {"cogs", "cost_of_goods_sold", "cost_of_goods", "cost"},
            "description": "Cost of goods sold.",
        },
        "Gross_Profit": {
            "type": "numeric",
            "aliases": {"gross_profit", "profit", "margin", "gross_margin"},
            "description": "Revenue minus COGS.",
        },
        "Commission_Amount": {
            "type": "numeric",
            "aliases": {"commission_amount", "commission", "sales_commission"},
            "description": "Sales commission earned.",
        },
        "Forecast_Amount": {
            "type": "numeric",
            "aliases": {"forecast_amount", "forecast", "pipeline_value"},
            "description": "Forecasted deal value.",
        },
        # Categorical
        "Customer_Name": {
            "type": "categorical",
            "aliases": {"customer_name", "client_name", "buyer_name"},
            "description": "Customer display name.",
        },
        "Sales_Channel": {
            "type": "categorical",
            "aliases": {"sales_channel", "channel", "source_channel"},
            "description": "Online / Retail / Wholesale.",
        },
        "Region": {
            "type": "categorical",
            "aliases": {"region", "territory", "area", "zone", "market"},
            "description": "Sales region or territory.",
        },
        "Product_Category": {
            "type": "categorical",
            "aliases": {"product_category", "category", "item_category", "product_type", "product"},
            "description": "Product grouping or category.",
        },
        "Deal_Stage": {
            "type": "categorical",
            "aliases": {"deal_stage", "pipeline_stage", "opportunity_stage"},
            "description": "Pipeline deal stage.",
        },
        "Payment_Term": {
            "type": "categorical",
            "aliases": {"payment_term", "payment_terms", "terms"},
            "description": "Net-30, COD, etc.",
        },
        "Order_Status": {
            "type": "categorical",
            "aliases": {"order_status", "status", "order_state"},
            "description": "Completed / Pending / Cancelled.",
        },
        # Dates
        "Order_Date": {
            "type": "date",
            "aliases": {"order_date", "sale_date", "transaction_date", "purchase_date"},
            "description": "Date the order was placed.",
        },
        "Invoice_Date": {
            "type": "date",
            "aliases": {"invoice_date", "billing_date"},
            "description": "Invoice issue date.",
        },
        "Close_Date": {
            "type": "date",
            "aliases": {"close_date", "closed_date", "deal_close_date"},
            "description": "Deal closure date.",
        },
        "Delivery_Date": {
            "type": "date",
            "aliases": {"delivery_date", "ship_date", "dispatch_date"},
            "description": "Expected or actual delivery date.",
        },
    },
}

# ---------------------------------------------------------------------------
# Manufacturing
# ---------------------------------------------------------------------------
MANUFACTURING_SCHEMA: IndustrySchema = {
    "industry": "Manufacturing",
    "min_required": 4,
    "required_columns": [
        "Production_Order_ID", "Batch_ID", "Machine_ID",
        "Produced_Quantity", "Defect_Rate", "Cycle_Time_Minutes",
        "Production_Date",
    ],
    "columns": {
        # Identifiers
        "Production_Order_ID": {
            "type": "identifier",
            "aliases": {"production_order_id", "prod_order_id", "work_order_id", "wo_id"},
            "description": "Production or work order identifier.",
        },
        "Batch_ID": {
            "type": "identifier",
            "aliases": {"batch_id", "lot_id", "batch_no", "lot_number"},
            "description": "Production batch or lot identifier.",
        },
        "Machine_ID": {
            "type": "identifier",
            "aliases": {"machine_id", "equipment_id", "asset_id", "line_id"},
            "description": "Machine or equipment identifier.",
        },
        "Plant_ID": {
            "type": "identifier",
            "aliases": {"plant_id", "factory_id", "facility_id", "site_id"},
            "description": "Manufacturing plant identifier.",
        },
        "Material_ID": {
            "type": "identifier",
            "aliases": {"material_id", "raw_material_id", "component_id", "part_id"},
            "description": "Raw material or component identifier.",
        },
        # Numeric
        "Planned_Quantity": {
            "type": "numeric",
            "aliases": {"planned_quantity", "planned_qty", "target_quantity", "target_qty"},
            "description": "Target production quantity.",
            "valid_range": (0, None),
        },
        "Produced_Quantity": {
            "type": "numeric",
            "aliases": {"produced_quantity", "produced_qty", "actual_quantity", "output_qty", "production_count"},
            "description": "Actual units produced.",
            "valid_range": (0, None),
        },
        "Scrap_Quantity": {
            "type": "numeric",
            "aliases": {"scrap_quantity", "scrap_qty", "waste_qty", "reject_qty"},
            "description": "Units scrapped or rejected.",
            "valid_range": (0, None),
        },
        "Cycle_Time_Minutes": {
            "type": "numeric",
            "aliases": {"cycle_time_minutes", "cycle_time", "takt_time", "processing_time"},
            "description": "Production cycle time in minutes.",
            "valid_range": (0, None),
        },
        "Downtime_Minutes": {
            "type": "numeric",
            "aliases": {"downtime_minutes", "downtime", "idle_time", "stoppage_time"},
            "description": "Machine downtime in minutes.",
            "valid_range": (0, None),
        },
        "Defect_Rate": {
            "type": "numeric",
            "aliases": {"defect_rate", "defect_pct", "rejection_rate", "fail_rate"},
            "description": "Defect rate as percentage or ratio.",
            "valid_range": (0, 100),
        },
        "Yield_Percent": {
            "type": "numeric",
            "aliases": {"yield_percent", "yield_pct", "yield_rate", "yield"},
            "description": "Production yield percentage.",
            "valid_range": (0, 100),
        },
        "Unit_Cost": {
            "type": "numeric",
            "aliases": {"unit_cost", "cost_per_unit", "production_cost", "manufacturing_cost"},
            "description": "Cost per unit produced.",
            "valid_range": (0, None),
        },
        "Temperature": {
            "type": "numeric",
            "aliases": {"temperature", "temp", "machine_temp", "operating_temp"},
            "description": "Machine or process temperature.",
        },
        # Categorical
        "Product_Name": {
            "type": "categorical",
            "aliases": {"product_name", "product", "item_name"},
            "description": "Manufactured product name.",
        },
        "Product_Category": {
            "type": "categorical",
            "aliases": {"product_category", "category", "product_type", "product_group"},
            "description": "Product grouping.",
        },
        "Shift": {
            "type": "categorical",
            "aliases": {"shift", "work_shift", "shift_name", "shift_type"},
            "description": "Morning / Afternoon / Night shift.",
        },
        "Machine_Status": {
            "type": "categorical",
            "aliases": {"machine_status", "equipment_status", "status", "machine_state"},
            "description": "Running / Idle / Maintenance.",
        },
        "Defect_Type": {
            "type": "categorical",
            "aliases": {"defect_type", "defect_category", "failure_type", "issue_type"},
            "description": "Classification of defects.",
        },
        "Operator_Name": {
            "type": "categorical",
            "aliases": {"operator_name", "operator", "technician", "worker_name"},
            "description": "Machine operator name.",
        },
        "Plant_Name": {
            "type": "categorical",
            "aliases": {"plant_name", "factory_name", "facility_name", "site_name"},
            "description": "Manufacturing plant display name.",
        },
        # Dates
        "Production_Date": {
            "type": "date",
            "aliases": {"production_date", "prod_date", "manufacturing_date", "mfg_date"},
            "description": "Date of production run.",
        },
        "Start_Timestamp": {
            "type": "date",
            "aliases": {"start_timestamp", "start_time", "start_datetime", "run_start"},
            "description": "Production run start time.",
        },
        "End_Timestamp": {
            "type": "date",
            "aliases": {"end_timestamp", "end_time", "end_datetime", "run_end"},
            "description": "Production run end time.",
        },
        "Maintenance_Date": {
            "type": "date",
            "aliases": {"maintenance_date", "service_date", "last_maintenance"},
            "description": "Last maintenance or service date.",
        },
    },
}

# ---------------------------------------------------------------------------
# Logistics
# ---------------------------------------------------------------------------
LOGISTICS_SCHEMA: IndustrySchema = {
    "industry": "Logistics",
    "min_required": 4,
    "required_columns": [
        "Shipment_ID", "Tracking_Number", "Order_ID",
        "Shipment_Weight_KG", "Distance_KM", "Freight_Cost",
        "Delivery_Status", "Shipment_Date",
    ],
    "columns": {
        # Identifiers
        "Shipment_ID": {
            "type": "identifier",
            "aliases": {"shipment_id", "ship_id", "consignment_id", "awb_number"},
            "description": "Unique shipment identifier.",
        },
        "Tracking_Number": {
            "type": "identifier",
            "aliases": {"tracking_number", "tracking_no", "tracking_id", "waybill"},
            "description": "Carrier tracking number.",
        },
        "Order_ID": {
            "type": "identifier",
            "aliases": {"order_id", "order_no", "reference_id", "ref_no"},
            "description": "Linked order reference.",
        },
        "Vehicle_ID": {
            "type": "identifier",
            "aliases": {"vehicle_id", "truck_id", "fleet_id", "plate_number"},
            "description": "Vehicle or fleet identifier.",
        },
        "Driver_ID": {
            "type": "identifier",
            "aliases": {"driver_id", "courier_id", "rider_id"},
            "description": "Driver or courier identifier.",
        },
        "Warehouse_ID": {
            "type": "identifier",
            "aliases": {"warehouse_id", "wh_id", "depot_id", "hub_id"},
            "description": "Warehouse or depot identifier.",
        },
        # Numeric
        "Shipment_Weight_KG": {
            "type": "numeric",
            "aliases": {"shipment_weight_kg", "weight_kg", "weight", "gross_weight"},
            "description": "Shipment weight in kilograms.",
            "valid_range": (0, None),
        },
        "Shipment_Volume_CBM": {
            "type": "numeric",
            "aliases": {"shipment_volume_cbm", "volume_cbm", "volume", "cubic_meters"},
            "description": "Shipment volume in cubic metres.",
            "valid_range": (0, None),
        },
        "Distance_KM": {
            "type": "numeric",
            "aliases": {"distance_km", "distance", "route_distance", "mileage"},
            "description": "Delivery route distance in kilometres.",
            "valid_range": (0, None),
        },
        "Freight_Cost": {
            "type": "numeric",
            "aliases": {"freight_cost", "shipping_cost", "delivery_cost", "transport_cost"},
            "description": "Total freight/shipping cost.",
            "valid_range": (0, None),
        },
        "Delivery_Time_Hours": {
            "type": "numeric",
            "aliases": {"delivery_time_hours", "delivery_time", "transit_time", "lead_time"},
            "description": "Total delivery time in hours.",
            "valid_range": (0, None),
        },
        "Delay_Minutes": {
            "type": "numeric",
            "aliases": {"delay_minutes", "delay", "late_minutes", "delay_time"},
            "description": "Delivery delay in minutes.",
            "valid_range": (0, None),
        },
        "Packages_Count": {
            "type": "numeric",
            "aliases": {"packages_count", "package_count", "num_packages", "pieces"},
            "description": "Number of packages in shipment.",
            "valid_range": (1, None),
        },
        "Fuel_Cost": {
            "type": "numeric",
            "aliases": {"fuel_cost", "fuel_expense", "fuel_charge"},
            "description": "Fuel cost for the delivery.",
            "valid_range": (0, None),
        },
        # Categorical
        "Origin_Location": {
            "type": "categorical",
            "aliases": {"origin_location", "origin", "pickup_location", "source", "from_city"},
            "description": "Shipment origin city or address.",
        },
        "Destination_Location": {
            "type": "categorical",
            "aliases": {"destination_location", "destination", "delivery_location", "to_city"},
            "description": "Shipment destination city or address.",
        },
        "Carrier_Name": {
            "type": "categorical",
            "aliases": {"carrier_name", "carrier", "courier", "logistics_provider"},
            "description": "Shipping carrier or courier name.",
        },
        "Delivery_Status": {
            "type": "categorical",
            "aliases": {"delivery_status", "status", "shipment_status", "tracking_status"},
            "description": "Delivered / In Transit / Returned.",
        },
        "Transport_Mode": {
            "type": "categorical",
            "aliases": {"transport_mode", "mode", "shipping_mode", "transport_type"},
            "description": "Road / Air / Sea / Rail.",
        },
        "Service_Level": {
            "type": "categorical",
            "aliases": {"service_level", "service_type", "priority", "shipping_tier"},
            "description": "Express / Standard / Economy.",
        },
        "Return_Flag": {
            "type": "categorical",
            "aliases": {"return_flag", "is_return", "returned", "rma_flag"},
            "description": "Whether shipment is a return (Yes/No).",
        },
        # Dates
        "Shipment_Date": {
            "type": "date",
            "aliases": {"shipment_date", "ship_date", "dispatch_date", "sent_date"},
            "description": "Date shipment was dispatched.",
        },
        "Estimated_Delivery_Date": {
            "type": "date",
            "aliases": {"estimated_delivery_date", "eta", "expected_delivery", "edd"},
            "description": "Expected delivery date.",
        },
        "Actual_Delivery_Date": {
            "type": "date",
            "aliases": {"actual_delivery_date", "delivered_date", "received_date"},
            "description": "Actual delivery date.",
        },
        "Pickup_Timestamp": {
            "type": "date",
            "aliases": {"pickup_timestamp", "pickup_time", "pickup_date", "collection_date"},
            "description": "Pickup or collection timestamp.",
        },
        "Scan_Timestamp": {
            "type": "date",
            "aliases": {"scan_timestamp", "last_scan", "scan_time", "checkpoint_time"},
            "description": "Last tracking scan timestamp.",
        },
    },
}

# ---------------------------------------------------------------------------
# E-commerce
# ---------------------------------------------------------------------------
ECOMMERCE_SCHEMA: IndustrySchema = {
    "industry": "E-commerce",
    "min_required": 4,
    "required_columns": [
        "Order_ID", "Customer_ID", "Product_ID",
        "Quantity", "Unit_Price", "Order_Value",
        "Order_Status", "Order_Date",
    ],
    "columns": {
        # Identifiers
        "Order_ID": {
            "type": "identifier",
            "aliases": {"order_id", "order_no", "order_number", "transaction_id"},
            "description": "Unique order identifier.",
        },
        "Customer_ID": {
            "type": "identifier",
            "aliases": {"customer_id", "cust_id", "user_id", "buyer_id"},
            "description": "Customer identifier.",
        },
        "Product_ID": {
            "type": "identifier",
            "aliases": {"product_id", "prod_id", "item_id", "sku", "asin"},
            "description": "Product or SKU identifier.",
        },
        "Session_ID": {
            "type": "identifier",
            "aliases": {"session_id", "visit_id", "browsing_session"},
            "description": "User browsing session identifier.",
        },
        "Cart_ID": {
            "type": "identifier",
            "aliases": {"cart_id", "basket_id", "shopping_cart_id"},
            "description": "Shopping cart identifier.",
        },
        # Numeric
        "Quantity": {
            "type": "numeric",
            "aliases": {"quantity", "qty", "units", "items_ordered"},
            "description": "Number of items ordered.",
            "valid_range": (1, 10000),
        },
        "Unit_Price": {
            "type": "numeric",
            "aliases": {"unit_price", "price", "item_price", "selling_price"},
            "description": "Price per unit.",
            "valid_range": (0, None),
        },
        "Discount_Amount": {
            "type": "numeric",
            "aliases": {"discount_amount", "discount", "promo_discount", "voucher_amount"},
            "description": "Discount applied.",
        },
        "Tax_Amount": {
            "type": "numeric",
            "aliases": {"tax_amount", "tax", "vat", "gst", "sales_tax"},
            "description": "Tax amount charged.",
            "valid_range": (0, None),
        },
        "Shipping_Fee": {
            "type": "numeric",
            "aliases": {"shipping_fee", "shipping_cost", "delivery_fee", "freight"},
            "description": "Shipping or delivery fee.",
            "valid_range": (0, None),
        },
        "Order_Value": {
            "type": "numeric",
            "aliases": {"order_value", "total_amount", "order_total", "grand_total", "total_price"},
            "description": "Total order value.",
            "valid_range": (0, None),
        },
        "Refund_Amount": {
            "type": "numeric",
            "aliases": {"refund_amount", "refund", "return_amount", "credit_amount"},
            "description": "Refund or credit issued.",
        },
        "Inventory_On_Hand": {
            "type": "numeric",
            "aliases": {"inventory_on_hand", "stock", "stock_level", "available_qty"},
            "description": "Current inventory count.",
            "valid_range": (0, None),
        },
        # Categorical
        "Customer_Name": {
            "type": "categorical",
            "aliases": {"customer_name", "buyer_name", "user_name", "full_name"},
            "description": "Customer display name.",
        },
        "Product_Name": {
            "type": "categorical",
            "aliases": {"product_name", "item_name", "product_title", "product"},
            "description": "Product display name.",
        },
        "Product_Category": {
            "type": "categorical",
            "aliases": {"product_category", "category", "item_category", "product_type"},
            "description": "Product grouping.",
        },
        "Payment_Method": {
            "type": "categorical",
            "aliases": {"payment_method", "payment_type", "pay_method", "payment_mode"},
            "description": "Credit Card / PayPal / COD / Bank Transfer.",
        },
        "Order_Status": {
            "type": "categorical",
            "aliases": {"order_status", "status", "order_state"},
            "description": "Completed / Pending / Cancelled / Refunded.",
        },
        "Device_Type": {
            "type": "categorical",
            "aliases": {"device_type", "device", "platform", "device_category"},
            "description": "Mobile / Desktop / Tablet.",
        },
        "Traffic_Source": {
            "type": "categorical",
            "aliases": {"traffic_source", "acquisition_source", "utm_source", "referral_source"},
            "description": "Organic / Paid / Social / Direct.",
        },
        "Coupon_Code": {
            "type": "categorical",
            "aliases": {"coupon_code", "promo_code", "voucher_code", "discount_code"},
            "description": "Applied promotional coupon code.",
        },
        # Dates
        "Order_Date": {
            "type": "date",
            "aliases": {"order_date", "purchase_date", "transaction_date", "created_date"},
            "description": "Date the order was placed.",
        },
        "Payment_Date": {
            "type": "date",
            "aliases": {"payment_date", "paid_date", "settlement_date"},
            "description": "Date payment was processed.",
        },
        "Shipment_Date": {
            "type": "date",
            "aliases": {"shipment_date", "shipped_date", "dispatch_date"},
            "description": "Date order was shipped.",
        },
        "Delivery_Date": {
            "type": "date",
            "aliases": {"delivery_date", "delivered_date", "received_date"},
            "description": "Date order was delivered.",
        },
        "Return_Date": {
            "type": "date",
            "aliases": {"return_date", "refund_date", "rma_date"},
            "description": "Date a return was initiated.",
        },
        # Ratings
        "Customer_Rating": {
            "type": "numeric",
            "aliases": {"customer_rating", "rating", "review_rating", "star_rating", "score"},
            "description": "Customer satisfaction rating.",
            "valid_range": (1, 5),
        },
    },
}

# ---------------------------------------------------------------------------
# Registry for programmatic look-up
# ---------------------------------------------------------------------------
INDUSTRY_SCHEMAS: Dict[str, IndustrySchema] = {
    "HR": HR_SCHEMA,
    "Sales": SALES_SCHEMA,
    "Manufacturing": MANUFACTURING_SCHEMA,
    "Logistics": LOGISTICS_SCHEMA,
    "E-commerce": ECOMMERCE_SCHEMA,
}
