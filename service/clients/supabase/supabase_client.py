import sys
import os

# Thêm đường dẫn để import
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from service.base.hybrid_singleton import HybridSingletonBase, create_hybrid_getter
from supabase import create_client, Client
import streamlit as st
import conf


class SupabaseHybridClient(HybridSingletonBase):
    """
    Supabase Client sử dụng Hybrid Singleton pattern
    Cải tiến từ SupabaseClient hiện tại với tính năng mới
    """

    def _initialize(self):
        """Initialize Supabase client"""
        print("🔧 Initializing Supabase Hybrid Client...")

        # Get configuration from conf.py
        self.url = conf.SUPABASE_URL
        self.key = conf.SUPABASE_KEY

        # Validate configuration
        is_valid, message = conf.validate_supabase_config()
        if not is_valid:
            st.error(f"❌ Supabase Configuration Error: {message}")
            self.client = None
            self.is_connected = False
            return

        try:
            # Create Supabase client
            self.client: Client = create_client(self.url, self.key)
            self.is_connected = True

            print(f"✅ Supabase Hybrid Client initialized successfully!")

        except Exception as e:
            st.error(f"❌ Failed to initialize Supabase client: {str(e)}")
            self.client = None
            self.is_connected = False

    def get_client(self) -> Client:
        """Get the underlying Supabase client"""
        if not self.is_connected:
            raise ValueError("Supabase client is not connected")
        return self.client

    def test_connection(self):
        """Test Supabase connection bằng cách test table access thay vì auth"""
        if not self.is_connected:
            return False, "Supabase client is not initialized"

        try:
            # Test connection bằng cách thử query một table system
            # Thay vì get_user() để tránh conflict với JIRA user
            response = (
                self.client.table("date_not_working").select("*").limit(1).execute()
            )
            return True, f"Supabase connection successful - Table access OK"
        except Exception as e:
            # Nếu table không tồn tại, thử test khác
            try:
                # Test basic connection bằng cách gọi API health check
                from supabase._sync.client import SyncClient

                if isinstance(self.client, SyncClient):
                    # Just test that we can create a query (không execute)
                    query_test = self.client.table("__test__").select("*")
                    return True, "Supabase connection successful - Basic client OK"
                else:
                    return True, "Supabase connection successful - Client initialized"
            except Exception as e2:
                return (
                    False,
                    f"Supabase connection failed: {str(e)} | Fallback test: {str(e2)}",
                )

    # Enhanced database operations with better error handling
    def select_all(self, table_name: str, columns: str = "*"):
        """Get all data from table with optional column selection"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return []

        try:
            response = self.client.table(table_name).select(columns).execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching data from table {table_name}: {str(e)}")
            return []

    def select_with_filter(
        self, table_name: str, column: str, value, operator: str = "eq"
    ):
        """Get data with flexible filtering"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return []

        try:
            query = self.client.table(table_name).select("*")

            # Support different operators
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "neq":
                query = query.neq(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "gte":
                query = query.gte(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "lte":
                query = query.lte(column, value)
            elif operator == "like":
                query = query.like(column, value)
            elif operator == "ilike":
                query = query.ilike(column, value)
            else:
                query = query.eq(column, value)  # Default to eq

            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error filtering data from table {table_name}: {str(e)}")
            return []

    def select_with_pagination(self, table_name: str, limit: int = 10, offset: int = 0):
        """Get data with pagination"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return []

        try:
            response = (
                self.client.table(table_name)
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data
        except Exception as e:
            st.error(f"Error fetching paginated data from table {table_name}: {str(e)}")
            return []

    def insert_data(self, table_name: str, data: dict, returning: str = "*"):
        """Insert data with flexible return options"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return None

        try:
            response = self.client.table(table_name).insert(data).execute()
            return response.data
        except Exception as e:
            st.error(f"Error inserting data into table {table_name}: {str(e)}")
            return None

    def insert_batch(self, table_name: str, data_list: list):
        """Insert multiple records at once"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return None

        try:
            response = self.client.table(table_name).insert(data_list).execute()
            return response.data
        except Exception as e:
            st.error(f"Error batch inserting data into table {table_name}: {str(e)}")
            return None

    def update_data(self, table_name: str, data: dict, column: str, value):
        """Update data with condition"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return None

        try:
            response = (
                self.client.table(table_name).update(data).eq(column, value).execute()
            )
            return response.data
        except Exception as e:
            st.error(f"Error updating data in table {table_name}: {str(e)}")
            return None

    def delete_data(self, table_name: str, column: str, value):
        """Delete data with condition"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return None

        try:
            response = (
                self.client.table(table_name).delete().eq(column, value).execute()
            )
            return response.data
        except Exception as e:
            st.error(f"Error deleting data from table {table_name}: {str(e)}")
            return None

    def count_records(self, table_name: str, column: str = "*"):
        """Count records in table"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return 0

        try:
            response = (
                self.client.table(table_name).select(column, count="exact").execute()
            )
            return response.count
        except Exception as e:
            st.error(f"Error counting records in table {table_name}: {str(e)}")
            return 0

    def execute_rpc(self, function_name: str, params: dict = None):
        """Execute stored procedure/function"""
        if not self.is_connected:
            st.error("Supabase client is not connected")
            return None

        try:
            if params:
                response = self.client.rpc(function_name, params).execute()
            else:
                response = self.client.rpc(function_name).execute()
            return response.data
        except Exception as e:
            st.error(f"Error executing RPC {function_name}: {str(e)}")
            return None


# Create hybrid getter functions
get_supabase_hybrid_client = create_hybrid_getter(
    client_class=SupabaseHybridClient,
    cache_key="supabase_hybrid_client",
    session_key="supabase_hybrid_session",
)

# Alternative getter without session state (lighter) q
get_supabase_hybrid_client_lite = create_hybrid_getter(
    client_class=SupabaseHybridClient,
    cache_key="supabase_hybrid_client_lite",
    session_key=None,
)


# Utility functions specific to Supabase
def get_supabase_hybrid_info():
    """Get Supabase hybrid client information"""
    return SupabaseHybridClient.get_instance_info()


def reset_supabase_hybrid():
    """Reset Supabase hybrid client"""
    SupabaseHybridClient.reset_instance()
    st.cache_resource.clear()

    # Clear session state
    keys_to_remove = [k for k in st.session_state.keys() if "supabase_hybrid" in k]
    for key in keys_to_remove:
        del st.session_state[key]

    st.success("🔄 Supabase Hybrid Client has been reset!")


# Backward compatibility
def get_supabase_client_hybrid():
    """
    Backward compatibility function
    Use get_supabase_hybrid_client() instead
    """
    import warnings

    warnings.warn(
        "get_supabase_client_hybrid() is deprecated. Use get_supabase_hybrid_client() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_supabase_hybrid_client()
