import os
import pandas as pd

DEFAULT_DB_PATH = "D:\\Projects\\Food Barcode Object Detection\\Deployments\\database\\food_chain_store.csv"


class DatabaseRepository:
    def __init__(self, database_path: str = DEFAULT_DB_PATH):
        self.database_path = database_path
        self.database = self._load_database()
        
    def _load_database(self) -> pd.DataFrame:
        try:
            if not os.path.exists(self.database_path):
                raise FileNotFoundError(f"Database file not found at: {self.database_path}")
            
            df = pd.read_csv(self.database_path)
            required_columns = {"barcode", "name", "category", "weight", "price", "discount number", "total_price", "company"}
            if not required_columns.issubset(df.columns):
                raise ValueError(f"Database file is missing required columns: {required_columns - set(df.columns)}")
            
            return df
        
        except Exception as e:
            print(f"Error loading database: {e}")
            return pd.DataFrame()
    
    def search_by_barcodes(self, barcode_keys: list) -> pd.DataFrame:
        if self.database.empty:
            print("Warning: Database is empty. No search can be performed.")
            return pd.DataFrame()
        
        return self.database[self.database["barcode"].isin(barcode_keys)]
    
    
    
class BarcodeService:
    
    @staticmethod
    def format_query(barcode_numbers: str, company_name: str) -> list:
        try:
            barcode_list = [line.strip() for line in barcode_numbers.split("\n") if line.strip()]
            if not barcode_list:
                raise ValueError("No valid barcodes provided for search.")

            return [f"{barcode} - {company_name}" for barcode in barcode_list]
        
        except Exception as e:
            print(f"Error formatting barcode queries: {e}")
            return []        
    
 
def run_database_search(barcode_codes: str, database_path: str = None, company_name: str = "hyper")  -> pd.DataFrame:
    
    db_repo = DatabaseRepository(database_path or DEFAULT_DB_PATH)
    barcode_keys = BarcodeService.format_query(barcode_codes, company_name)
    
    if not barcode_keys:
        print("No valid barcode keys to search.")
        return pd.DataFrame()
    
    return db_repo.search_by_barcodes(barcode_keys)
