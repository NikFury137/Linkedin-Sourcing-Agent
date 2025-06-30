"""
Supplier Database Tool
=====================

Manages supplier data storage and retrieval.
"""

import sqlite3
import json
from typing import List, Dict, Optional
from pathlib import Path
from crewai_tools import BaseTool

class SupplierDatabaseTool(BaseTool):
    """
    Tool for managing supplier database operations
    """

    name: str = "supplier_database"
    description: str = "Store and retrieve supplier information from the database"

    def __init__(self, db_path: str = "data/suppliers.db"):
        super().__init__()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the supplier database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    website TEXT,
                    country TEXT,
                    city TEXT,
                    product_categories TEXT,
                    contact_info TEXT,
                    certifications TEXT,
                    capabilities TEXT,
                    financial_info TEXT,
                    risk_assessment TEXT,
                    performance_scores TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER,
                    criteria TEXT,
                    score REAL,
                    notes TEXT,
                    evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            """)

    def _run(self, action: str, **kwargs) -> str:
        """
        Execute database operations

        Args:
            action: The action to perform ('store', 'search', 'get', 'update')
            **kwargs: Additional parameters based on action
        """
        if action == "store":
            return self._store_supplier(kwargs)
        elif action == "search":
            return self._search_suppliers(kwargs.get("query", ""))
        elif action == "get":
            return self._get_supplier(kwargs.get("supplier_id"))
        elif action == "update":
            return self._update_supplier(kwargs)
        else:
            return f"Unknown action: {action}"

    def _store_supplier(self, supplier_data: Dict) -> str:
        """Store supplier information in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO suppliers (
                        name, website, country, city, product_categories,
                        contact_info, certifications, capabilities,
                        financial_info, risk_assessment, performance_scores
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    supplier_data.get("name"),
                    supplier_data.get("website"),
                    supplier_data.get("country"),
                    supplier_data.get("city"),
                    json.dumps(supplier_data.get("product_categories", [])),
                    json.dumps(supplier_data.get("contact_info", {})),
                    json.dumps(supplier_data.get("certifications", [])),
                    json.dumps(supplier_data.get("capabilities", {})),
                    json.dumps(supplier_data.get("financial_info", {})),
                    json.dumps(supplier_data.get("risk_assessment", {})),
                    json.dumps(supplier_data.get("performance_scores", {}))
                ))
                supplier_id = cursor.lastrowid
                return f"Supplier stored successfully with ID: {supplier_id}"
        except Exception as e:
            return f"Error storing supplier: {str(e)}"

    def _search_suppliers(self, query: str) -> str:
        """Search for suppliers based on query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, website, country, product_categories
                    FROM suppliers
                    WHERE name LIKE ? OR product_categories LIKE ? OR country LIKE ?
                    ORDER BY name
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))

                results = cursor.fetchall()
                if not results:
                    return "No suppliers found matching the query"

                formatted_results = []
                for row in results:
                    formatted_results.append(f"""
ID: {row[0]}
Name: {row[1]}
Website: {row[2]}
Country: {row[3]}
Categories: {row[4]}
""")

                return "\n".join(formatted_results)
        except Exception as e:
            return f"Error searching suppliers: {str(e)}"

    def _get_supplier(self, supplier_id: int) -> str:
        """Get detailed supplier information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
                result = cursor.fetchone()

                if not result:
                    return f"Supplier with ID {supplier_id} not found"

                return f"Supplier details: {result}"
        except Exception as e:
            return f"Error retrieving supplier: {str(e)}"

    def _update_supplier(self, update_data: Dict) -> str:
        """Update supplier information"""
        try:
            supplier_id = update_data.get("id")
            if not supplier_id:
                return "Supplier ID is required for update"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build dynamic update query
                fields = []
                values = []
                for key, value in update_data.items():
                    if key != "id":
                        fields.append(f"{key} = ?")
                        if isinstance(value, (dict, list)):
                            values.append(json.dumps(value))
                        else:
                            values.append(value)

                if not fields:
                    return "No fields to update"

                query = f"UPDATE suppliers SET {', '.join(fields)} WHERE id = ?"
                values.append(supplier_id)

                cursor.execute(query, values)

                if cursor.rowcount > 0:
                    return f"Supplier {supplier_id} updated successfully"
                else:
                    return f"Supplier {supplier_id} not found"
        except Exception as e:
            return f"Error updating supplier: {str(e)}"
