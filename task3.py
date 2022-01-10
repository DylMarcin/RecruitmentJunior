from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional
from requests import request

DOMAIN = "https://recruitment.developers.emako.pl"

class Connector:
    @lru_cache
    def headers(self) -> Dict[str, str]:
        # reimplement as needed
        return {
            "Authorization": None,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def append_pagination_data(self, data: dict, page:int) -> None:
        if page:
            data['pagination'] = {'index' : page}

    def request_size_error(self, method:str):
        return {"Error": f"{method} request processes a maximum of 20 elements"}

    def request(self, method: str, path: str, data: dict = {}) -> dict:
        return request(
            method, f"{DOMAIN}/{path}", json=data, headers=self.headers()
        ).json()

    def get_products(self, ids: Optional[List[int]] = None, page: int = None) -> List[dict]:
        data = {"ids": ids}
        self.append_pagination_data(data, page)
        return self.request("GET", "products", data)["result"]

    def get_all_products_summary(self, page: int = None) -> List[dict]:
        data = {"detailed": False}
        self.append_pagination_data(data, page)
        return self.request("GET", "products", data)["result"]

    def get_new_products(self, newer_than: Optional[datetime] = None, page: int = None) -> List[dict]:
        if newer_than is None:
            newer_than = datetime.now() - timedelta(days=5)
        data = {"created_at": {"start": newer_than.isoformat()}}
        self.append_pagination_data(data, page)
        return self.request("GET", "products", data)["result"]

    def add_products(self, products: List[dict]):
        if len(products) <= 20:
            return self.request("POST", "products", {"products": products})["result"]
        return self.request_size_error("POST")

    def update_stocks(self, stocks: Dict[int, list]):
        current_data = self.get_products(list(stocks))
        if len(current_data) <= 20:
            for product_entry in current_data:
                product_entry["details"]["supply"] = stocks[product_entry["id"]]
            return self.request("PUT", "products", {"products": current_data})
        return self.request_size_error("PUT")