let
    Source = LoadRetailTable("FactOrders", {
    {"invoice_no", type text},
    {"order_date", type date},
    {"month", type date},
    {"country", type text},
    {"customer_id", type text},
    {"customer_group", type text},
    {"sales_value_gbp", Currency.Type},
    {"units", Int64.Type},
    {"eligible_lines", Int64.Type}
}),
    CleanCustomerID = Table.TransformColumns(Source, {{"customer_id", each if _ is null or Text.Trim(_) = "" then null else Text.Trim(_), type nullable text}})
in
    CleanCustomerID
