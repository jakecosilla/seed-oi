import uuid
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/seed_oi"

def seed_db():
    print(f"Connecting to database at {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("Clearing existing data...")
        # Tables to truncate in order of dependencies (child tables first)
        tables = [
            "recommendations", "scenarios", "risks", "issues", 
            "shipments", "production_runs", "work_orders", "sales_orders", 
            "purchase_orders", "inventory_balances", "customers", 
            "vendors", "materials", "products", "plants", "users", "tenants"
        ]
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE {t} CASCADE;"))

        now = datetime.now(timezone.utc)
        
        print("Seeding Tenants...")
        # We use a deterministic tenant UUID
        tenant_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
        conn.execute(text("""
            INSERT INTO tenants (id, name, created_at, updated_at) 
            VALUES (:id, 'Acme Corp', :now, :now)
        """), {"id": tenant_id, "now": now})

        print("Seeding Plants...")
        plant_north = uuid.uuid4()
        plant_south = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO plants (id, tenant_id, name, location, created_at, updated_at)
            VALUES 
            (:p1, :t, 'Northern Site', 'Chicago, IL', :now, :now),
            (:p2, :t, 'Southern Site', 'Austin, TX', :now, :now)
        """), {"p1": plant_north, "p2": plant_south, "t": tenant_id, "now": now})

        print("Seeding Vendors...")
        vendor_a = uuid.uuid4()
        vendor_b = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO vendors (id, tenant_id, code, name, reliability_score, created_at, updated_at)
            VALUES
            (:v1, :t, 'V-001', 'TechComponents Ltd.', 0.85, :now, :now),
            (:v2, :t, 'V-002', 'Global Energy Cells', 0.92, :now, :now)
        """), {"v1": vendor_a, "v2": vendor_b, "t": tenant_id, "now": now})

        print("Seeding Products and Materials...")
        prod_1 = uuid.uuid4()
        mat_1 = uuid.uuid4()
        mat_2 = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO products (id, tenant_id, sku, name, unit_of_measure, created_at, updated_at)
            VALUES (:p, :t, 'SKU-100', 'Industrial Drone X1', 'EA', :now, :now)
        """), {"p": prod_1, "t": tenant_id, "now": now})

        conn.execute(text("""
            INSERT INTO materials (id, tenant_id, code, name, unit_of_measure, lead_time_days, created_at, updated_at)
            VALUES 
            (:m1, :t, 'MAT-X-001', 'Microcontroller V2', 'EA', 14, :now, :now),
            (:m2, :t, 'MAT-Y-002', 'Lithium Ion Cell', 'EA', 30, :now, :now)
        """), {"m1": mat_1, "m2": mat_2, "t": tenant_id, "now": now})

        print("Seeding Inventory Balances...")
        conn.execute(text("""
            INSERT INTO inventory_balances (id, tenant_id, material_id, plant_id, quantity_on_hand, quantity_allocated, quantity_on_order, created_at, updated_at)
            VALUES
            (:id1, :t, :m1, :p1, 50, 200, 500, :now, :now),
            (:id2, :t, :m2, :p2, 1000, 800, 2000, :now, :now)
        """), {"id1": uuid.uuid4(), "id2": uuid.uuid4(), "t": tenant_id, "m1": mat_1, "m2": mat_2, "p1": plant_north, "p2": plant_south, "now": now})

        print("Seeding Purchase Orders, Sales Orders, and Work Orders...")
        po_1 = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO purchase_orders (id, tenant_id, vendor_id, order_number, status, expected_delivery_date, created_at, updated_at)
            VALUES (:po, :t, :v1, 'PO-5542', 'Delayed', :exp, :now, :now)
        """), {"po": po_1, "t": tenant_id, "v1": vendor_a, "exp": now + timedelta(days=12), "now": now})

        so_1 = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO sales_orders (id, tenant_id, order_number, status, requested_delivery_date, created_at, updated_at)
            VALUES (:so, :t, 'SO-992', 'At Risk', :req, :now, :now)
        """), {"so": so_1, "t": tenant_id, "req": now + timedelta(days=5), "now": now})

        wo_1 = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO work_orders (id, tenant_id, plant_id, product_id, order_number, status, planned_start_date, planned_end_date, target_quantity, created_at, updated_at)
            VALUES (:wo, :t, :p1, :prod, 'WO-1002', 'Blocked', :start, :end, 150, :now, :now)
        """), {"wo": wo_1, "t": tenant_id, "p1": plant_north, "prod": prod_1, "start": now - timedelta(days=2), "end": now + timedelta(days=2), "now": now})

        print("Seeding Storyline 1: Material Shortage...")
        # Use deterministic Issue ID so our mock API or testing can hit it directly
        issue_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
        conn.execute(text("""
            INSERT INTO issues (id, tenant_id, title, description, severity, status, detected_at, primary_entity_type, primary_entity_id, created_at, updated_at)
            VALUES (:i, :t, 'Material Shortage: Northern Site', 'Critical shortage of Microcontroller V2 affecting Work Order WO-1002.', 'Critical', 'Open', :now, 'Material', 'MAT-X-001', :now, :now)
        """), {"i": issue_id, "t": tenant_id, "now": now})

        conn.execute(text("""
            INSERT INTO risks (id, tenant_id, issue_id, risk_type, affected_entity_type, affected_entity_id, estimated_delay_days, revenue_exposure, created_at, updated_at)
            VALUES (:r, :t, :i, 'Revenue Exposure', 'SalesOrder', 'SO-992', 12, 850000.0, :now, :now)
        """), {"r": uuid.uuid4(), "t": tenant_id, "i": issue_id, "now": now})

        scen_1 = uuid.uuid4()
        scen_2 = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO scenarios (id, tenant_id, issue_id, name, description, status, net_cost_impact, delay_days_avoided, created_at, updated_at)
            VALUES 
            (:s1, :t, :i, 'Expedite Air Freight', 'Bypass sea port congestion by using air freight for critical materials.', 'Recommended', 15000.0, 10, :now, :now),
            (:s2, :t, :i, 'Reallocate from Southern Plant', 'Transfer 500 units of Material X from Southern Site inventory.', 'Alternative', 2000.0, 4, :now, :now)
        """), {"s1": scen_1, "s2": scen_2, "t": tenant_id, "i": issue_id, "now": now})

        # Convert dictionaries to JSON strings for action_details
        ad_1 = json.dumps({"Carrier": "FedEx", "Route": "SFO-NYC"})
        ad_2 = json.dumps({"Source": "Southern Site", "Qty": "500"})

        conn.execute(text("""
            INSERT INTO recommendations (id, tenant_id, scenario_id, action_type, action_details, confidence_score, rank, created_at, updated_at)
            VALUES 
            (:r1, :t, :s1, 'Expedite', :ad1, 0.95, 1, :now, :now),
            (:r2, :t, :s2, 'Reallocate', :ad2, 0.85, 2, :now, :now)
        """), {"r1": uuid.uuid4(), "r2": uuid.uuid4(), "t": tenant_id, "s1": scen_1, "s2": scen_2, "ad1": ad_1, "ad2": ad_2, "now": now})
        
        print("Seeding Storyline 2: Logistics Delay...")
        issue_2_id = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO issues (id, tenant_id, title, description, severity, status, detected_at, primary_entity_type, primary_entity_id, created_at, updated_at)
            VALUES (:i, :t, 'Logistics Delay: Port Congestion', 'Shipment of Lithium Ion Cells delayed at port.', 'Warning', 'Open', :now, 'PurchaseOrder', 'PO-8821', :now, :now)
        """), {"i": issue_2_id, "t": tenant_id, "now": now - timedelta(days=1)})

        conn.execute(text("""
            INSERT INTO risks (id, tenant_id, issue_id, risk_type, affected_entity_type, affected_entity_id, estimated_delay_days, revenue_exposure, created_at, updated_at)
            VALUES (:r, :t, :i, 'Delay', 'WorkOrder', 'WO-2041', 5, 420000.0, :now, :now)
        """), {"r": uuid.uuid4(), "t": tenant_id, "i": issue_2_id, "now": now})

        print("Seeding Storyline 3: Supplier Quality Alert...")
        issue_3_id = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO issues (id, tenant_id, title, description, severity, status, detected_at, primary_entity_type, primary_entity_id, created_at, updated_at)
            VALUES (:i, :t, 'Supplier Quality Alert: TechComponents', 'Recent batch of Microcontroller V2 failed QA metrics (High defect rate).', 'Monitor', 'Open', :now, 'Vendor', 'V-001', :now, :now)
        """), {"i": issue_3_id, "t": tenant_id, "now": now - timedelta(days=2)})

        conn.execute(text("""
            INSERT INTO risks (id, tenant_id, issue_id, risk_type, affected_entity_type, affected_entity_id, estimated_delay_days, revenue_exposure, created_at, updated_at)
            VALUES (:r, :t, :i, 'Quality Risk', 'Product', 'SKU-100', 0, 150000.0, :now, :now)
        """), {"r": uuid.uuid4(), "t": tenant_id, "i": issue_3_id, "now": now})

        print("✅ Demo data seeded successfully.")

if __name__ == "__main__":
    seed_db()
