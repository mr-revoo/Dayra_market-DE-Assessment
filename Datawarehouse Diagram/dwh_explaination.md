# Why This Star Schema Diagram Was Made

The star schema in the Gold Layer fulfills the core goal of building a modern analytics platform in Amazon Redshift using dbt. It enables precise and performant analytical reporting, real-time monitoring, and business intelligence for an e-commerce business. By unifying hourly OLTP batch extracts and near real-time Kafka streaming logs, the schema supports flexible and robust analysis of both sales transactions and user behavior.

# Dimensional Modeling Philosophy

This schema is driven by the principles of **Dimensional Modeling**—especially Kimball’s methodology—which prioritizes:

- **Analyst Simplicity:** The schema is immediately understandable. Facts contain business metrics; dimensions define the who, what, where, and when.

- **High Query Performance:** The architecture is shaped for Amazon Redshift’s strengths—minimizing joins and leveraging columnar MPP. Analysts and BI tools can produce ad-hoc reports with fast response times.

- **Business-First Design:** Modeling starts with actual business questions (sales trends, customer journeys), then chooses fact grains and conformed dimensions that answer those questions flexibly and efficiently.

- **Historical Accuracy with SCD2:** Slowly Changing Dimension Type 2 (SCD2) captures changes in dimension attributes (e.g., product name, customer city) so analyses reflect the business reality at the time of each transaction.

- **Conformed Dimensions:** Key dimensions (e.g., unified customers, products) are reused across fact tables to maintain consistency and allow "one version of the truth" in reporting.

# Fact Tables: Measuring Business Events

- **Fact Orders (Order Header Grain)**  
  Captures top-level order metrics (total amount, freight, dates).  
  Links to customers, employees, and three key dates (ordered, required, shipped).  
  Enables daily sales tracking and fulfillment analytics.

- **Fact Unified Order Line Items (Line Item Grain)**  
  Tracks every product sold within an order—combining OLTP and streaming data sources using a `data_source` flag.  
  Key for analyzing product-level performance and promotional effectiveness.

- **Fact Online Store Events (Session/User Real-Time Grain)**  
  Records user sessions, events, and order events from streaming logs.  
  Links behavior (navigation, device, geography) with transactions.  
  Essential for funnel analysis, user engagement, and real-time alerts.

*Both Fact Orders and Fact Online Store Events include FK placeholders for `website_key` and `navigation_key`, empowering future analysis of the impact of site/page design and user pathing on sales.*

# Dimension Tables: Business Context

- **Dim Unified Customers:**  
  Merges transactional customer data and online users, supports both historical and real-time analytics, and maintains history on key attributes (city, email) using SCD2. Enables full-lifecycle customer journey analysis.

- **Dim Products:**  
  Provides a unified catalog for querying product performance across all channels and sources. SCD2 for name/category/price changes ensures historical accuracy, while operational attributes (stock, reorder) update as needed. Its existence allows product rollups (brand/category), time-trend analysis, and anomaly detection in sales.

- **Dim Employees:**  
  For analyzing sales by representative or service agent; supports historical title, location, and org changes (SCD2).

- **Dim Date / Dim Time:**  
  Granular time context for consistent period-over-period reporting and time-series analysis (supports fiscal, calendar, hourly queries).

- **Dim Geography:**  
  Adds country, region, and city context for segmentation (e.g., by Middle East/North Africa).

- **Dim Device Type, Dim Website, Dim Navigation:**  
  Critical for e-commerce: track how users access the platform, which pages/designs work best, and how navigation patterns influence conversion rates.
